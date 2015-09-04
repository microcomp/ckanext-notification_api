import urllib2
import json
import logging

import ckan.model as model
import ckan.logic as logic
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as df
import ckan.plugins as p
from pylons import config, request, response
from ckan.common import _, c
import ckan.plugins.toolkit as toolkit

from db import notification_table, NotificationApi

_check_access = logic.check_access

def db_operation_decorator(fun):
    def func_wrapper(*args, **kwargs):
        create_notification_table()
        fun(*args, **kwargs)
    return func_wrapper

def create_notification_table():
    if not notification_table.exists():
        notification_table.create()

@db_operation_decorator
def get_dataset_followers(dataset_id):
    search = {'dataset_id': dataset_id, 'status':'active'}
    results = NotificationApi.get(**search)
    res = []
    for entity in results:
        res.append({'address' : entity.ip_address, 'user' : entity.user_id})
    return res

@db_operation_decorator
def new_notification(context, data_dict):
    user_id = data_dict['user_id']
    dataset_id = data_dict['dataset_id']
    ip_address = data_dict['ip_address']
    notification = NotificationApi(dataset_id, user_id, ip_address)
    notification.save()
    return True
 
@db_operation_decorator
def remove_notification(context, data_dict):
    info = NotificationApi.get(**data_dict)
    info[0].status = 'inactive'
    info[0].save()
    return {"status":"success"}
 
@db_operation_decorator
def reactivate_notification(context, data_dict):
    info = NotificationApi.get(**data_dict)
    info[0].status = 'active'
    info[0].save()
    return {"status":"success"} 

def valid_dataset_id(dataset_id):
    dataset =  model.Session.query(model.Package).filter(model.Package.id == dataset_id).first()
    return dataset != None

def valid_resource_id(resource_id):
    dataset =  model.Session.query(model.Resource).filter(model.Resource.id == resource_id).first()
    return dataset != None

@db_operation_decorator
def in_db(datadict):
    contains = NotificationApi.get(**datadict)
    logging.warning(contains)
    return len(contains) >= 1

@logic.side_effect_free
def subscribe(context, data_dict):
    '''Subscribe for notifications. Parameters: rid (valid dataset/resource id), url'''
    
    if context['auth_user_obj'] == None:
        raise logic.NotAuthorized

    try:
        rid = data_dict["rid"]
    except KeyError:
        ed = {'message': 'Missing rid or not valid.'}
        raise logic.ValidationError(ed)

    try:
        adr =data_dict["url"]
    except KeyError:
        ed = {'message': 'Missing url or not valid.'}
        raise logic.ValidationError(ed)

    valid_dataset = valid_dataset_id(rid)
    valid_resource = valid_resource_id(rid)
    if(valid_dataset == False and valid_resource == False):
        ed = {'message': 'rid is not valid.'}
        raise logic.ValidationError(ed)


    data_dict2 = {"dataset_id": rid, "ip_address":adr, "user_id":context['auth_user_obj'].id}
    
    __in_db = in_db(data_dict2)

    if __in_db:
        resp = {"info": "reactivated/already exists in database"}
        reactivate_notification(context, data_dict2)
    else:
        new_notification(context, data_dict2)
        resp = {"result": "subscribed", "ip":c.remote_addr}
    
    return resp

@toolkit.side_effect_free
def unsubscribe(context, data_dict):
    ''' Unsubscribe API'''
    if context['auth_user_obj'] == None:
        raise logic.NotAuthorized
    try:
        rid = data_dict["rid"]
    except KeyError:
        ed = {'message': 'Missing rid or not valid.'}
        raise logic.ValidationError(ed)

    try:
        adr =data_dict["url"]
    except KeyError:
        ed = {'message': 'Missing url or not valid.'}
        raise logic.ValidationError(ed)
    valid_dataset = valid_dataset_id(rid)
    valid_resource = valid_resource_id(rid)
    if(valid_dataset == False and valid_resource == False):
        ed = {'message': 'rid is not valid.'}
        raise logic.ValidationError(ed)

    data_dict2 = {"dataset_id": rid, "ip":adr, "user_id":context['auth_user_obj'].id}
    if in_db(data_dict2):
        remove_notification(context, data_dict2)
        resp = {"info": "unsubscribed" }
    else:
        ed = {'message': 'Rid and url not in database'}
        raise logic.ValidationError(ed)
    
    return resp

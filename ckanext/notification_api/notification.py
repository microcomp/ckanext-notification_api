import urllib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
import datetime
import ckan.model as model
import ckan.logic as logic
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as df
import ckan.plugins as p
from pylons import config, request, response
from ckan.common import _, c
import ckan.plugins.toolkit as toolkit
import urllib2
import logging
import ckan.logic
import __builtin__

import db
import json
_check_access = logic.check_access


def create_notificatio_api(context):
    if db.notification_api_table is None:
        db.init_db(context['model'])
@ckan.logic.side_effect_free
def new_notification(context, data_dict):
    create_notificatio_api(context)
    info = db.NotificationAPI()
    info.user_id = data_dict['user_id']
    info.dataset_id = data_dict['dataset_id']
    info.ip = data_dict['ip']

    info.save()
    session = context['session']
    session.add(info)
    session.commit()
    return {"status":"success"} 
@ckan.logic.side_effect_free
def remove_notification(context, data_dict):
    create_notificatio_api(context)
    info = db.NotificationAPI.get(**data_dict)
    info[0].status = 'inactive'
    info[0].save()
    session = context['session']
    #session.add(info)
    session.commit()
    return {"status":"success"} 
@ckan.logic.side_effect_free
def reactivate_notification(context, data_dict):
    create_notificatio_api(context)
    info = db.NotificationAPI.get(**data_dict)
    info[0].status = 'active'
    info[0].save()
    session = context['session']
    #session.add(info)
    session.commit()
    return {"status":"success"} 

def valid_dataset_id(dataset_id):
    dataset =  model.Session.query(model.Package).filter(model.Package.id == dataset_id).first()
    return dataset != None
def valid_resource_id(resource_id):
    dataset =  model.Session.query(model.Resource).filter(model.Resource.id == resource_id).first()
    return dataset != None
def valid_apikey(API_key):
    return model.Session.query(model.User).filter(model.User.apikey == API_key).first() != None
def user_id(API_key):
    return model.Session.query(model.User).filter(model.User.apikey == API_key).first().id
def in_db(datadict, context):
    create_notificatio_api(context)
    contains = db.NotificationAPI.get(**datadict)
    logging.warning(contains)
    return len(contains) >= 1

@toolkit.side_effect_free
def sign_up(context, data_dict):

    '''Sign up for notifications. Parameters: rid (valid dataset/resource id), url'''
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
    
    __in_db = in_db(data_dict2, context)

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
    #apikey =  self._get_apikey() #"11148c41-e328-492d-82a2-8af393063c0e" #
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
    if in_db(data_dict2,context):
        remove_notification(context, data_dict2)
        resp = {"info": "unsubscribed" }
    else:
        ed = {'message': 'Rid and url not in database'}
        raise logic.ValidationError(ed)
    
    return resp
class NotificationController(base.BaseController):
    pass

def send_notification(dataset_id, status):
    data_dict = {'dataset_id': dataset_id, 'status':'active'}
    context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
    create_notificatio_api(context)
    ##try:
    if db.notification_api_table.exists():
        ips = db.NotificationAPI.get(**data_dict)
        logging.warning("/////starting...///////")
        #logging.warning(ips)
        resp = json.dumps({"help": "notification", "result": dataset_id+" "+status,  }, encoding='utf8')
        for i in ips:
            #i.ip
            path = i.ip+"?dataset_id="+i.dataset_id+"&status="+status
            try:
                response = urllib2.urlopen(path)
                logging.warning("/////cccc///////")
                html = response.read()
                logging.warning(html)
                logging.warning(path)
            except ValueError:
                logging.warning("wrong url")

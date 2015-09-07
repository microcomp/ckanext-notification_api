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
log = logging.getLogger(__name__)

def db_operation_decorator(fun):
    def func_wrapper(*args, **kwargs):
        create_notification_table()
        return fun(*args, **kwargs)
    return func_wrapper

def create_notification_table():
    if not notification_table.exists():
        notification_table.create()

@db_operation_decorator
def get_resource_followers(entity_id):
    search = {'entity_id': entity_id, 'status':'active'}
    results = NotificationApi.get(**search)
    res = []
    for entity in results:
        res.append({'address' : entity.url, 'user' : entity.user_id})
    return res

@db_operation_decorator
def new_notification(context, data_dict):
    user_id = data_dict['user_id']
    entity_id = data_dict['entity_id']
    url = data_dict['url']
    notification = NotificationApi(entity_id, user_id, url)
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

def valid_resource_id(resource_id):
    dataset =  model.Session.query(model.Resource).filter(model.Resource.id == resource_id).first()
    return dataset != None

@db_operation_decorator
def in_db(datadict):
    contains = NotificationApi.get(**datadict)
    return len(contains) > 0

@logic.side_effect_free
def notification_subscribe(context, data_dict):
    '''Subscribe for notifications. 
    :param entity_id: id of the certain entity
    :type entity_id: string
    :param url: url address to the endpoint to be notified
    :type url: string'''
    
    _check_access('notification_subscribe', context, data_dict)

    try:
        entity_id = data_dict["entity_id"]
    except KeyError:
        raise logic.ValidationError('Missing attribute entity_id!')

    try:
        adr =data_dict["url"]
    except KeyError:
        raise logic.ValidationError('Missing attribute url!')

    valid_resource = valid_resource_id(entity_id)
    if not valid_resource:
        raise logic.ValidationError('entity_id is not valid!')

    data_dict2 = {"entity_id": entity_id, "url":adr, "user_id":context['auth_user_obj'].id}    
    existing_entry = in_db(data_dict2)

    if existing_entry:
        reactivate_notification(context, data_dict2)
        return "reactivated/already exists in database"
    else:
        new_notification(context, data_dict2)
        return "subscribed"

@toolkit.side_effect_free
def notification_unsubscribe(context, data_dict):
    ''' Unsubscribe API    
    :param entity_id: id of the certain entity
    :type entity_id: string
    :param url: url address to the endpoint
    :type url: string'''
    
    try:
        entity_id = data_dict["entity_id"]
    except KeyError:
        raise logic.ValidationError('Missing attribute entity_id!')
    
    try:
        adr = data_dict["url"]
    except KeyError:
        raise logic.ValidationError('Missing attribute url!')
    
    _check_access('notification_unsubscribe', context, data_dict)
    
    valid_resource = valid_resource_id(entity_id)
    if not valid_resource:
        raise logic.ValidationError('entity_id is not valid!')

    data_dict2 = {"entity_id" : entity_id, "url" : adr, "user_id" : context['auth_user_obj'].id}
    if in_db(data_dict2):
        remove_notification(context, data_dict2)
        return "unsubscribed"
    else:
        raise logic.ValidationError('entity_id and url not in database!')
    
def auth_notification_subscribe(context, data_dict):
    if context['auth_user_obj'] == None:
        return {'success': False,
                'msg': _('Not authorized to subscribe notifications!')}
    return {'success' : True}

def auth_notification_unsubscribe(context, data_dict):
    if context['auth_user_obj'] == None:
        return {'success': False,
                'msg': _('Not authorized to unsubscribe notifications!')}
    entity_id = data_dict["entity_id"]
    url = data_dict["url"]
    search = {'entity_id' : entity_id, 'url' : url}
    result = NotificationApi.get(**search)
    if result:
        if result[0].user_id != context['auth_user_obj'].id:
            return {'success': False,
                    'msg': _('Not authorized to unsubscribe notifications!')}
        return {'success' : True}
    else:
        return {'success' : False,
                'msg' : _('There is no url %s registered for entity %s'.format(url ,entity_id))}
            
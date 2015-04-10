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

APIKEY_HEADER_NAME_KEY = 'apikey_header_name'
APIKEY_HEADER_NAME_DEFAULT = 'X-CKAN-API-Key'
ERRORS = {0: 'subscribed', 404: "dataset not found", 111: "invalid apikey", 222:"already in the database"}

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


class NotificationController(base.BaseController):
    def _get_apikey(self):
        apikey_header_name = config.get(APIKEY_HEADER_NAME_KEY,
                                        APIKEY_HEADER_NAME_DEFAULT)
        apikey = request.headers.get(apikey_header_name, '')
        if not apikey:
            apikey = request.environ.get(apikey_header_name, '')
        if not apikey:
            # For misunderstanding old documentation (now fixed).
            apikey = request.environ.get('HTTP_AUTHORIZATION', '')
        if not apikey:
            apikey = request.environ.get('Authorization', '')
            # Forget HTTP Auth credentials (they have spaces).
            if ' ' in apikey:
                apikey = ''
        if not apikey:
            return None
        self.log.debug("Received API Key: %s" % apikey)
        apikey = unicode(apikey)
        return apikey

    def sign_up(self):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
        logging.warning("IP adress or logged user")
        logging.warning(c.author)
        apikey =  self._get_apikey() #"11148c41-e328-492d-82a2-8af393063c0e" #
        rid = base.request.params.get("rid","")
        adr = base.request.params.get("url","")
        logging.warning("apikey:")
        logging.warning(adr)
        if  (valid_dataset_id(rid) or valid_resource_id(rid)) and apikey != None:
            data_dict = {"dataset_id": rid, "ip":adr, "user_id":user_id(apikey)}
            logging.warning("data_dict:")
            logging.warning(data_dict)
            logging.warning(in_db(data_dict, context))
            if in_db(data_dict,context):
                resp = json.dumps({"help": "response","sucess":False, "result": "222 already in the database", }, encoding='utf8')
                reactivate_notification(context, data_dict)
            else:
                new_notification(context, data_dict)
                resp = json.dumps({"help": "response","sucess":True, "result": "subscribed", "ip":c.remote_addr, }, encoding='utf8')
        else:
            if apikey!= None: 
                resp = json.dumps({"help": "response","sucess":False, "result": "404 dataset not found", "ip":c.remote_addr, }, encoding='utf8')
            else:
                resp = json.dumps({"help": "response","sucess":False, "result": "111 invalid apikey", "ip":c.remote_addr, }, encoding='utf8')
        return resp

    def unsubscribe(self):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
        apikey =  self._get_apikey() #"11148c41-e328-492d-82a2-8af393063c0e" #
        rid = base.request.params.get("rid","")
        adr = base.request.params.get("url","")
        
        if  (valid_dataset_id(rid) or valid_resource_id(rid)) and valid_apikey(apikey):
            data_dict = {"dataset_id": rid, "ip":adr, "user_id":user_id(apikey)}
            logging.warning("data_dict:")
            logging.warning(data_dict)
            logging.warning(in_db(data_dict, context))
            data_dict2 = {"dataset_id": rid, "ip":adr}
            if in_db(data_dict2,context):
                remove_notification(context, data_dict2)
                resp = json.dumps({"help": "response","sucess":True, "result": "0 unsubscribed", }, encoding='utf8')
            else:
                
                resp = json.dumps({"help": "response","sucess":False, "result": "10", "ip":c.remote_addr, }, encoding='utf8')
        else:
            if apikey!= None: 
                resp = json.dumps({"help": "response","sucess":False, "result": "404 dataset not found", "ip":c.remote_addr, }, encoding='utf8')
            else:
                resp = json.dumps({"help": "response","sucess":False, "result": "111 invalid apikey", "ip":c.remote_addr, }, encoding='utf8')
        return resp
        
    def kiirat(self):
        url = send_notification("ac8a662d-7e57-4fd1-ade4-bb757fbea53f", "test")
        return base.render('kiirat.html')

def send_notification(dataset_id, status):
    data_dict = {'dataset_id': dataset_id, 'status':'active'}
    context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
    create_notificatio_api(context)
    ips = db.NotificationAPI.get(**data_dict)
    logging.warning("/////starting...///////")
    #logging.warning(ips)
    resp = json.dumps({"help": "notification", "result": dataset_id+" "+status,  }, encoding='utf8')
    for i in ips:
        #i.ip
        path = i.ip+"?dataset_id="+i.dataset_id+"&status="+status
        response = urllib2.urlopen(path)
        logging.warning("/////cccc///////")
        html = response.read()
        logging.warning(html)
        logging.warning(path)
        #return path
        #done...
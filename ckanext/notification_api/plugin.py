import logging
import json
import uuid

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.model as model
from ckan.model.domain_object import DomainObjectOperation
from ckan.lib.celery_app import celery
from pylons import config

from ckanext.notification_api import logic

log = logging.getLogger(__name__)

class NotificationApiPlugin(plugins.SingletonPlugin):

    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IDomainObjectModification, inherit=True)

    def get_actions(self):
        return {'notification_subscribe':logic.notification_subscribe,
                'notification_unsubscribe': logic.notification_unsubscribe}
    
    def get_auth_functions(self):
        return {'notification_subscribe' : logic.auth_notification_subscribe,
                'notification_unsubscribe' : logic.auth_notification_unsubscribe}

    def configure(self, config):
        self.site_url = config.get('ckan.site_url', 'unknown')

    def notify(self, entity, operation=None):
        if isinstance(entity, model.Resource):
            if not operation:
                return
            elif operation == DomainObjectOperation.changed:
                log.info('Resource edited: %s', entity.id)
                self._create_task(entity.id, 'updated')
            elif operation == DomainObjectOperation.deleted:
                log.info('Resource deleted: %s', entity.id)
                self._create_task(entity.id, 'deleted')

    def _create_task(self, entity_id, status):
        receivers = logic.get_resource_followers(entity_id)
        log.info('notif receivers: %s', receivers)
        celery.send_task("notification_api.send", args=[receivers, self.site_url, entity_id, status], task_id=str(uuid.uuid4()))
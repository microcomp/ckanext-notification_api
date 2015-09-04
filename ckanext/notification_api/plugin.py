import logging
import json
import uuid

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.model as model
from ckan.model.domain_object import DomainObjectOperation
from ckan.lib.celery_app import celery
from pylons import config

import notification

log = logging.getLogger(__name__)

class NotificationApiPlugin(plugins.SingletonPlugin):

    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IDomainObjectModification, inherit=True)

    def get_actions(self):
        return {'notification_subscribe':notification.subscribe,
                'notification_unsubscribe': notification.unsubscribe}

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
        receivers = notification.get_dataset_followers(entity_id)
        celery.send_task("notification_api.send", args=[receivers, self.site_url, entity_id, status], task_id=str(uuid.uuid4()))
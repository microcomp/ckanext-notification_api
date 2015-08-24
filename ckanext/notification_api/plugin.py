import ckan.plugins as plugins
import notification
import ckan.plugins.toolkit as toolkit
import ckan.model as model
from ckan.plugins import IMapper, IDomainObjectModification

import logging

from ckan.model.extension import ObserverNotifier
from ckan.model.domain_object import DomainObjectOperation

class NotificationApiPlugin(plugins.SingletonPlugin):

    plugins.implements(plugins.interfaces.IActions)
    plugins.implements(plugins.ITemplateHelpers, inherit=False)
    plugins.implements(plugins.IDomainObjectModification, inherit=True)

    def get_helpers(self):
        return {'send_notification': notification.send_notification}

    def get_actions(self):
        return {'notification_subscribe':notification.sign_up,
                'notification_unsubscribe': notification.unsubscribe}
    def notify(self, entity, operation=None):
        context = {'model': model, 'ignore_auth': True}
        
        if isinstance(entity, model.Resource):
            if not operation:
                return
            elif operation == DomainObjectOperation.changed:
                logging.warning('\n\n\n\n\n\n')
                logging.warning(entity.id)
                logging.warning('\n\n\n\n\n\n')
                notification.send_notification(entity.id, 'updated')
            elif operation == DomainObjectOperation.deleted:
                logging.warning(entity)
                notification.send_notification(entity.id, 'deleted')

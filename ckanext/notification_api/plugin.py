import ckan.plugins as plugins
import notification
import ckan.plugins.toolkit as toolkit
import ckan.model as model
from ckan.plugins import IMapper, IDomainObjectModification

import logging

from ckan.model.extension import ObserverNotifier
from ckan.model.domain_object import DomainObjectOperation

class NotificationApiPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers, inherit=False)
    plugins.implements(plugins.IDomainObjectModification, inherit=True)
    def before_map(self, map):
        map.connect('sign_up','/custom_api/notification/subscribe', action='sign_up', controller='ckanext.notification_api.notification:NotificationController')
        map.connect('unsubscribe','/custom_api/notification/unsubscribe', action='unsubscribe', controller='ckanext.notification_api.notification:NotificationController')
        
        return map
    def get_helpers(self):
        return {'send_notification': notification.send_notification}

    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')

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

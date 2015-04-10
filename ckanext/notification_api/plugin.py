import ckan.plugins as plugins
import notification
import ckan.plugins.toolkit as toolkit

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
        context = {'model': model, 'ignore_auth': True, 'defer_commit': True}
        if isinstance(entity, model.Resource):
            if not operation:
                return
            elif operation == DomainObjectOperation.changed:
                notification.send_notification(entity, 'updated')
            elif operation == DomainObjectOperation.deleted:
                notification.send_notification(entity, 'deleted')

import ckan.plugins as plugins
import notification
import ckan.plugins.toolkit as toolkit

class NotificationApiPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers, inherit=False)
    def before_map(self, map):
        map.connect('sign_up','/custom_api/notification/sign_up', action='sign_up', controller='ckanext.notification_api.notification:NotificationController')
        map.connect('unsubscribe','/custom_api/notification/unsubscribe', action='unsubscribe', controller='ckanext.notification_api.notification:NotificationController')
        map.connect('kiirat','/kiirat', action='kiirat', controller='ckanext.notification_api.notification:NotificationController')
        return map
    def get_helpers(self):
        return {'send_notification': notification.send_notification}

    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
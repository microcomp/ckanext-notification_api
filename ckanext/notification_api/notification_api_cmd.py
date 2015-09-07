import sys
import logging

from ckan.lib.cli import CkanCommand

log = logging.getLogger('ckanext)
log.setLevel(logging.DEBUG)


class NotificationCmd(CkanCommand):
    """Init required vocabs
        Usage:
        edem-cmd <cmd>
        - deletes created db table
    """
    
    summary = __doc__.split('\n')[0]
    usage = __doc__
    #max_args = 3
    #min_args = 0
    
    def __init__(self, name):
        super(NotificationCmd, self).__init__(name)
    def command(self):
        self._load_config()
        
        from pylons import config
        from db import notification_table, NotificationApi
        from tasks import send_notification
        
        site_url = config.get('ckan.site_url', 'unknown')
              
        if len(self.args) == 0:
            self.parser.print_usage()
            sys.exit(1)
        cmd = self.args[0]
        if cmd == 'test_notification':
            log.info('sending testing notifications to all subscribers')
            if notification_table.exists():
                search = {'status' : 'active'}
                results = NotificationApi.get(**search)
                res = []
                for entity in results:
                    res.append({'address' : entity.ip_address, 'user' : entity.user_id })
                    send_notification(res, site_url, entity.dataset_id, 'changed')
            else:
                log.info("table doesnt exist")
                
        if cmd == 'uninstall':
            log.info('Starting DB uninstall')
            if notification_table.exists():
                log.info('dropping table notification_api')
                notification_table.drop()
                log.info('table notification_api successfully dropped')
            
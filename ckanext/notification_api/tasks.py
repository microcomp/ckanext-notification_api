import logging
import os
import json
import requests

import ckan.plugins.toolkit as toolkit
from ckan.lib.celery_app import celery

log = logging.getLogger(__name__)

@celery.task(name = "notification_api.send")
def send_notification(receivers, site_url, entity_id, status):
    log.info('Firing webhooks for {0}'.format(entity_id))
    for receiver in receivers:
        payload = {
            'entity': 'dataset',
            'address': receiver['address'],
            'ckan': site_url,
            'topic': entity_id,
            'user_ref': receiver['user'],
            'status' : status
        }
        log.info('post request to %s', receiver['address'])
        try:
            requests.post(receiver['address'], headers={
                    'Content-Type': 'application/json'
                },
                data=json.dumps(payload),
                timeout=5
            )
            log.info('post request sent')
        except requests.exceptions.ConnectionError as e:
            log.info('Connection failed to url %s', receiver['address'])
        
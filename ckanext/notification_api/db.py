import datetime
import uuid
import logging

import ckan.model as model
from ckan.model import domain_object
from ckan.model.meta import metadata, Session, mapper
from sqlalchemy import types, Column, Table, ForeignKey, func, CheckConstraint
from pylons import session

log = logging.getLogger(__name__)

def make_uuid():
    return unicode(uuid.uuid4())

class NotificationApi(domain_object.DomainObject):
    def __init__(self, dataset_id, user_id, ip_address, status=None):
        assert dataset_id
        assert user_id
        assert ip_address
        self.dataset_id = dataset_id
        self.user_id = user_id
        self.ip_address = ip_address
        if status:
            self.status = status

    @classmethod
    def get(cls, **kw):
        '''Finds a single entity in the register.'''
        query = Session.query(cls).autoflush(False)
        return query.filter_by(**kw).all()

notification_table = Table('notification_api', metadata,
        Column('id', types.UnicodeText, primary_key=True, default=make_uuid),
        Column('dataset_id', types.UnicodeText, default=u'', nullable=False),
        Column('user_id', types.UnicodeText, default=u'', nullable=False),
        Column('ip_address', types.UnicodeText, default=u'', nullable=False),
        Column('status', types.UnicodeText, default=u'active', nullable=False)
    )

mapper(NotificationApi, notification_table)
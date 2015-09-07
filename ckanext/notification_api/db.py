import uuid
import logging

from ckan.model import domain_object
from ckan.model.meta import metadata, Session, mapper
from sqlalchemy import types, Column, Table, UniqueConstraint

log = logging.getLogger(__name__)

def make_uuid():
    return unicode(uuid.uuid4())

class NotificationApi(domain_object.DomainObject):
    def __init__(self, entity_id, user_id, url, status=None):
        assert entity_id
        assert user_id
        assert url
        self.entity_id = entity_id
        self.user_id = user_id
        self.url = url
        if status:
            self.status = status

    @classmethod
    def get(cls, **kw):
        '''Finds a single entity in the register.'''
        query = Session.query(cls).autoflush(False)
        return query.filter_by(**kw).all()

notification_table = Table('notification_api', metadata,
        Column('id', types.UnicodeText, primary_key=True, default=make_uuid),
        Column('entity_id', types.UnicodeText, default=u'', nullable=False),
        Column('user_id', types.UnicodeText, default=u'', nullable=False),
        Column('url', types.UnicodeText, default=u'', nullable=False),
        Column('status', types.UnicodeText, default=u'active', nullable=False),
        UniqueConstraint('entity_id', 'url', name='uix_1')
    )

mapper(NotificationApi, notification_table)
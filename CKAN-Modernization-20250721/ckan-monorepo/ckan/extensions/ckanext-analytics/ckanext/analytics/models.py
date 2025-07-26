import uuid
import datetime
from sqlalchemy import Column, String, DateTime, Text, Boolean, Table, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from ckan.model import meta, Session
from ckan.model.domain_object import DomainObject
from datetime import timedelta


# Define table using CKAN's metadata
analytics_events_table = Table(
    'analytics_events', meta.metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column('event_type', String(50), nullable=False, index=True),
    Column('dataset_id', String(100), nullable=True, index=True),
    Column('resource_id', String(100), nullable=True, index=True),
    Column('user_id', String(100), nullable=True),
    Column('session_hash', String(64), nullable=True),
    Column('event_data', JSONB, nullable=True),
    Column('user_agent', Text, nullable=True),
    Column('referrer', Text, nullable=True),
    Column('do_not_track', Boolean, default=False),
    Column('timestamp', DateTime, default=datetime.datetime.utcnow, nullable=False, index=True),
    extend_existing=True
)


class AnalyticsEvent(DomainObject):
    """
    Analytics event tracking for CKAN usage patterns.
    
    Tracks user interactions with datasets, resources, and search
    while respecting privacy (IP addresses are hashed).
    """
    
    def __repr__(self):
        return f'<AnalyticsEvent {self.event_type} {self.timestamp}>'
    
    @classmethod
    def get_by_type(cls, event_type, days=30):
        """Get events by type within specified days"""
        since = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        return Session.query(cls).filter(
            cls.event_type == event_type,
            cls.timestamp >= since
        ).all()
    
    @classmethod
    def get_popular_datasets(cls, days=30, limit=10):
        """Get most viewed datasets in the last N days"""
        from sqlalchemy import func
        since = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        
        return Session.query(
            cls.dataset_id,
            func.count(cls.id).label('view_count')
        ).filter(
            cls.event_type == 'dataset_view',
            cls.dataset_id.isnot(None),
            cls.timestamp >= since
        ).group_by(cls.dataset_id).order_by(
            func.count(cls.id).desc()
        ).limit(limit).all()
    
    @classmethod
    def get_search_terms(cls, days=30, limit=20):
        """Get popular search terms"""
        from sqlalchemy import func
        since = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        
        # Extract search query from event_data JSON
        return Session.query(
            cls.event_data['query'].astext.label('search_term'),
            func.count(cls.id).label('search_count')
        ).filter(
            cls.event_type == 'search_query',
            cls.event_data['query'].astext.isnot(None),
            cls.timestamp >= since
        ).group_by(cls.event_data['query'].astext).order_by(
            func.count(cls.id).desc()
        ).limit(limit).all()


def create_analytics_tables():
    """Create analytics tables in the database"""
    analytics_events_table.create(meta.engine, checkfirst=True)


def drop_analytics_tables():
    """Drop analytics tables (for development/testing)"""
    analytics_events_table.drop(meta.engine, checkfirst=True)
    

# Add the table to the class manually 
AnalyticsEvent.__table__ = analytics_events_table


def init_db():
    """Initialize analytics database tables"""
    Base.metadata.create_all(meta.engine)
    meta.Session.commit()


def drop_db():
    """Drop analytics database tables"""
    Base.metadata.drop_all(meta.engine)
    meta.Session.commit()


def create_analytics_tables():
    """Create analytics tables (alias for init_db)"""
    init_db()


def drop_analytics_tables():
    """Drop analytics tables (alias for drop_db)"""
    drop_db()

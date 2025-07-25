import uuid
import datetime
from sqlalchemy import Column, String, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from ckan.model import meta
from ckan.model.domain_object import DomainObject


Base = declarative_base()


class AnalyticsEvent(DomainObject, Base):
    """
    Analytics event tracking for CKAN usage patterns.
    
    Tracks user interactions with datasets, resources, and search
    while respecting privacy (IP addresses are hashed).
    """
    __tablename__ = 'analytics_events'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(50), nullable=False, index=True)
    # Event types: 'dataset_view', 'resource_download', 'search_query', 'api_call'
    
    # Dataset/Resource references (optional based on event type)
    dataset_id = Column(String(100), nullable=True, index=True)
    resource_id = Column(String(100), nullable=True, index=True)
    
    # User tracking (privacy-respecting)
    user_id = Column(String(100), nullable=True)  # Only for logged-in users
    session_hash = Column(String(64), nullable=True)  # Hashed session/IP combo
    
    # Event metadata
    event_data = Column(JSONB, nullable=True)  # Flexible JSON storage for event-specific data
    user_agent = Column(Text, nullable=True)
    referrer = Column(Text, nullable=True)
    
    # Privacy flags
    do_not_track = Column(Boolean, default=False)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f'<AnalyticsEvent {self.event_type} {self.timestamp}>'
    
    @classmethod
    def get_by_type(cls, event_type, days=30):
        """Get events by type within specified days"""
        since = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        return meta.Session.query(cls).filter(
            cls.event_type == event_type,
            cls.timestamp >= since
        ).all()
    
    @classmethod
    def get_popular_datasets(cls, days=30, limit=10):
        """Get most viewed datasets in the last N days"""
        from sqlalchemy import func
        since = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        
        return meta.Session.query(
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
        return meta.Session.query(
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
    Base.metadata.create_all(meta.engine)


def drop_analytics_tables():
    """Drop analytics tables (for development/testing)"""
    Base.metadata.drop_all(meta.engine)


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

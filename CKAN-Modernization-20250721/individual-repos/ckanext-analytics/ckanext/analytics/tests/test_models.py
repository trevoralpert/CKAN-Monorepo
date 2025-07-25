import pytest
import datetime
from unittest.mock import patch, MagicMock

import ckan.tests.helpers as helpers
import ckan.model as model
from ckan.tests import factories

from ckanext.analytics.models import AnalyticsEvent, create_analytics_tables, drop_analytics_tables


class TestAnalyticsEvent(helpers.FunctionalTestBase):
    """Test analytics event model"""
    
    def setup_method(self):
        """Set up test fixtures"""
        helpers.reset_db()
        create_analytics_tables()
    
    def teardown_method(self):
        """Clean up after tests"""
        drop_analytics_tables()
        helpers.reset_db()
    
    def test_create_analytics_event(self):
        """Test creating an analytics event"""
        event = AnalyticsEvent(
            event_type='dataset_view',
            dataset_id='test-dataset',
            session_hash='test-hash',
            event_data={'test': 'data'},
            timestamp=datetime.datetime.utcnow()
        )
        
        model.Session.add(event)
        model.Session.commit()
        
        # Verify event was created
        saved_event = model.Session.query(AnalyticsEvent).first()
        assert saved_event is not None
        assert saved_event.event_type == 'dataset_view'
        assert saved_event.dataset_id == 'test-dataset'
        assert saved_event.event_data['test'] == 'data'
    
    def test_get_popular_datasets(self):
        """Test getting popular datasets"""
        # Create test events
        events = [
            AnalyticsEvent(
                event_type='dataset_view',
                dataset_id='dataset-1',
                timestamp=datetime.datetime.utcnow()
            ),
            AnalyticsEvent(
                event_type='dataset_view',
                dataset_id='dataset-1',
                timestamp=datetime.datetime.utcnow()
            ),
            AnalyticsEvent(
                event_type='dataset_view',
                dataset_id='dataset-2',
                timestamp=datetime.datetime.utcnow()
            )
        ]
        
        for event in events:
            model.Session.add(event)
        model.Session.commit()
        
        # Test popular datasets query
        popular = AnalyticsEvent.get_popular_datasets(days=30, limit=10)
        
        assert len(popular) == 2
        # Should be ordered by popularity
        assert popular[0][0] == 'dataset-1'
        assert popular[0][1] == 2  # 2 views
        assert popular[1][0] == 'dataset-2'
        assert popular[1][1] == 1  # 1 view
    
    def test_get_search_terms(self):
        """Test getting popular search terms"""
        # Create test search events
        events = [
            AnalyticsEvent(
                event_type='search_query',
                event_data={'query': 'covid data'},
                timestamp=datetime.datetime.utcnow()
            ),
            AnalyticsEvent(
                event_type='search_query',
                event_data={'query': 'covid data'},
                timestamp=datetime.datetime.utcnow()
            ),
            AnalyticsEvent(
                event_type='search_query',
                event_data={'query': 'budget'},
                timestamp=datetime.datetime.utcnow()
            )
        ]
        
        for event in events:
            model.Session.add(event)
        model.Session.commit()
        
        # Test search terms query
        search_terms = AnalyticsEvent.get_search_terms(days=30, limit=10)
        
        assert len(search_terms) == 2
        # Should be ordered by frequency
        assert search_terms[0][0] == 'covid data'
        assert search_terms[0][1] == 2
        assert search_terms[1][0] == 'budget'
        assert search_terms[1][1] == 1
    
    def test_get_by_type(self):
        """Test getting events by type"""
        # Create test events
        events = [
            AnalyticsEvent(
                event_type='dataset_view',
                timestamp=datetime.datetime.utcnow()
            ),
            AnalyticsEvent(
                event_type='search_query',
                timestamp=datetime.datetime.utcnow()
            ),
            AnalyticsEvent(
                event_type='dataset_view',
                timestamp=datetime.datetime.utcnow()
            )
        ]
        
        for event in events:
            model.Session.add(event)
        model.Session.commit()
        
        # Test filtering by type
        dataset_views = AnalyticsEvent.get_by_type('dataset_view', days=30)
        search_queries = AnalyticsEvent.get_by_type('search_query', days=30)
        
        assert len(dataset_views) == 2
        assert len(search_queries) == 1
        assert all(e.event_type == 'dataset_view' for e in dataset_views)
        assert search_queries[0].event_type == 'search_query'
    
    def test_privacy_fields(self):
        """Test privacy-related fields"""
        event = AnalyticsEvent(
            event_type='dataset_view',
            session_hash='hashed-session',
            user_agent='Mozilla/5.0',
            referrer='https://example.com',
            do_not_track=True,
            timestamp=datetime.datetime.utcnow()
        )
        
        model.Session.add(event)
        model.Session.commit()
        
        saved_event = model.Session.query(AnalyticsEvent).first()
        assert saved_event.session_hash == 'hashed-session'
        assert saved_event.user_agent == 'Mozilla/5.0'
        assert saved_event.referrer == 'https://example.com'
        assert saved_event.do_not_track is True
    
    def test_old_events_excluded(self):
        """Test that old events are excluded from queries"""
        # Create old event (35 days ago)
        old_event = AnalyticsEvent(
            event_type='dataset_view',
            dataset_id='old-dataset',
            timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=35)
        )
        
        # Create recent event
        recent_event = AnalyticsEvent(
            event_type='dataset_view',
            dataset_id='recent-dataset',
            timestamp=datetime.datetime.utcnow()
        )
        
        model.Session.add(old_event)
        model.Session.add(recent_event)
        model.Session.commit()
        
        # Test that only recent events are returned
        popular = AnalyticsEvent.get_popular_datasets(days=30)
        
        assert len(popular) == 1
        assert popular[0][0] == 'recent-dataset'

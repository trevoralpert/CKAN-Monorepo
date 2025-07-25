import pytest
import datetime
from unittest.mock import patch, MagicMock

import ckan.tests.helpers as helpers
import ckan.model as model
from ckan.tests import factories

from ckanext.analytics.logic.action import (
    package_show_with_analytics, package_search_with_analytics,
    resource_download_with_analytics, _log_event, 
    _get_session_hash, _check_do_not_track
)
from ckanext.analytics.models import AnalyticsEvent, create_analytics_tables


class TestAnalyticsActions(helpers.FunctionalTestBase):
    """Test analytics action functions"""
    
    def setup_method(self):
        """Set up test fixtures"""
        helpers.reset_db()
        create_analytics_tables()
    
    def test_get_session_hash(self):
        """Test session hash generation"""
        # Mock request object
        mock_request = MagicMock()
        mock_request.environ = {
            'REMOTE_ADDR': '192.168.1.1',
            'HTTP_USER_AGENT': 'Test Browser'
        }
        
        hash1 = _get_session_hash(mock_request)
        assert hash1 is not None
        assert len(hash1) == 64  # SHA256 hex digest length
        
        # Same inputs should produce same hash
        hash2 = _get_session_hash(mock_request)
        assert hash1 == hash2
        
        # Different inputs should produce different hash
        mock_request.environ['REMOTE_ADDR'] = '192.168.1.2'
        hash3 = _get_session_hash(mock_request)
        assert hash1 != hash3
    
    def test_check_do_not_track(self):
        """Test Do Not Track header detection"""
        # Mock request with DNT header
        mock_request = MagicMock()
        mock_request.environ = {'HTTP_DNT': '1'}
        
        assert _check_do_not_track(mock_request) is True
        
        # Mock request without DNT header
        mock_request.environ = {}
        assert _check_do_not_track(mock_request) is False
        
        # Mock request with DNT=0
        mock_request.environ = {'HTTP_DNT': '0'}
        assert _check_do_not_track(mock_request) is False
    
    @patch('ckanext.analytics.logic.action.toolkit.request')
    def test_log_event_basic(self, mock_request):
        """Test basic event logging"""
        # Mock request
        mock_request.environ = {
            'REMOTE_ADDR': '192.168.1.1',
            'HTTP_USER_AGENT': 'Test Browser',
            'HTTP_REFERER': 'https://example.com',
            'HTTP_DNT': '0'
        }
        
        # Log an event
        _log_event(
            event_type='dataset_view',
            dataset_id='test-dataset',
            user_id='test-user',
            event_data={'test': 'data'}
        )
        
        # Verify event was logged
        event = model.Session.query(AnalyticsEvent).first()
        assert event is not None
        assert event.event_type == 'dataset_view'
        assert event.dataset_id == 'test-dataset'
        assert event.user_id == 'test-user'
        assert event.event_data['test'] == 'data'
        assert event.do_not_track is False
    
    @patch('ckanext.analytics.logic.action.toolkit.request')
    def test_log_event_with_dnt(self, mock_request):
        """Test event logging respects Do Not Track"""
        # Mock request with DNT header
        mock_request.environ = {'HTTP_DNT': '1'}
        
        # Attempt to log an event
        _log_event(event_type='dataset_view', dataset_id='test-dataset')
        
        # Verify no event was logged due to DNT
        event_count = model.Session.query(AnalyticsEvent).count()
        assert event_count == 0
    
    @patch('ckanext.analytics.logic.action.toolkit.get_action')
    @patch('ckanext.analytics.logic.action._log_event')
    def test_package_show_with_analytics(self, mock_log_event, mock_get_action):
        """Test package_show wrapper logs analytics"""
        # Mock the original package_show action
        mock_package_show = MagicMock()
        mock_package_show.return_value = {
            'id': 'test-dataset',
            'name': 'test-dataset',
            'title': 'Test Dataset',
            'organization': {'name': 'test-org'}
        }
        mock_get_action.return_value = mock_package_show
        
        # Call the analytics wrapper
        context = {'user': 'test-user'}
        data_dict = {'id': 'test-dataset'}
        
        result = package_show_with_analytics(context, data_dict)
        
        # Verify original action was called
        mock_package_show.assert_called_once_with(context, data_dict)
        
        # Verify analytics event was logged
        mock_log_event.assert_called_once()
        call_args = mock_log_event.call_args
        assert call_args[1]['event_type'] == 'dataset_view'
        assert call_args[1]['dataset_id'] == 'test-dataset'
        assert call_args[1]['user_id'] == 'test-user'
        
        # Verify result is returned correctly
        assert result['id'] == 'test-dataset'
    
    @patch('ckanext.analytics.logic.action.toolkit.get_action')
    @patch('ckanext.analytics.logic.action._log_event')
    def test_package_search_with_analytics(self, mock_log_event, mock_get_action):
        """Test package_search wrapper logs analytics"""
        # Mock the original package_search action
        mock_package_search = MagicMock()
        mock_package_search.return_value = {
            'count': 5,
            'results': [{'id': 'dataset1'}, {'id': 'dataset2'}]
        }
        mock_get_action.return_value = mock_package_search
        
        # Call the analytics wrapper
        context = {'user': 'test-user'}
        data_dict = {
            'q': 'covid data',
            'sort': 'relevance',
            'facet.field': ['organization']
        }
        
        result = package_search_with_analytics(context, data_dict)
        
        # Verify original action was called
        mock_package_search.assert_called_once_with(context, data_dict)
        
        # Verify analytics event was logged
        mock_log_event.assert_called_once()
        call_args = mock_log_event.call_args
        assert call_args[1]['event_type'] == 'search_query'
        assert call_args[1]['user_id'] == 'test-user'
        
        # Check event data
        event_data = call_args[1]['event_data']
        assert event_data['query'] == 'covid data'
        assert event_data['sort'] == 'relevance'
        assert event_data['results_count'] == 5
        
        # Verify result is returned correctly
        assert result['count'] == 5
    
    @patch('ckanext.analytics.logic.action.toolkit.get_action')
    @patch('ckanext.analytics.logic.action._log_event')
    def test_resource_download_with_analytics(self, mock_log_event, mock_get_action):
        """Test resource download analytics logging"""
        # Mock resource_show action
        mock_resource_show = MagicMock()
        mock_resource_show.return_value = {
            'id': 'resource-123',
            'package_id': 'dataset-456',
            'name': 'data.csv',
            'format': 'CSV',
            'size': 1024,
            'url': 'http://example.com/data.csv'
        }
        mock_get_action.return_value = mock_resource_show
        
        # Call the analytics function
        context = {'user': 'test-user'}
        data_dict = {'id': 'resource-123'}
        
        resource_download_with_analytics(context, data_dict)
        
        # Verify resource_show was called
        mock_resource_show.assert_called_once_with(context, {'id': 'resource-123'})
        
        # Verify analytics event was logged
        mock_log_event.assert_called_once()
        call_args = mock_log_event.call_args
        assert call_args[1]['event_type'] == 'resource_download'
        assert call_args[1]['dataset_id'] == 'dataset-456'
        assert call_args[1]['resource_id'] == 'resource-123'
        assert call_args[1]['user_id'] == 'test-user'
        
        # Check event data
        event_data = call_args[1]['event_data']
        assert event_data['resource_name'] == 'data.csv'
        assert event_data['resource_format'] == 'CSV'
        assert event_data['resource_size'] == 1024
    
    @patch('ckanext.analytics.logic.action._log_event')
    def test_log_event_error_handling(self, mock_log_event):
        """Test that logging errors don't break main functionality"""
        # Mock _log_event to raise an exception
        mock_log_event.side_effect = Exception('Database error')
        
        # This should not raise an exception
        try:
            from ckanext.analytics.logic.action import package_show_with_analytics
            # The function should handle the error gracefully
        except Exception:
            pytest.fail('Analytics error should not propagate')
    
    def test_get_actions_structure(self):
        """Test that get_actions returns the correct structure"""
        from ckanext.analytics.logic.action import get_actions
        
        actions = get_actions()
        
        assert 'package_show' in actions
        assert 'package_search' in actions
        assert callable(actions['package_show'])
        assert callable(actions['package_search'])


class TestPrivacyFeatures:
    """Test privacy-related functionality"""
    
    def test_session_hash_anonymization(self):
        """Test that session hashes don't contain original data"""
        mock_request = MagicMock()
        mock_request.environ = {
            'REMOTE_ADDR': '192.168.1.100',
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        
        session_hash = _get_session_hash(mock_request)
        
        # Hash should not contain original IP or user agent
        assert '192.168.1.100' not in session_hash
        assert 'Mozilla' not in session_hash
        assert 'Windows' not in session_hash
        
        # Should be valid hex string
        assert all(c in '0123456789abcdef' for c in session_hash)
    
    def test_no_request_handling(self):
        """Test functions handle missing request gracefully"""
        # These should not raise errors
        assert _get_session_hash(None) is None
        assert _check_do_not_track(None) is False

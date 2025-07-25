import pytest
import json
import datetime
from unittest.mock import patch, MagicMock

import ckan.tests.helpers as helpers

from ckanext.analytics.cache import (
    generate_cache_key, cached_query, AnalyticsCache, 
    get_redis_client, clear_analytics_cache
)


class TestAnalyticsCache(helpers.FunctionalTestBase):
    """Test analytics caching functionality"""
    
    def test_generate_cache_key(self):
        """Test cache key generation"""
        # Test basic key generation
        key = generate_cache_key('test', 'arg1', 'arg2', param='value')
        assert 'analytics:test:' in key
        assert 'arg1:arg2' in key
        assert 'param=value' in key
        
        # Test long key hashing
        long_args = ['very_long_argument'] * 20
        long_key = generate_cache_key('test', *long_args)
        assert len(long_key) < 250  # Should be hashed
        assert 'analytics:test:' in long_key
    
    @patch('ckanext.analytics.cache.get_redis_client')
    def test_cached_query_decorator(self, mock_redis_client):
        """Test the cached_query decorator"""
        # Mock Redis client
        mock_client = MagicMock()
        mock_redis_client.return_value = mock_client
        
        # Test cache miss - function should be called
        mock_client.get.return_value = None
        
        @cached_query(cache_timeout=300)
        def test_function(arg1, arg2='default'):
            return {'result': f'{arg1}_{arg2}'}
        
        result = test_function('test', arg2='value')
        
        assert result == {'result': 'test_value'}
        mock_client.get.assert_called_once()
        mock_client.setex.assert_called_once()
        
        # Test cache hit - function should not be called again
        mock_client.reset_mock()
        mock_client.get.return_value = json.dumps({'cached': 'result'})
        
        cached_result = test_function('test', arg2='value')
        
        assert cached_result == {'cached': 'result'}
        mock_client.get.assert_called_once()
        mock_client.setex.assert_not_called()
    
    @patch('ckanext.analytics.cache.get_redis_client')
    def test_cached_query_redis_unavailable(self, mock_redis_client):
        """Test cached_query when Redis is unavailable"""
        # Mock Redis as unavailable
        mock_redis_client.return_value = None
        
        @cached_query(cache_timeout=300)
        def test_function(arg):
            return {'result': arg}
        
        # Function should still work without caching
        result = test_function('test')
        assert result == {'result': 'test'}
    
    @patch('ckanext.analytics.cache.get_redis_client')
    def test_cached_query_redis_error(self, mock_redis_client):
        """Test cached_query with Redis errors"""
        # Mock Redis client that raises errors
        mock_client = MagicMock()
        mock_client.get.side_effect = Exception('Redis error')
        mock_redis_client.return_value = mock_client
        
        @cached_query(cache_timeout=300)
        def test_function(arg):
            return {'result': arg}
        
        # Function should work despite Redis errors
        result = test_function('test')
        assert result == {'result': 'test'}
    
    @patch('ckanext.analytics.models.AnalyticsEvent')
    @patch('ckanext.analytics.cache.get_redis_client')
    def test_analytics_cache_get_popular_datasets(self, mock_redis_client, mock_event):
        """Test cached popular datasets query"""
        # Mock Redis as unavailable to test direct query
        mock_redis_client.return_value = None
        
        # Mock the database query
        mock_event.get_popular_datasets.return_value = [('dataset1', 5), ('dataset2', 3)]
        
        result = AnalyticsCache.get_popular_datasets(30)
        
        assert result == [('dataset1', 5), ('dataset2', 3)]
        mock_event.get_popular_datasets.assert_called_once_with(days=30, limit=10)
    
    @patch('ckanext.analytics.models.AnalyticsEvent')
    @patch('ckanext.analytics.cache.get_redis_client')
    def test_analytics_cache_get_search_terms(self, mock_redis_client, mock_event):
        """Test cached search terms query"""
        # Mock Redis as unavailable
        mock_redis_client.return_value = None
        
        # Mock the database query
        mock_event.get_search_terms.return_value = [('covid', 10), ('budget', 5)]
        
        result = AnalyticsCache.get_search_terms(30)
        
        assert result == [('covid', 10), ('budget', 5)]
        mock_event.get_search_terms.assert_called_once_with(days=30, limit=20)
    
    @patch('ckanext.analytics.cache.get_redis_client')
    def test_clear_analytics_cache(self, mock_redis_client):
        """Test clearing analytics cache"""
        mock_client = MagicMock()
        mock_client.keys.return_value = ['analytics:key1', 'analytics:key2']
        mock_redis_client.return_value = mock_client
        
        clear_analytics_cache()
        
        mock_client.keys.assert_called_once_with('analytics:*')
        mock_client.delete.assert_called_once_with('analytics:key1', 'analytics:key2')
    
    @patch('ckanext.analytics.cache.get_redis_client')
    def test_clear_analytics_cache_no_redis(self, mock_redis_client):
        """Test clearing cache when Redis is unavailable"""
        mock_redis_client.return_value = None
        
        # Should not raise error
        clear_analytics_cache()
    
    def test_get_dashboard_data_structure(self):
        """Test dashboard data structure"""
        with patch.object(AnalyticsCache, 'get_popular_datasets', return_value=[]):
            with patch.object(AnalyticsCache, 'get_search_terms', return_value=[]):
                with patch.object(AnalyticsCache, 'get_event_counts', return_value={}):
                    with patch.object(AnalyticsCache, 'get_daily_activity', return_value={'labels': [], 'data': []}):
                        
                        data = AnalyticsCache.get_dashboard_data(30)
                        
                        # Check structure
                        assert 'popular_datasets' in data
                        assert 'search_terms' in data
                        assert 'event_counts' in data
                        assert 'daily_activity' in data
                        
                        # Check daily activity structure
                        assert 'labels' in data['daily_activity']
                        assert 'data' in data['daily_activity']


class TestRedisConnection:
    """Test Redis connection functionality"""
    
    @patch('redis.from_url')
    def test_redis_connection_success(self, mock_redis):
        """Test successful Redis connection"""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        
        client = get_redis_client()
        
        assert client is not None
        mock_client.ping.assert_called_once()
    
    @patch('redis.from_url')
    def test_redis_connection_failure(self, mock_redis):
        """Test Redis connection failure"""
        mock_redis.side_effect = Exception('Connection failed')
        
        client = get_redis_client()
        
        assert client is None

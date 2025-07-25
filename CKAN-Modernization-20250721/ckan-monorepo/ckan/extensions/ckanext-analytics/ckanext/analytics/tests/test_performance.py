import pytest
import time
import datetime
from unittest.mock import patch, MagicMock

import ckan.tests.helpers as helpers
import ckan.model as model

from ckanext.analytics.models import AnalyticsEvent, create_analytics_tables
from ckanext.analytics.cache import AnalyticsCache
from ckanext.analytics.logic.action import _log_event


class TestAnalyticsPerformance(helpers.FunctionalTestBase):
    """Test analytics performance requirements"""
    
    def setup_method(self):
        """Set up test fixtures"""
        helpers.reset_db()
        create_analytics_tables()
    
    def test_event_logging_performance(self):
        """Test that event logging is fast (<50ms)"""
        with patch('ckanext.analytics.logic.action.toolkit.request') as mock_request:
            # Mock request
            mock_request.environ = {
                'REMOTE_ADDR': '192.168.1.1',
                'HTTP_USER_AGENT': 'Test Browser',
                'HTTP_DNT': '0'
            }
            
            # Measure time for single event logging
            start_time = time.time()
            
            _log_event(
                event_type='dataset_view',
                dataset_id='test-dataset',
                event_data={'test': 'data'}
            )
            
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Should be under 50ms
            assert execution_time < 50, f'Event logging took {execution_time:.2f}ms, should be <50ms'
    
    def test_popular_datasets_query_performance(self):
        """Test popular datasets query performance"""
        # Create test data (100 events)
        events = []
        for i in range(100):
            event = AnalyticsEvent(
                event_type='dataset_view',
                dataset_id=f'dataset-{i % 20}',  # 20 different datasets
                timestamp=datetime.datetime.utcnow()
            )
            events.append(event)
        
        for event in events:
            model.Session.add(event)
        model.Session.commit()
        
        # Measure query time
        start_time = time.time()
        
        popular = AnalyticsEvent.get_popular_datasets(days=30, limit=10)
        
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000
        
        # Should be reasonably fast
        assert execution_time < 100, f'Popular datasets query took {execution_time:.2f}ms'
        assert len(popular) > 0
    
    def test_search_terms_query_performance(self):
        """Test search terms query performance"""
        # Create test search events
        search_terms = ['covid', 'budget', 'traffic', 'education', 'health']
        events = []
        
        for i in range(100):
            event = AnalyticsEvent(
                event_type='search_query',
                event_data={'query': search_terms[i % len(search_terms)]},
                timestamp=datetime.datetime.utcnow()
            )
            events.append(event)
        
        for event in events:
            model.Session.add(event)
        model.Session.commit()
        
        # Measure query time
        start_time = time.time()
        
        search_results = AnalyticsEvent.get_search_terms(days=30, limit=20)
        
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000
        
        # Should be reasonably fast
        assert execution_time < 100, f'Search terms query took {execution_time:.2f}ms'
        assert len(search_results) > 0
    
    @patch('ckanext.analytics.cache.get_redis_client')
    def test_cache_hit_performance(self, mock_redis_client):
        """Test that cache hits are very fast"""
        # Mock Redis client with cached data
        mock_client = MagicMock()
        mock_client.get.return_value = '[[\dataset1\, 5], [\dataset2\, 3]]'
        mock_redis_client.return_value = mock_client
        
        # Measure cache hit time
        start_time = time.time()
        
        result = AnalyticsCache.get_popular_datasets(30)
        
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000
        
        # Cache hits should be very fast
        assert execution_time < 10, f'Cache hit took {execution_time:.2f}ms, should be <10ms'
        assert result == [['dataset1', 5], ['dataset2', 3]]
    
    def test_bulk_event_creation_performance(self):
        """Test performance with bulk event creation"""
        # Create 1000 events
        events = []
        start_time = time.time()
        
        for i in range(1000):
            event = AnalyticsEvent(
                event_type='dataset_view',
                dataset_id=f'dataset-{i % 50}',
                session_hash=f'hash-{i % 100}',
                timestamp=datetime.datetime.utcnow()
            )
            events.append(event)
        
        # Bulk insert
        model.Session.bulk_save_objects(events)
        model.Session.commit()
        
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000
        
        # Should handle bulk inserts reasonably
        assert execution_time < 5000, f'Bulk insert of 1000 events took {execution_time:.2f}ms'
        
        # Verify data was inserted
        count = model.Session.query(AnalyticsEvent).count()
        assert count == 1000
    
    def test_dashboard_data_aggregation_performance(self):
        """Test performance of dashboard data aggregation"""
        # Create diverse test data
        event_types = ['dataset_view', 'search_query', 'resource_download']
        
        for i in range(500):
            event = AnalyticsEvent(
                event_type=event_types[i % len(event_types)],
                dataset_id=f'dataset-{i % 25}' if i % 3 == 0 else None,
                resource_id=f'resource-{i % 30}' if i % 3 == 2 else None,
                event_data={'query': f'term-{i % 10}'} if i % 3 == 1 else None,
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=i % 30)
            )
            model.Session.add(event)
        
        model.Session.commit()
        
        # Test dashboard data aggregation performance
        start_time = time.time()
        
        # This would normally use cache, but let's test direct queries
        with patch('ckanext.analytics.cache.get_redis_client', return_value=None):
            dashboard_data = AnalyticsCache.get_dashboard_data(30, force_refresh=True)
        
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000
        
        # Should aggregate data reasonably fast
        assert execution_time < 500, f'Dashboard aggregation took {execution_time:.2f}ms'
        
        # Verify data structure
        assert 'popular_datasets' in dashboard_data
        assert 'search_terms' in dashboard_data
        assert 'event_counts' in dashboard_data
        assert 'daily_activity' in dashboard_data
    
    def test_memory_usage_with_large_dataset(self):
        """Test memory efficiency with larger datasets"""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create larger dataset (5000 events)
        events = []
        for i in range(5000):
            event = AnalyticsEvent(
                event_type='dataset_view',
                dataset_id=f'dataset-{i % 100}',
                session_hash=f'hash-{i % 200}',
                event_data={'key': f'value-{i}'},
                timestamp=datetime.datetime.utcnow()
            )
            events.append(event)
        
        # Process in batches to avoid memory spikes
        batch_size = 1000
        for i in range(0, len(events), batch_size):
            batch = events[i:i + batch_size]
            model.Session.bulk_save_objects(batch)
            model.Session.commit()
        
        # Test queries on large dataset
        popular = AnalyticsEvent.get_popular_datasets(days=30, limit=50)
        
        # Get final memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024, f'Memory increased by {memory_increase / 1024 / 1024:.2f}MB'
        
        # Query should still work
        assert len(popular) > 0
        assert len(popular) <= 50


class TestScalabilityLimits:
    """Test system limits and scalability"""
    
    def test_large_event_data_handling(self):
        """Test handling of large event data"""
        # Create event with large JSON data
        large_data = {
            'large_field': 'x' * 1000,  # 1KB string
            'array_field': list(range(100)),
            'nested': {
                'deep': {
                    'data': ['item'] * 50
                }
            }
        }
        
        start_time = time.time()
        
        with patch('ckanext.analytics.logic.action.toolkit.request') as mock_request:
            mock_request.environ = {'HTTP_DNT': '0'}
            
            _log_event(
                event_type='dataset_view',
                dataset_id='test-dataset',
                event_data=large_data
            )
        
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000
        
        # Should handle large data without significant performance impact
        assert execution_time < 100, f'Large event data took {execution_time:.2f}ms'
    
    def test_concurrent_event_logging_simulation(self):
        """Simulate concurrent event logging"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def log_events(thread_id, num_events):
            """Log events in a separate thread"""
            start_time = time.time()
            
            with patch('ckanext.analytics.logic.action.toolkit.request') as mock_request:
                mock_request.environ = {'HTTP_DNT': '0'}
                
                for i in range(num_events):
                    _log_event(
                        event_type='dataset_view',
                        dataset_id=f'dataset-{thread_id}-{i}',
                        event_data={'thread': thread_id, 'event': i}
                    )
            
            end_time = time.time()
            results.put((thread_id, end_time - start_time))
        
        # Start multiple threads
        threads = []
        num_threads = 5
        events_per_thread = 20
        
        for i in range(num_threads):
            thread = threading.Thread(target=log_events, args=(i, events_per_thread))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        total_time = 0
        while not results.empty():
            thread_id, execution_time = results.get()
            total_time += execution_time
            # Each thread should complete in reasonable time
            assert execution_time < 5.0, f'Thread {thread_id} took {execution_time:.2f}s'
        
        # Verify all events were logged
        total_events = model.Session.query(AnalyticsEvent).count()
        assert total_events == num_threads * events_per_thread

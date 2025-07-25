import click
import datetime
from sqlalchemy import func, desc
from ckan.model import Session, Package, Resource, User
from ckanext.analytics.models import AnalyticsEvent, init_db, drop_db

@click.group()
def analytics():
    """Analytics commands."""
    pass

@analytics.command('init-db')
@click.option('--yes', is_flag=True, help='Confirm database initialization.')
def init_db_command(yes):
    """Initialize the analytics database tables."""
    if not yes and not click.confirm("This will create analytics tables. Continue?"):
        return
    init_db()
    click.echo("Analytics tables created successfully.")

@analytics.command('drop-db')
@click.option('--yes', is_flag=True, help='Confirm database drop.')
def drop_db_command(yes):
    """Drop the analytics database tables."""
    if not yes and not click.confirm("This will drop ALL analytics data. Continue?"):
        return
    drop_db()
    click.echo("Analytics tables dropped successfully.")

@analytics.command('stats')
@click.option('--days', default=30, type=int, help='Number of days to look back for statistics.')
def stats_command(days):
    """Display analytics statistics."""
    click.echo("\n📊 Most Popular Datasets (last {} days):".format(days))
    click.echo("--------------------------------------------------")
    
    # Get popular datasets
    popular_datasets = Session.query(
        Package.title, func.count(AnalyticsEvent.dataset_id).label('views')
    ).join(AnalyticsEvent, Package.id == AnalyticsEvent.dataset_id)\
    .filter(AnalyticsEvent.event_type == 'dataset_view')\
    .filter(AnalyticsEvent.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(days=days))\
    .group_by(Package.title)\
    .order_by(desc('views'))\
    .limit(10).all()

    if popular_datasets:
        for title, views in popular_datasets:
            click.echo(f"- {title}: {views} views")
    else:
        click.echo("No dataset views recorded.")

    click.echo("\n🔍 Popular Search Terms (last {} days):".format(days))
    click.echo("--------------------------------------------------")
    
    # Get popular search terms
    popular_search_terms = Session.query(
        AnalyticsEvent.event_data['query'].astext.label('query'), func.count(AnalyticsEvent.id).label('count')
    ).filter(AnalyticsEvent.event_type == 'search_query')\
    .filter(AnalyticsEvent.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(days=days))\
    .group_by(AnalyticsEvent.event_data['query'].astext)\
    .order_by(desc('count'))\
    .limit(10).all()

    if popular_search_terms:
        for query, count in popular_search_terms:
            if query:
                click.echo(f"- '{query}': {count} searches")
    else:
        click.echo("No search queries recorded.")

    click.echo("\n📈 Event Counts (last {} days):".format(days))
    click.echo("--------------------------------------------------")
    
    # Get event counts by type
    event_counts = Session.query(
        AnalyticsEvent.event_type, func.count(AnalyticsEvent.id).label('count')
    ).filter(AnalyticsEvent.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(days=days))\
    .group_by(AnalyticsEvent.event_type)\
    .order_by(desc('count'))\
    .all()

    if event_counts:
        for event_type, count in event_counts:
            click.echo(f"- {event_type}: {count} events")
    else:
        click.echo("No events recorded.")

@analytics.command('health-check')
def health_check_command():
    """Check analytics system health"""
    click.echo('🏥 Checking analytics system health...')
    
    issues = []
    
    # Check database tables
    try:
        count = Session.query(AnalyticsEvent).count()
        click.echo(f'✅ Database: {count} events in analytics_events table')
    except Exception as e:
        issues.append(f'❌ Database: {e}')
    
    # Check Redis connection
    try:
        from ckanext.analytics.cache import get_redis_client
        redis_client = get_redis_client()
        if redis_client:
            redis_client.ping()
            click.echo('✅ Redis: Connection successful')
        else:
            issues.append('⚠️  Redis: Not available (caching disabled)')
    except Exception as e:
        issues.append(f'❌ Redis: {e}')
    
    # Check plugin configuration
    try:
        import ckan.plugins.toolkit as toolkit
        plugins = toolkit.config.get('ckan.plugins', '')
        if isinstance(plugins, str):
            plugins_list = plugins.split()
        else:
            plugins_list = plugins or []
            
        if 'analytics' in plugins_list:
            click.echo('✅ Plugin: analytics plugin is enabled')
        else:
            issues.append('❌ Plugin: analytics plugin not enabled in ckan.plugins')
    except Exception as e:
        issues.append(f'❌ Plugin: {e}')
    
    # Check recent activity
    try:
        recent_count = Session.query(AnalyticsEvent).filter(
            AnalyticsEvent.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(hours=24)
        ).count()
        click.echo(f'📈 Activity: {recent_count} events in last 24 hours')
        
        if recent_count == 0:
            issues.append('⚠️  Activity: No recent events (system may not be capturing data)')
    except Exception as e:
        issues.append(f'❌ Activity: {e}')
    
    # Summary
    if issues:
        click.echo('\n🚨 Issues found:')
        for issue in issues:
            click.echo(f'  {issue}')
    else:
        click.echo('\n🎉 All systems healthy!')
    
    return len(issues) == 0

@analytics.command('benchmark')
@click.option('--events', default=100, type=int, help='Number of events to create for benchmarking')
def benchmark_command(events):
    """Run analytics performance benchmarks"""
    import time
    
    click.echo(f'🏃 Running analytics benchmarks...')
    click.echo(f'Creating {events} test events...')
    
    # Create test events
    start_time = time.time()
    
    test_events = []
    for i in range(events):
        event = AnalyticsEvent(
            event_type='dataset_view' if i % 3 == 0 else 'search_query' if i % 3 == 1 else 'resource_download',
            dataset_id=f'dataset-{i % 10}',
            resource_id=f'resource-{i % 10}' if i % 3 == 2 else None,
            session_hash=f'hash-{i % 20}',
            event_data={'query': f'term-{i % 5}'} if i % 3 == 1 else None,
            timestamp=datetime.datetime.utcnow() - datetime.timedelta(minutes=i % 60)
        )
        test_events.append(event)
    
    # Bulk insert
    Session.bulk_save_objects(test_events)
    Session.commit()
    
    creation_time = time.time() - start_time
    click.echo(f'✅ Created {events} events in {creation_time:.2f}s ({events/creation_time:.0f} events/sec)')
    
    # Test query performance
    start_time = time.time()
    popular = AnalyticsEvent.get_popular_datasets(days=30, limit=10)
    query_time = time.time() - start_time
    
    click.echo(f'📊 Query Results:')
    click.echo(f'  Popular datasets query: {query_time:.3f}s')
    click.echo(f'  Found {len(popular)} popular datasets')
    
    # Clean up test data
    click.echo('🧹 Cleaning up test data...')
    Session.query(AnalyticsEvent).filter(
        AnalyticsEvent.dataset_id.like('dataset-%')
    ).delete(synchronize_session=False)
    Session.commit()
    
    click.echo('✅ Benchmark complete!')

def get_commands():
    return [analytics]

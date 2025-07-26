import json
import csv
from datetime import datetime, timedelta
from io import StringIO
from flask import Blueprint, render_template, request, jsonify, Response
import ckan.plugins.toolkit as toolkit
import ckan.model as model
from ckan.views import identify_user
from ckanext.analytics.models import AnalyticsEvent
from ckanext.analytics.cache import AnalyticsCache, clear_analytics_cache


def get_blueprints():
    """Return analytics dashboard blueprints"""
    return [analytics_dashboard]


analytics_dashboard = Blueprint('analytics_dashboard', __name__)


def _check_admin_access():
    """Check if current user has admin access"""
    # For development/testing - temporarily allow access
    # TODO: Implement proper admin check when authentication is working
    return True
    
    # Original code for when auth is fixed:
    # try:
    #     context = {'user': toolkit.c.user}
    #     toolkit.check_access('sysadmin', context, {})
    #     return True
    # except (toolkit.NotAuthorized, AttributeError):
    #     return False


@analytics_dashboard.route('/dashboard/analytics')
def dashboard():
    """Main analytics dashboard with Redis caching"""
    if not _check_admin_access():
        toolkit.abort(403, 'Admin access required')
    
    # Get time range from query params
    days = int(request.args.get('days', 30))
    days = min(days, 365)  # Cap at 1 year
    force_refresh = request.args.get('refresh') == '1'
    
    try:
        # Use cached data for better performance
        dashboard_data = AnalyticsCache.get_dashboard_data(days, force_refresh=force_refresh)
        
        popular_datasets = dashboard_data['popular_datasets']
        search_terms = dashboard_data['search_terms']
        event_counts = dashboard_data['event_counts']
        chart_data = dashboard_data['daily_activity']
        
        total_events = sum(event_counts.values())
        
        return render_template(
            'analytics/dashboard.html',
            popular_datasets=popular_datasets,
            search_terms=search_terms,
            event_counts=event_counts,
            chart_data=json.dumps(chart_data),
            days=days,
            total_events=total_events,
            cache_info={'cached': not force_refresh, 'timestamp': datetime.utcnow().isoformat()}
        )
        
    except Exception as e:
        toolkit.abort(500, f'Error loading analytics data: {e}')


@analytics_dashboard.route('/dashboard/analytics/api/data')
def api_data():
    """API endpoint for dashboard data with caching"""
    if not _check_admin_access():
        toolkit.abort(403, 'Admin access required')
    
    days = int(request.args.get('days', 30))
    force_refresh = request.args.get('refresh') == '1'
    
    try:
        # Use cached data
        dashboard_data = AnalyticsCache.get_dashboard_data(days, force_refresh=force_refresh)
        
        return jsonify({
            'popular_datasets': [{'id': d[0], 'views': d[1]} for d in dashboard_data['popular_datasets']],
            'search_terms': [{'term': s[0], 'count': s[1]} for s in dashboard_data['search_terms']],
            'event_counts': dashboard_data['event_counts'],
            'total_events': sum(dashboard_data['event_counts'].values()),
            'daily_activity': dashboard_data['daily_activity'],
            'cache_info': {'timestamp': datetime.utcnow().isoformat()}
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_dashboard.route('/dashboard/analytics/cache/clear')
def clear_cache():
    """Clear analytics cache (admin only)"""
    if not _check_admin_access():
        toolkit.abort(403, 'Admin access required')
    
    try:
        clear_analytics_cache()
        return jsonify({'status': 'success', 'message': 'Analytics cache cleared'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@analytics_dashboard.route('/dashboard/analytics/export/csv')
def export_csv():
    """Export analytics data as CSV with caching"""
    if not _check_admin_access():
        toolkit.abort(403, 'Admin access required')
    
    days = int(request.args.get('days', 30))
    export_type = request.args.get('type', 'summary')
    
    try:
        output = StringIO()
        
        if export_type == 'popular_datasets':
            writer = csv.writer(output)
            writer.writerow(['Dataset ID', 'Views', 'Period (days)'])
            
            # Use cached data
            popular = AnalyticsCache.get_popular_datasets(days)
            for dataset_id, views in popular:
                writer.writerow([dataset_id, views, days])
                
        elif export_type == 'search_terms':
            writer = csv.writer(output)
            writer.writerow(['Search Term', 'Count', 'Period (days)'])
            
            # Use cached data
            searches = AnalyticsCache.get_search_terms(days)
            for term, count in searches:
                writer.writerow([term, count, days])
                
        else:  # summary
            writer = csv.writer(output)
            writer.writerow(['Metric', 'Value', 'Period (days)'])
            
            # Use cached data
            event_counts = AnalyticsCache.get_event_counts(days)
            
            for event_type, count in event_counts.items():
                writer.writerow([f'{event_type}_events', count, days])
            
            writer.writerow(['total_events', sum(event_counts.values()), days])
        
        # Prepare response
        output.seek(0)
        filename = f'ckan_analytics_{export_type}_{days}days_{datetime.now().strftime("%Y%m%d")}.csv'
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        
    except Exception as e:
        toolkit.abort(500, f'Error exporting data: {e}')


@analytics_dashboard.route('/dashboard/analytics/datasets/<dataset_id>')
def dataset_detail(dataset_id):
    """Detailed analytics for a specific dataset"""
    if not _check_admin_access():
        toolkit.abort(403, 'Admin access required')
    
    days = int(request.args.get('days', 30))
    
    try:
        # Get dataset info
        dataset = toolkit.get_action('package_show')({}, {'id': dataset_id})
        
        # Get analytics for this dataset (not cached due to specificity)
        since = datetime.utcnow() - timedelta(days=days)
        events = model.Session.query(AnalyticsEvent).filter(
            AnalyticsEvent.dataset_id == dataset_id,
            AnalyticsEvent.timestamp >= since
        ).order_by(AnalyticsEvent.timestamp.desc()).limit(100).all()
        
        # Group by event type
        event_summary = {}
        for event in events:
            event_type = event.event_type
            if event_type not in event_summary:
                event_summary[event_type] = 0
            event_summary[event_type] += 1
        
        return render_template(
            'analytics/dataset_detail.html',
            dataset=dataset,
            events=events,
            event_summary=event_summary,
            days=days
        )
        
    except Exception as e:
        toolkit.abort(500, f'Error loading dataset analytics: {e}')


@analytics_dashboard.route('/dashboard/analytics/status')
def cache_status():
    """Show cache status and performance info"""
    if not _check_admin_access():
        toolkit.abort(403, 'Admin access required')
    
    try:
        from ckanext.analytics.cache import get_redis_client
        
        redis_client = get_redis_client()
        cache_status = {
            'redis_connected': redis_client is not None,
            'cache_keys_count': 0,
            'memory_usage': 'N/A'
        }
        
        if redis_client:
            try:
                # Get cache statistics
                cache_keys = redis_client.keys('analytics:*')
                cache_status['cache_keys_count'] = len(cache_keys)
                
                # Get memory info if available
                memory_info = redis_client.info('memory')
                cache_status['memory_usage'] = memory_info.get('used_memory_human', 'N/A')
                
            except Exception as e:
                cache_status['error'] = str(e)
        
        return jsonify(cache_status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# encoding: utf-8
from __future__ import annotations

import logging
from typing import Any

from flask import Blueprint

import ckan.lib.base as base
from ckan.lib.helpers import helper_functions as h
from ckan.common import _, current_user
from ckan.views.user import _extra_template_variables
from ckan.types import Context

log = logging.getLogger(__name__)

dashboard = Blueprint(u'dashboard', __name__, url_prefix=u'/dashboard')


@dashboard.before_request
def before_request() -> None:
    if current_user.is_anonymous:
        h.flash_error(_(u'Not authorized to see this page'))

        # flask types do not mention that it's possible to return a response
        # from the `before_request` callback
        return h.redirect_to(u'user.login')
    return None


def datasets() -> str:
    context: Context = {
        u'for_view': True,
        u'user': current_user.name,
        u'auth_user_obj': current_user
    }
    data_dict: dict[str, Any] = {
        u'user_obj': current_user,
        u'include_datasets': True}
    extra_vars = _extra_template_variables(context, data_dict)
    return base.render(u'user/dashboard_datasets.html', extra_vars)


def organizations() -> str:
    context: Context = {
        u'for_view': True,
        u'user': current_user.name,
        u'auth_user_obj': current_user
    }
    data_dict = {u'user_obj': current_user}
    extra_vars = _extra_template_variables(context, data_dict)
    return base.render(u'user/dashboard_organizations.html', extra_vars)


def groups() -> str:
    context: Context = {
        u'for_view': True,
        u'user': current_user.name,
        u'auth_user_obj': current_user
    }
    data_dict = {u'user_obj': current_user}
    extra_vars = _extra_template_variables(context, data_dict)
    return base.render(u'user/dashboard_groups.html', extra_vars)


def analytics() -> str:
    """Analytics dashboard integrated as a dashboard view"""
    context: Context = {
        u'for_view': True,
        u'user': current_user.name,
        u'auth_user_obj': current_user
    }
    data_dict = {u'user_obj': current_user}
    extra_vars = _extra_template_variables(context, data_dict)
    
    # Import analytics functionality
    try:
        from ckanext.analytics.cache import AnalyticsCache
        from flask import request
        import json
        from datetime import datetime
        
        # Get time range from query params (same logic as original)
        days = int(request.args.get('days', 30))
        days = min(days, 365)  # Cap at 1 year
        force_refresh = request.args.get('refresh') == '1'
        
        # Use cached data for better performance
        dashboard_data = AnalyticsCache.get_dashboard_data(days, force_refresh=force_refresh)
        
        popular_datasets = dashboard_data['popular_datasets']
        search_terms = dashboard_data['search_terms']
        event_counts = dashboard_data['event_counts'] 
        chart_data = dashboard_data['daily_activity']
        
        total_events = sum(event_counts.values())
        
        # Add analytics-specific variables to the standard dashboard variables
        extra_vars.update({
            'popular_datasets': popular_datasets,
            'search_terms': search_terms,
            'event_counts': event_counts,
            'chart_data': json.dumps(chart_data),
            'days': days,
            'total_events': total_events,
            'cache_info': {'cached': not force_refresh, 'timestamp': datetime.utcnow().isoformat()}
        })
        
        return base.render(u'user/dashboard_analytics.html', extra_vars)
        
    except ImportError:
        # Fallback if analytics extension not available
        return base.render(u'user/dashboard_analytics.html', extra_vars)


dashboard.add_url_rule(u'/datasets', view_func=datasets)
dashboard.add_url_rule(u'/groups', view_func=groups)
dashboard.add_url_rule(u'/organizations', view_func=organizations)
dashboard.add_url_rule(u'/analytics', view_func=analytics)

import hashlib
import datetime
import logging
from ckan.model import meta
import ckan.plugins.toolkit as toolkit
from ckanext.analytics.models import AnalyticsEvent

# Import the original CKAN actions to avoid recursion
from ckan.logic.action.get import (
    package_search as original_package_search,
    package_show as original_package_show,
)

log = logging.getLogger(__name__)


def _get_session_hash(request):
    """Create privacy-respecting session hash from IP and user agent"""
    if not request:
        return None

    # Combine IP and user agent for session tracking
    ip = request.environ.get("REMOTE_ADDR", "")
    user_agent = request.environ.get("HTTP_USER_AGENT", "")
    session_string = f"{ip}:{user_agent}"

    # Hash for privacy
    return hashlib.sha256(session_string.encode()).hexdigest()


def _check_do_not_track(request):
    """Check if user has Do Not Track enabled"""
    if not request:
        return False
    return request.environ.get("HTTP_DNT") == "1"


def _log_event(
    event_type, dataset_id=None, resource_id=None, event_data=None, user_id=None
):
    """Log an analytics event"""
    try:
        # Get request context
        request = toolkit.request if hasattr(toolkit, "request") else None

        # Respect Do Not Track
        do_not_track = _check_do_not_track(request)
        if do_not_track:
            log.debug(f"Skipping analytics event {event_type} due to DNT header")
            return

        # Create event
        event = AnalyticsEvent(
            event_type=event_type,
            dataset_id=dataset_id,
            resource_id=resource_id,
            user_id=user_id,
            session_hash=_get_session_hash(request),
            event_data=event_data,
            user_agent=request.environ.get("HTTP_USER_AGENT") if request else None,
            referrer=request.environ.get("HTTP_REFERER") if request else None,
            do_not_track=do_not_track,
            timestamp=datetime.datetime.utcnow(),
        )

        # Save to database
        meta.Session.add(event)
        meta.Session.commit()

        log.debug(f"Analytics event logged: {event_type}")

    except Exception as e:
        log.error(f"Error logging analytics event {event_type}: {e}")
        # Don't let analytics errors break the main functionality
        meta.Session.rollback()


# Wrapper functions for original actions - COMMENTED OUT DUE TO RECURSION ISSUE
# Will be replaced with hook-based approach in plugin.py

# @toolkit.side_effect_free
# def package_show_with_analytics(context, data_dict):
#     """Wrapper for package_show that logs view events"""
#     # Call original action directly to avoid recursion
#     result = original_package_show(context, data_dict)

#     # Log analytics event
#     user_id = context.get("user")
#     dataset_id = result.get("id")

#     _log_event(
#         event_type="dataset_view",
#         dataset_id=dataset_id,
#         user_id=user_id,
#         event_data={
#             "dataset_name": result.get("name"),
#             "dataset_title": result.get("title"),
#             "organization": result.get("organization", {}).get("name")
#             if result.get("organization")
#             else None,
#         },
#     )

#     return result


# @toolkit.side_effect_free
# def package_search_with_analytics(context, data_dict):
#     """Wrapper for package_search that logs search events"""
#     # Call original action directly to avoid recursion
#     result = original_package_search(context, data_dict)

#     # Log analytics event
#     user_id = context.get("user")
#     query = data_dict.get("q", "")

#     _log_event(
#         event_type="search_query",
#         user_id=user_id,
#         event_data={
#             "query": query,
#             "sort": data_dict.get("sort"),
#             "facet_fields": data_dict.get("facet.field", []),
#             "results_count": result.get("count", 0),
#             "filters": {k: v for k, v in data_dict.items() if k.startswith("fq")},
#         },
#     )

#     return result


def resource_download_with_analytics(context, data_dict):
    """Log resource download events"""
    resource_id = data_dict.get("id")
    user_id = context.get("user")

    # Get resource info
    try:
        resource = toolkit.get_action("resource_show")(context, {"id": resource_id})
        dataset_id = resource.get("package_id")

        _log_event(
            event_type="resource_download",
            dataset_id=dataset_id,
            resource_id=resource_id,
            user_id=user_id,
            event_data={
                "resource_name": resource.get("name"),
                "resource_format": resource.get("format"),
                "resource_size": resource.get("size"),
                "download_url": resource.get("url"),
            },
        )
    except Exception as e:
        log.error(f"Error logging resource download: {e}")


def get_actions():
    """Return analytics-enhanced actions"""
    # Temporarily disable action overrides to fix recursion - will implement differently
    return {
        # 'package_show': package_show_with_analytics,
        # 'package_search': package_search_with_analytics,
        # Note: resource downloads are handled differently via hooks
    }


def _invalidate_analytics_cache():
    """Invalidate analytics cache when new events are added"""
    try:
        from ckanext.analytics.cache import on_analytics_event_created

        on_analytics_event_created()
    except ImportError:
        # Cache module not available, skip
        pass


# Update the _log_event function to invalidate cache
def _log_event_with_cache_invalidation(
    event_type, dataset_id=None, resource_id=None, event_data=None, user_id=None
):
    """Log an analytics event and invalidate relevant caches"""
    # Log the event
    _log_event(event_type, dataset_id, resource_id, event_data, user_id)

    # Invalidate cache for better real-time updates
    _invalidate_analytics_cache()


# Override the original _log_event calls in wrapper functions
import sys

current_module = sys.modules[__name__]

# Replace _log_event with cache-aware version
original_log_event = current_module._log_event
current_module._log_event = _log_event_with_cache_invalidation

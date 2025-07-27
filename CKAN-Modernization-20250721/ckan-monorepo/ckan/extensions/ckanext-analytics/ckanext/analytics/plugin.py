import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging
import time
from flask import request, g

import ckanext.analytics.cli as cli
import ckanext.analytics.views as views
from ckanext.analytics.logic import action
from ckanext.analytics import validators

log = logging.getLogger(__name__)


class AnalyticsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IResourceController)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.IActions)
    
    # Config sync flag to run only once
    _config_synced = False

    # IConfigurer
    def update_config(self, config_):
        # Disable aggressive global_config.clear() to avoid wiping other plugins' settings.
        # We only need to register templates/assets here.
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "analytics")
        # Skip the previous full-config re-load that caused conflicts.
        return

    def _ensure_config_sync(self):
        """Ensure global config is synced - can be called from multiple places"""
        if AnalyticsPlugin._config_synced:
            return True
            
        try:
            from ckan.cli import load_config
            from ckan.common import config as global_config
            import os
            
            # Only sync if config is empty/None (avoid repeated syncing)
            if global_config.get('ckan.plugins') is None:
                config_file = os.environ.get('CKAN_CONFIG', 'demo.ini')
                if not os.path.isabs(config_file):
                    config_file = os.path.join(os.getcwd(), config_file)
                
                if os.path.exists(config_file):
                    fresh_config = load_config(config_file)
                    global_config.clear()
                    global_config.update(fresh_config)
                    AnalyticsPlugin._config_synced = True
                    log.info("Analytics Plugin: Config sync completed from %s", config_file)
                    
                    # Force plugin reload after config sync
                    try:
                        import ckan.plugins as plugins
                        plugins.load_all(force_update=True)
                        log.info("Analytics Plugin: Plugin reload completed after config sync")
                    except Exception as reload_e:
                        log.warning("Analytics Plugin: Plugin reload failed: %s", reload_e)
                    
                    return True
                    
        except Exception as e:
            log.error("Analytics Plugin: Config sync failed: %s", e)
            
        return False

    # IClick - Add CLI commands
    def get_commands(self):
        return cli.get_commands()

    # IValidators - Register custom validators
    def get_validators(self):
        return {
            'email_validator': validators.email_validator,
            'department_validator': validators.department_validator,
            'update_frequency_validator': validators.update_frequency_validator,
            'data_quality_validator': validators.data_quality_validator,
            'geographic_coverage_validator': validators.geographic_coverage_validator,
            'public_access_validator': validators.public_access_validator,
            'collection_method_validator': validators.collection_method_validator,
        }

    # IActions - Register AI suggestion API endpoints
    def get_actions(self):
        # SECONDARY CONFIG SYNC - run config sync here as backup
        self._ensure_config_sync()
        
        return {
            'get_dataset_ai_suggestions': action.get_dataset_ai_suggestions,
            'get_batch_ai_suggestions': action.get_batch_ai_suggestions,
            'accept_ai_suggestion': action.accept_ai_suggestion,
            'get_ai_suggestion_stats': action.get_ai_suggestion_stats,
            'reset_ai_suggestion_stats': action.reset_ai_suggestion_stats,
        }

    # IBlueprint - Add web dashboard
    def get_blueprint(self):
        # TERTIARY CONFIG SYNC - ensure config sync through web interface
        self._ensure_config_sync()
        return views.get_blueprints()

    # IPackageController - Track dataset views (SAFE - NO RECURSION)
    def after_show(self, context, pkg_dict):
        """Called after package_show completes successfully"""
        start_time = time.time()
        try:
            # Skip if this is an internal CKAN call or marked to skip logging
            if context.get("__no_log__"):
                return

            # Enhanced Flask context detection for safety
            try:
                # Check if we're in a proper Flask request context
                if not request:
                    log.debug("No Flask request context - skipping analytics")
                    return

                # Check if g object is available
                if not hasattr(g, "user"):
                    log.debug("No Flask g object - skipping analytics")
                    return

            except RuntimeError as e:
                # Outside application context
                log.debug(f"Outside Flask context - skipping analytics: {e}")
                return

            # Respect Do Not Track header
            if request.headers.get("DNT") == "1":
                log.debug("Skipping analytics due to DNT header")
                return

            # Additional safety: Check for valid dataset ID
            dataset_id = pkg_dict.get("id")
            if not dataset_id:
                log.debug("No dataset ID - skipping analytics")
                return

            # Log the dataset view event
            user_id = g.userobj.id if g.userobj else None

            action._log_event(
                event_type="dataset_view",
                dataset_id=pkg_dict.get("id"),
                user_id=user_id,
                event_data={
                    "dataset_name": pkg_dict.get("name"),
                    "dataset_title": pkg_dict.get("title"),
                    "organization": pkg_dict.get("organization", {}).get("name")
                    if pkg_dict.get("organization")
                    else None,
                },
            )

            # Performance monitoring
            elapsed = time.time() - start_time
            if elapsed > 0.05:  # 50ms warning threshold
                log.warning(
                    f"Analytics after_show took {elapsed:.3f}s - performance issue!"
                )

        except Exception as e:
            log.error(f"Analytics error in after_show: {e}")
            # Never let analytics break core functionality
            pass

    def after_search(self, search_results, search_params):
        """Called after package_search completes successfully"""
        start_time = time.time()
        try:
            # Skip if this is an internal CKAN call or marked to skip logging
            # (search_params is dict, need to check context separately if available)

            # Enhanced Flask context detection for safety
            try:
                # Check if we're in a proper Flask request context
                if not request:
                    log.debug("No Flask request context - skipping search analytics")
                    return

                # Check if g object is available
                if not hasattr(g, "user"):
                    log.debug("No Flask g object - skipping search analytics")
                    return

            except RuntimeError as e:
                # Outside application context
                log.debug(f"Outside Flask context - skipping search analytics: {e}")
                return

            # Respect Do Not Track header
            if request.headers.get("DNT") == "1":
                log.debug("Skipping analytics due to DNT header")
                return

            # Extract and validate search query
            query = search_params.get("q", "").strip()
            if not query:  # Only log meaningful searches
                log.debug("Empty search query - skipping analytics")
                return

            # Additional safety: validate search results structure
            if not isinstance(search_results, dict):
                log.debug("Invalid search results structure - skipping analytics")
                return

            # Log meaningful search events
            user_id = g.userobj.id if g.userobj else None

            action._log_event(
                event_type="search_query",
                user_id=user_id,
                event_data={
                    "query": query,
                    "sort": search_params.get("sort"),
                    "facet_fields": search_params.get("facet.field", []),
                    "results_count": search_results.get("count", 0),
                    "filters": {
                        k: v for k, v in search_params.items() if k.startswith("fq")
                    },
                },
            )

            # Performance monitoring
            elapsed = time.time() - start_time
            if elapsed > 0.05:  # 50ms warning threshold
                log.warning(
                    f"Analytics after_search took {elapsed:.3f}s - performance issue!"
                )

        except Exception as e:
            log.error(f"Analytics error in after_search: {e}")
            # Never let analytics break core functionality
            pass

    # IResourceController - Track resource activities
    def before_resource_create(self, context, resource):
        """Called before a resource is created"""
        # No specific analytics needed for resource creation - just ensure compatibility
        pass

    def after_resource_create(self, context, resource):
        """Called after a resource is created"""
        try:
            # Log resource creation event
            user_id = context.get('user')
            dataset_id = resource.get('package_id')
            
            action._log_event(
                event_type="resource_create",
                dataset_id=dataset_id,
                resource_id=resource.get('id'),
                user_id=user_id,
                event_data={
                    "resource_name": resource.get('name'),
                    "resource_format": resource.get('format'),
                    "resource_size": resource.get('size'),
                    "resource_url": resource.get('url')
                }
            )
        except Exception as e:
            log.error(f"Error logging resource creation analytics: {e}")

    def before_resource_update(self, context, current, resource):
        """Called before a resource is updated"""
        # No specific analytics needed for resource update preparation
        pass

    def after_resource_update(self, context, resource):
        """Called after a resource is updated"""
        try:
            # Log resource update event
            user_id = context.get('user')
            dataset_id = resource.get('package_id')
            
            action._log_event(
                event_type="resource_update",
                dataset_id=dataset_id,
                resource_id=resource.get('id'),
                user_id=user_id,
                event_data={
                    "resource_name": resource.get('name'),
                    "resource_format": resource.get('format'),
                    "resource_size": resource.get('size')
                }
            )
        except Exception as e:
            log.error(f"Error logging resource update analytics: {e}")

    def before_resource_delete(self, context, resource, resources):
        """Called before a resource is deleted"""
        # No specific analytics needed for resource delete preparation
        pass

    def after_resource_delete(self, context, resources):
        """Called after resources are deleted"""
        try:
            # Log resource deletion event for each deleted resource
            user_id = context.get('user')
            
            for resource in resources:
                action._log_event(
                    event_type="resource_delete",
                    dataset_id=resource.get('package_id'),
                    resource_id=resource.get('id'),
                    user_id=user_id,
                    event_data={
                        "resource_name": resource.get('name'),
                        "resource_format": resource.get('format')
                    }
                )
        except Exception as e:
            log.error(f"Error logging resource deletion analytics: {e}")

    def before_download(self, context, resource, filename):
        """Called before a resource is downloaded"""
        try:
            action.resource_download_with_analytics(context, {"id": resource["id"]})
        except Exception as e:
            log.error(f"Error logging resource download analytics: {e}")

        # Don't modify the download process
        return

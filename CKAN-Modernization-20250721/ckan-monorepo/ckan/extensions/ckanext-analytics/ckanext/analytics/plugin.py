import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging

import ckanext.analytics.cli as cli
import ckanext.analytics.views as views
from ckanext.analytics.logic import action

log = logging.getLogger(__name__)


class AnalyticsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IResourceController)
    plugins.implements(plugins.IBlueprint)
    

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "analytics")

    # IActions - Override core actions to add analytics
    def get_actions(self):
        return action.get_actions()

    # IClick - Add CLI commands
    def get_commands(self):
        return cli.get_commands()

    # IBlueprint - Add web dashboard
    def get_blueprint(self):
        return views.get_blueprints()

    # IResourceController - Track resource downloads
    def before_download(self, context, resource, filename):
        """Called before a resource is downloaded"""
        try:
            action.resource_download_with_analytics(context, {'id': resource['id']})
        except Exception as e:
            log.error(f"Error logging resource download analytics: {e}")
        
        # Don't modify the download process
        return

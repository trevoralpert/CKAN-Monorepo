from flask import Blueprint
from ckanext.search_enhanced.controller import SearchEnhancedController

def get_blueprints():
    """Return a list of blueprints to be registered by the app."""
    
    # Create a blueprint
    blueprint = Blueprint(
        'search_enhanced',
        __name__,
        url_prefix='/api'
    )
    
    # Add routes
    blueprint.add_url_rule(
        '/search/suggestions',
        'search_suggestions',
        SearchEnhancedController().search_suggestions,
        methods=['GET']
    )
    
    blueprint.add_url_rule(
        '/dataset/<id>/related',
        'related_datasets', 
        SearchEnhancedController().related_datasets,
        methods=['GET']
    )
    
    return [blueprint]

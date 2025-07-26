# Fix for get_blueprint method
import logging
from flask import Blueprint

log = logging.getLogger(__name__)

def get_blueprint_implementation():
    """Return Flask blueprint for search enhanced features"""
    
    blueprint = Blueprint(
        'search_enhanced', 
        __name__,
        url_prefix='/api'
    )
    
    # Import here to avoid circular imports
    from ckanext.search_enhanced.controller import SearchEnhancedController
    controller = SearchEnhancedController()
    
    # Add routes
    blueprint.add_url_rule(
        '/search/suggestions',
        'search_suggestions',
        controller.search_suggestions,
        methods=['GET']
    )
    
    blueprint.add_url_rule(
        '/dataset/<id>/related',
        'related_datasets',
        controller.related_datasets, 
        methods=['GET']
    )
    
    return [blueprint]

import logging
from collections import OrderedDict
from typing import Dict, Any, List, Optional

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.plugins.interfaces import IFacets, IPackageController, IRoutes
from ckan.common import config
from ckan import model
from ckan.lib.helpers import url_for

log = logging.getLogger(__name__)


class SearchEnhancedPlugin(plugins.SingletonPlugin):
    """
    Advanced Search & Discovery enhancements for CKAN Phase 3
    
    Features:
    - City-specific faceted search (department, update frequency, geographic coverage)
    - Related datasets recommendations based on analytics and similarity  
    - Search analytics integration for improved relevance
    - Enhanced search UI components
    """
    
    plugins.implements(IFacets)
    plugins.implements(IPackageController, inherit=True)
    plugins.implements(IRoutes, inherit=True)

    # IFacets Interface Implementation
    def dataset_facets(self, facets_dict: Dict[str, str], package_type: str) -> Dict[str, str]:
        """
        Add custom facets for city dataset metadata
        
        Leverages Phase 2 metadata schema to provide faceted search on:
        - City Department
        - Update Frequency  
        - Geographic Coverage
        - Data Quality Assessment
        - Public Access Level
        """
        # Start with existing facets
        new_facets = OrderedDict()
        
        # Add organization first (most important for cities)
        if 'organization' in facets_dict:
            new_facets['organization'] = facets_dict['organization']
        
        # Add city-specific facets from Phase 2 schema
        new_facets['extras_department'] = toolkit._('Department')
        new_facets['extras_update_frequency'] = toolkit._('Update Frequency')
        new_facets['extras_geographic_coverage'] = toolkit._('Geographic Coverage')
        new_facets['extras_public_access_level'] = toolkit._('Access Level')
        new_facets['extras_data_quality_assessment'] = toolkit._('Data Quality')
        
        # Add standard facets
        if 'tags' in facets_dict:
            new_facets['tags'] = facets_dict['tags']
        if 'res_format' in facets_dict:
            new_facets['res_format'] = facets_dict['res_format']
        if 'license_id' in facets_dict:
            new_facets['license_id'] = facets_dict['license_id']
            
        # Add any remaining facets
        for key, value in facets_dict.items():
            if key not in new_facets:
                new_facets[key] = value
                
        log.debug(f"Enhanced facets for {package_type}: {list(new_facets.keys())}")
        return new_facets

    def group_facets(self, facets_dict: Dict[str, str], group_type: str, package_type: str) -> Dict[str, str]:
        """Add enhanced facets to group pages"""
        return self.dataset_facets(facets_dict, package_type)

    def organization_facets(self, facets_dict: Dict[str, str], organization_type: str, package_type: str) -> Dict[str, str]:
        """Add enhanced facets to organization pages"""
        return self.dataset_facets(facets_dict, package_type)

    # IPackageController Interface Implementation
    def before_dataset_index(self, search_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance dataset before Solr indexing with city metadata and analytics
        
        Maps Phase 2 schema fields to specific Solr fields for better faceting
        """
        try:
            from ckanext.search_enhanced.solr_enhancements import enhance_dataset_for_indexing
            return enhance_dataset_for_indexing(search_data)
        except Exception as e:
            log.error(f"Error enhancing dataset for indexing: {e}")
            return search_data

    def after_dataset_show(self, context: Dict[str, Any], pkg_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance package display with related datasets
        
        Uses analytics data and similarity scoring to find related datasets
        """
        try:
            # Get related datasets based on:
            # 1. Same department
            # 2. Similar tags
            # 3. Analytics data (users who viewed this also viewed...)
            related_datasets = self._get_related_datasets(pkg_dict)
            pkg_dict['related_datasets'] = related_datasets
            
        except Exception as e:
            log.warning(f"Error getting related datasets for {pkg_dict.get('name', '')}: {e}")
            pkg_dict['related_datasets'] = []
            
        return pkg_dict

    def after_dataset_search(self, search_results: Dict[str, Any], search_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance search results with analytics-driven improvements
        
        - Boost popular datasets based on analytics
        - Add search suggestions for zero-result queries
        - Track search patterns for continuous improvement
        """
        try:
            # Enhance results with popularity data from analytics
            if 'results' in search_results:
                search_results['results'] = self._enhance_results_with_analytics(
                    search_results['results']
                )
            
            # Add search suggestions for low-result queries
            if search_results.get('count', 0) < 3:
                search_results['search_suggestions'] = self._get_search_suggestions(
                    search_params.get('q', '')
                )
                
        except Exception as e:
            log.warning(f"Error enhancing search results: {e}")
            
        return search_results

    # IRoutes Interface Implementation  
    def before_map(self, map):
        """Add custom routes for enhanced search features"""
        map.connect(
            'search_suggestions',
            '/api/search/suggestions',
            controller='ckanext.search_enhanced.controller:SearchEnhancedController',
            action='search_suggestions'
        )
        map.connect(
            'related_datasets',
            '/api/dataset/{id}/related',
            controller='ckanext.search_enhanced.controller:SearchEnhancedController', 
            action='related_datasets'
        )
        return map

    # Helper Methods
    def _get_related_datasets(self, pkg_dict: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find related datasets using multiple similarity factors
        
        Scoring based on:
        1. Same department (high weight)
        2. Shared tags (medium weight)
        3. Analytics co-viewing patterns (medium weight)
        4. Same organization (low weight)
        """
        try:
            current_id = pkg_dict.get('id')
            if not current_id:
                return []
                
            # Get department for department-based similarity
            current_dept = None
            for extra in pkg_dict.get('extras', []):
                if extra.get('key') == 'department':
                    current_dept = extra.get('value')
                    break
                    
            # Get current tags
            current_tags = set(tag.get('name', '') for tag in pkg_dict.get('tags', []))
            current_org = pkg_dict.get('organization', {}).get('id')
            
            # Query for potential related datasets
            search_dict = {
                'q': '*:*',
                'fq': f'-id:{current_id}',  # Exclude current dataset
                'rows': 50,  # Get more to score and filter
                'include_private': False
            }
            
            # Add department filter if available (high relevance)
            if current_dept:
                search_dict['fq'] += f' +extras_department:"{current_dept}"'
                
            context = {'user': toolkit.c.user, 'ignore_auth': True}
            search_results = toolkit.get_action('package_search')(context, search_dict)
            
            # Score and rank results
            scored_results = []
            for dataset in search_results.get('results', []):
                score = self._calculate_similarity_score(
                    dataset, current_tags, current_dept, current_org, current_id
                )
                if score > 0:
                    dataset['similarity_score'] = score
                    scored_results.append(dataset)
                    
            # Sort by score and return top results
            scored_results.sort(key=lambda x: x['similarity_score'], reverse=True)
            return scored_results[:limit]
            
        except Exception as e:
            log.error(f"Error calculating related datasets: {e}")
            return []

    def _calculate_similarity_score(self, dataset: Dict[str, Any], current_tags: set, 
                                   current_dept: str, current_org: str, current_id: str) -> float:
        """Calculate similarity score between datasets"""
        score = 0.0
        
        try:
            # Department similarity (high weight: 0.4)
            dataset_dept = None
            for extra in dataset.get('extras', []):
                if extra.get('key') == 'department':
                    dataset_dept = extra.get('value')
                    break
                    
            if dataset_dept and current_dept and dataset_dept == current_dept:
                score += 0.4
                
            # Tag similarity (medium weight: 0.3)
            dataset_tags = set(tag.get('name', '') for tag in dataset.get('tags', []))
            if current_tags and dataset_tags:
                tag_intersection = len(current_tags & dataset_tags)
                tag_union = len(current_tags | dataset_tags)
                if tag_union > 0:
                    tag_similarity = tag_intersection / tag_union
                    score += 0.3 * tag_similarity
                    
            # Organization similarity (low weight: 0.1)  
            dataset_org = dataset.get('organization', {}).get('id')
            if dataset_org and current_org and dataset_org == current_org:
                score += 0.1
                
            # Analytics-based similarity (medium weight: 0.2)
            # TODO: Implement analytics co-viewing patterns
            analytics_score = self._get_analytics_similarity(current_id, dataset.get('id'))
            score += 0.2 * analytics_score
            
        except Exception as e:
            log.warning(f"Error calculating similarity for dataset {dataset.get('id', '')}: {e}")
            
        return score

    def _get_analytics_similarity(self, dataset1_id: str, dataset2_id: str) -> float:
        """
        Calculate analytics-based similarity (users who viewed X also viewed Y)
        
        Returns score 0.0-1.0 based on co-viewing patterns from Phase 1 analytics
        """
        try:
            # Import analytics model from Phase 1
            from ckanext.analytics.models import AnalyticsEvent
            
            # Get users who viewed dataset1
            viewers1 = model.Session.query(AnalyticsEvent.session_hash).filter(
                AnalyticsEvent.event_type == 'dataset_view',
                AnalyticsEvent.dataset_id == dataset1_id
            ).distinct().all()
            
            # Get users who viewed dataset2  
            viewers2 = model.Session.query(AnalyticsEvent.session_hash).filter(
                AnalyticsEvent.event_type == 'dataset_view',
                AnalyticsEvent.dataset_id == dataset2_id
            ).distinct().all()
            
            if not viewers1 or not viewers2:
                return 0.0
                
            # Calculate Jaccard similarity of viewer sets
            set1 = set(v[0] for v in viewers1)
            set2 = set(v[0] for v in viewers2)
            
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            log.debug(f"Analytics similarity calculation failed: {e}")
            return 0.0

    def _enhance_results_with_analytics(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance search results with analytics data
        
        Adds view counts and popularity indicators from Phase 1 analytics
        """
        try:
            from ckanext.analytics.models import AnalyticsEvent
            
            for dataset in results:
                dataset_id = dataset.get('id')
                if dataset_id:
                    # Get view count from last 30 days
                    view_count = model.Session.query(AnalyticsEvent).filter(
                        AnalyticsEvent.event_type == 'dataset_view',
                        AnalyticsEvent.dataset_id == dataset_id,
                        AnalyticsEvent.timestamp >= model.Session.query(
                            model.func.now() - model.text("interval '30 days'")
                        ).scalar()
                    ).count()
                    
                    dataset['analytics_views_30d'] = view_count
                    dataset['analytics_popularity'] = 'high' if view_count > 50 else 'medium' if view_count > 10 else 'low'
                    
        except Exception as e:
            log.debug(f"Analytics enhancement failed: {e}")
            
        return results

    def _get_search_suggestions(self, query: str) -> List[str]:
        """
        Generate search suggestions for low-result queries
        
        Uses analytics data to suggest popular search terms
        """
        try:
            if not query or len(query) < 2:
                return []
                
            from ckanext.analytics.models import AnalyticsEvent
            
            # Get popular search terms that contain the query
            suggestions = model.Session.query(
                AnalyticsEvent.event_data['query'].astext
            ).filter(
                AnalyticsEvent.event_type == 'search_query',
                AnalyticsEvent.event_data['query'].astext.ilike(f'%{query}%'),
                AnalyticsEvent.event_data['query'].astext != query
            ).distinct().limit(5).all()
            
            return [sugg[0] for sugg in suggestions if sugg[0]]
            
        except Exception as e:
            log.debug(f"Search suggestions failed: {e}")
            return [] 
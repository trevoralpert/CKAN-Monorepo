import logging
from collections import OrderedDict
from typing import Dict, Any, List, Optional

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.plugins.interfaces import IFacets, IPackageController, IBlueprint
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

    # IFacets Interface Implementation
    def dataset_facets(
        self, facets_dict: Dict[str, str], package_type: str
    ) -> Dict[str, str]:
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
        if "organization" in facets_dict:
            new_facets["organization"] = facets_dict["organization"]

        # Add city-specific facets from Phase 2 schema
        new_facets["extras_department"] = toolkit._("Department")
        new_facets["extras_update_frequency"] = toolkit._("Update Frequency")
        new_facets["extras_geographic_coverage"] = toolkit._("Geographic Coverage")
        new_facets["extras_public_access_level"] = toolkit._("Access Level")
        new_facets["extras_data_quality_assessment"] = toolkit._("Data Quality")

        # Add standard facets
        if "tags" in facets_dict:
            new_facets["tags"] = facets_dict["tags"]
        if "res_format" in facets_dict:
            new_facets["res_format"] = facets_dict["res_format"]
        if "license_id" in facets_dict:
            new_facets["license_id"] = facets_dict["license_id"]

        # Add any remaining facets
        for key, value in facets_dict.items():
            if key not in new_facets:
                new_facets[key] = value

        log.debug(f"Enhanced facets for {package_type}: {list(new_facets.keys())}")
        return new_facets

    def group_facets(
        self, facets_dict: Dict[str, str], group_type: str, package_type: str
    ) -> Dict[str, str]:
        """Add enhanced facets to group pages"""
        return self.dataset_facets(facets_dict, package_type)

    def organization_facets(
        self, facets_dict: Dict[str, str], organization_type: str, package_type: str
    ) -> Dict[str, str]:
        """Add enhanced facets to organization pages"""
        return self.dataset_facets(facets_dict, package_type)

    # IPackageController Interface Implementation
    def before_dataset_index(self, search_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance dataset before Solr indexing with city metadata and analytics

        Maps Phase 2 schema fields to specific Solr fields for better faceting
        """
        try:
            from ckanext.search_enhanced.solr_enhancements import (
                enhance_dataset_for_indexing,
            )

            return enhance_dataset_for_indexing(search_data)
        except Exception as e:
            log.error(f"Error enhancing dataset for indexing: {e}")
            return search_data

    def after_dataset_show(
        self, context: Dict[str, Any], pkg_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
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
            pkg_dict["related_datasets"] = related_datasets

        except Exception as e:
            log.warning(
                f"Error getting related datasets for {pkg_dict.get('name', '')}: {e}"
            )
            pkg_dict["related_datasets"] = []

        return pkg_dict

    def after_dataset_search(
        self, search_results: Dict[str, Any], search_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhance search results with analytics-driven improvements

        - Boost popular datasets based on analytics
        - Add search suggestions for zero-result queries
        - Track search patterns for continuous improvement
        """
        try:
            # Enhance results with popularity data from analytics
            if "results" in search_results:
                search_results["results"] = self._enhance_results_with_analytics(
                    search_results["results"]
                )

            # Add search suggestions for low-result queries
            if search_results.get("count", 0) < 3:
                search_results["search_suggestions"] = self._get_search_suggestions(
                    search_params.get("q", "")
                )

        except Exception as e:
            log.warning(f"Error enhancing search results: {e}")

        return search_results

    # IRoutes Interface Implementation

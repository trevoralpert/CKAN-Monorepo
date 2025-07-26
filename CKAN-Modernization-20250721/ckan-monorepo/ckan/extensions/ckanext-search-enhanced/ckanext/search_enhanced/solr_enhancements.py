"""
Solr Schema Enhancements for Phase 3 Search Improvements

This module provides utilities to enhance the existing CKAN Solr schema
with city-specific metadata fields for better faceting and search.
"""

import logging
from typing import Dict, Any, List

log = logging.getLogger(__name__)


class SolrSchemaEnhancer:
    """
    Utility class for enhancing CKAN's Solr schema with Phase 2 metadata fields

    Adds specific fields for:
    - Department faceting
    - Update frequency filtering
    - Geographic coverage search
    - Data quality indicators
    - Public access levels
    """

    @staticmethod
    def get_enhanced_fields() -> Dict[str, Dict[str, Any]]:
        """
        Define enhanced Solr fields for city metadata

        Returns field definitions that can be added to schema.xml
        or configured via Solr's schema API
        """
        return {
            # City Department field for faceting
            "department": {
                "type": "string",
                "indexed": True,
                "stored": True,
                "multiValued": False,
                "copyTo": ["text"],  # Include in full-text search
            },
            # Update frequency for filtering
            "update_frequency": {
                "type": "string",
                "indexed": True,
                "stored": True,
                "multiValued": False,
            },
            # Geographic coverage for spatial filtering
            "geographic_coverage": {
                "type": "string",
                "indexed": True,
                "stored": True,
                "multiValued": False,
            },
            # Data quality assessment for filtering
            "data_quality_assessment": {
                "type": "string",
                "indexed": True,
                "stored": True,
                "multiValued": False,
            },
            # Public access level for security filtering
            "public_access_level": {
                "type": "string",
                "indexed": True,
                "stored": True,
                "multiValued": False,
            },
            # Contact email (searchable but not faceted)
            "contact_email": {
                "type": "string",
                "indexed": True,
                "stored": True,
                "multiValued": False,
            },
            # Last updated date for temporal filtering
            "last_updated": {
                "type": "date",
                "indexed": True,
                "stored": True,
                "multiValued": False,
            },
            # Collection method for methodology filtering
            "collection_method": {
                "type": "string",
                "indexed": True,
                "stored": True,
                "multiValued": False,
            },
            # Analytics-driven fields
            "popularity_score": {
                "type": "float",
                "indexed": True,
                "stored": True,
                "multiValued": False,
                "default": 0.0,
            },
            "view_count_30d": {
                "type": "int",
                "indexed": True,
                "stored": True,
                "multiValued": False,
                "default": 0,
            },
        }

    @staticmethod
    def get_copy_field_mappings() -> List[Dict[str, str]]:
        """
        Define copy field mappings for enhanced search

        Copy fields allow multiple fields to be searched together
        """
        return [
            {"source": "department", "dest": "text"},
            {"source": "update_frequency", "dest": "text"},
            {"source": "geographic_coverage", "dest": "text"},
            {"source": "data_quality_assessment", "dest": "text"},
            {"source": "collection_method", "dest": "text"},
        ]

    @staticmethod
    def get_field_boosting_config() -> Dict[str, float]:
        """
        Define field boosting for relevance scoring

        Higher values = more important in search ranking
        """
        return {
            "title": 3.0,  # Highest priority
            "department": 2.5,  # High priority for city data
            "tags": 2.0,  # Important for categorization
            "notes": 1.5,  # Medium priority
            "organization": 1.2,  # Slightly boosted
            "res_name": 1.0,  # Standard priority
            "text": 0.8,  # Lower priority catch-all
        }

    @staticmethod
    def generate_schema_xml_snippet() -> str:
        """
        Generate XML snippet to add to schema.xml

        Can be used to manually update Solr schema
        """
        fields = SolrSchemaEnhancer.get_enhanced_fields()
        copy_fields = SolrSchemaEnhancer.get_copy_field_mappings()

        xml_parts = []
        xml_parts.append("<!-- Phase 3 Search Enhancement Fields -->")

        # Add field definitions
        for field_name, field_config in fields.items():
            field_type = field_config["type"]
            indexed = str(field_config.get("indexed", True)).lower()
            stored = str(field_config.get("stored", True)).lower()
            multi_valued = str(field_config.get("multiValued", False)).lower()

            xml_parts.append(
                f'<field name="{field_name}" type="{field_type}" '
                f'indexed="{indexed}" stored="{stored}" multiValued="{multi_valued}"/>'
            )

        # Add copy field mappings
        xml_parts.append("\n<!-- Phase 3 Copy Field Mappings -->")
        for mapping in copy_fields:
            xml_parts.append(
                f'<copyField source="{mapping["source"]}" dest="{mapping["dest"]}"/>'
            )

        return "\n".join(xml_parts)

    @staticmethod
    def map_ckan_field_to_solr(dataset_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map CKAN dataset fields to enhanced Solr fields

        Extracts city metadata from CKAN extras and maps to specific Solr fields
        """
        solr_doc = {}
        extras = {
            extra["key"]: extra["value"] for extra in dataset_dict.get("extras", [])
        }

        # Map city-specific fields
        field_mappings = {
            "department": "department",
            "update_frequency": "update_frequency",
            "geographic_coverage": "geographic_coverage",
            "data_quality_assessment": "data_quality_assessment",
            "public_access_level": "public_access_level",
            "contact_email": "contact_email",
            "last_updated": "last_updated",
            "collection_method": "collection_method",
        }

        for ckan_field, solr_field in field_mappings.items():
            if ckan_field in extras and extras[ckan_field]:
                solr_doc[solr_field] = extras[ckan_field]

        return solr_doc


def enhance_dataset_for_indexing(dataset_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hook function to enhance dataset before Solr indexing

    This can be called from IPackageController.before_dataset_index()
    """
    try:
        # Add city-specific field mappings
        enhanced_fields = SolrSchemaEnhancer.map_ckan_field_to_solr(dataset_dict)
        dataset_dict.update(enhanced_fields)

        # Add analytics-driven fields (if analytics extension is available)
        try:
            from ckanext.analytics.models import AnalyticsEvent
            from ckan import model
            import datetime

            dataset_id = dataset_dict.get("id")
            if dataset_id:
                # Calculate 30-day view count
                thirty_days_ago = datetime.datetime.utcnow() - datetime.timedelta(
                    days=30
                )
                view_count = (
                    model.Session.query(AnalyticsEvent)
                    .filter(
                        AnalyticsEvent.event_type == "dataset_view",
                        AnalyticsEvent.dataset_id == dataset_id,
                        AnalyticsEvent.timestamp >= thirty_days_ago,
                    )
                    .count()
                )

                dataset_dict["view_count_30d"] = view_count

                # Simple popularity score (can be enhanced with more sophisticated algorithms)
                download_count = (
                    model.Session.query(AnalyticsEvent)
                    .filter(
                        AnalyticsEvent.event_type == "resource_download",
                        AnalyticsEvent.dataset_id == dataset_id,
                        AnalyticsEvent.timestamp >= thirty_days_ago,
                    )
                    .count()
                )

                # Weighted popularity score: views + (downloads * 2)
                popularity_score = view_count + (download_count * 2)
                dataset_dict["popularity_score"] = float(popularity_score)

        except Exception as e:
            log.debug(
                f"Analytics enhancement failed for dataset {dataset_dict.get('name', '')}: {e}"
            )
            dataset_dict["view_count_30d"] = 0
            dataset_dict["popularity_score"] = 0.0

        log.debug(f"Enhanced dataset {dataset_dict.get('name', '')} for indexing")

    except Exception as e:
        log.error(f"Error enhancing dataset for indexing: {e}")

    return dataset_dict

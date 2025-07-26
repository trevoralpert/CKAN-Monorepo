"""
Tests for Phase 3 Search Enhanced Plugin

Tests the core functionality including:
- Facet enhancements
- Related datasets calculation
- Analytics integration
- API endpoints
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from collections import OrderedDict

from ckanext.search_enhanced.plugin import SearchEnhancedPlugin
from ckanext.search_enhanced.solr_enhancements import (
    SolrSchemaEnhancer,
    enhance_dataset_for_indexing,
)


class TestSearchEnhancedPlugin:
    """Test the main SearchEnhancedPlugin functionality"""

    def setup_method(self):
        self.plugin = SearchEnhancedPlugin()

    def test_dataset_facets_includes_city_fields(self):
        """Test that city-specific facets are added to the facets dict"""
        original_facets = OrderedDict(
            [
                ("organization", "Organizations"),
                ("tags", "Tags"),
                ("res_format", "Formats"),
            ]
        )

        enhanced_facets = self.plugin.dataset_facets(original_facets, "dataset")

        # Check that city-specific facets are present
        assert "extras_department" in enhanced_facets
        assert "extras_update_frequency" in enhanced_facets
        assert "extras_geographic_coverage" in enhanced_facets
        assert enhanced_facets["extras_department"] == "Department"

        # Check that original facets are preserved
        assert "organization" in enhanced_facets
        assert "tags" in enhanced_facets
        assert "res_format" in enhanced_facets

    def test_facets_order_prioritizes_organization_and_department(self):
        """Test that organization and department appear first in facets"""
        original_facets = OrderedDict(
            [
                ("tags", "Tags"),
                ("organization", "Organizations"),
                ("res_format", "Formats"),
            ]
        )

        enhanced_facets = self.plugin.dataset_facets(original_facets, "dataset")
        facet_keys = list(enhanced_facets.keys())

        # Organization should be first, department second
        assert facet_keys[0] == "organization"
        assert facet_keys[1] == "extras_department"

    def test_calculate_similarity_score_department_matching(self):
        """Test similarity scoring with department matching"""
        current_tags = {"fire", "safety", "emergency"}
        current_dept = "fire"
        current_org = "city-org-1"
        current_id = "dataset-1"

        # Mock dataset with same department
        dataset = {
            "id": "dataset-2",
            "extras": [{"key": "department", "value": "fire"}],
            "tags": [{"name": "fire"}, {"name": "response"}],
            "organization": {"id": "city-org-1"},
        }

        score = self.plugin._calculate_similarity_score(
            dataset, current_tags, current_dept, current_org, current_id
        )

        # Should get high score for department match (0.4) + some tag overlap + org match (0.1)
        assert score > 0.5  # Department + org + some tag similarity
        assert score <= 1.0

    def test_calculate_similarity_score_no_matches(self):
        """Test similarity scoring with no matches"""
        current_tags = {"water", "utilities"}
        current_dept = "water"
        current_org = "city-org-1"
        current_id = "dataset-1"

        # Mock dataset with different department, tags, org
        dataset = {
            "id": "dataset-2",
            "extras": [{"key": "department", "value": "fire"}],
            "tags": [{"name": "emergency"}, {"name": "response"}],
            "organization": {"id": "city-org-2"},
        }

        score = self.plugin._calculate_similarity_score(
            dataset, current_tags, current_dept, current_org, current_id
        )

        # Should get very low score (only analytics similarity if any)
        assert score >= 0.0
        assert score <= 0.2  # Max analytics score

    @patch("ckanext.search_enhanced.plugin.toolkit")
    def test_get_related_datasets_with_department_filter(self, mock_toolkit):
        """Test that related datasets search filters by department"""
        # Mock package dict
        pkg_dict = {
            "id": "test-dataset",
            "extras": [{"key": "department", "value": "fire"}],
            "tags": [{"name": "emergency"}],
            "organization": {"id": "org-1"},
        }

        # Mock search results
        mock_search_results = {
            "results": [
                {
                    "id": "related-1",
                    "name": "fire-stations",
                    "title": "Fire Station Locations",
                    "extras": [{"key": "department", "value": "fire"}],
                    "tags": [{"name": "emergency"}, {"name": "locations"}],
                    "organization": {"id": "org-1"},
                }
            ]
        }

        mock_toolkit.get_action.return_value.return_value = mock_search_results
        mock_toolkit.c.user = "test-user"

        related = self.plugin._get_related_datasets(pkg_dict)

        # Should find related datasets
        assert len(related) > 0
        assert related[0]["id"] == "related-1"
        assert "similarity_score" in related[0]

        # Check that search was called with department filter
        search_call = mock_toolkit.get_action.return_value.call_args[0][1]
        assert '+extras_department:"fire"' in search_call["fq"]


class TestSolrSchemaEnhancer:
    """Test Solr schema enhancement utilities"""

    def test_get_enhanced_fields_includes_city_fields(self):
        """Test that enhanced fields include all city metadata fields"""
        fields = SolrSchemaEnhancer.get_enhanced_fields()

        expected_fields = [
            "department",
            "update_frequency",
            "geographic_coverage",
            "data_quality_assessment",
            "public_access_level",
            "contact_email",
            "last_updated",
            "collection_method",
            "popularity_score",
            "view_count_30d",
        ]

        for field in expected_fields:
            assert field in fields
            assert fields[field]["indexed"] is True
            assert fields[field]["stored"] is True

    def test_map_ckan_field_to_solr(self):
        """Test mapping CKAN dataset to Solr document"""
        dataset = {
            "id": "test-dataset",
            "title": "Test Dataset",
            "extras": [
                {"key": "department", "value": "fire"},
                {"key": "update_frequency", "value": "weekly"},
                {"key": "geographic_coverage", "value": "citywide"},
                {"key": "irrelevant_field", "value": "should_be_ignored"},
            ],
        }

        solr_doc = SolrSchemaEnhancer.map_ckan_field_to_solr(dataset)

        assert solr_doc["department"] == "fire"
        assert solr_doc["update_frequency"] == "weekly"
        assert solr_doc["geographic_coverage"] == "citywide"
        assert "irrelevant_field" not in solr_doc

    def test_generate_schema_xml_snippet(self):
        """Test XML schema snippet generation"""
        xml_snippet = SolrSchemaEnhancer.generate_schema_xml_snippet()

        # Should contain field definitions
        assert '<field name="department"' in xml_snippet
        assert 'type="string"' in xml_snippet
        assert 'indexed="true"' in xml_snippet

        # Should contain copy field mappings
        assert '<copyField source="department" dest="text"/>' in xml_snippet

    def test_field_boosting_config(self):
        """Test field boosting configuration"""
        boosting = SolrSchemaEnhancer.get_field_boosting_config()

        # Title should have highest boost
        assert boosting["title"] > boosting["department"]
        assert boosting["department"] > boosting["tags"]
        assert sum(boosting.values()) > 10  # Reasonable total boosting


class TestEnhanceDatasetForIndexing:
    """Test the dataset enhancement function"""

    def test_enhance_dataset_with_city_fields(self):
        """Test that city fields are properly extracted"""
        dataset = {
            "id": "test-dataset",
            "title": "Test Dataset",
            "extras": [
                {"key": "department", "value": "fire"},
                {"key": "update_frequency", "value": "daily"},
            ],
        }

        enhanced = enhance_dataset_for_indexing(dataset.copy())

        assert enhanced["department"] == "fire"
        assert enhanced["update_frequency"] == "daily"
        # Should have analytics fields even if they're zero
        assert "view_count_30d" in enhanced
        assert "popularity_score" in enhanced

    def test_enhance_dataset_handles_missing_analytics(self):
        """Test that enhancement works without analytics extension"""
        dataset = {"id": "test-dataset", "title": "Test Dataset", "extras": []}

        enhanced = enhance_dataset_for_indexing(dataset.copy())

        # Should have default analytics values
        assert enhanced["view_count_30d"] == 0
        assert enhanced["popularity_score"] == 0.0

    @patch("ckanext.search_enhanced.solr_enhancements.model")
    @patch("ckanext.analytics.models.AnalyticsEvent")
    def test_enhance_dataset_with_analytics(self, mock_analytics_event, mock_model):
        """Test analytics integration in dataset enhancement"""
        # Mock analytics data
        mock_model.Session.query.return_value.filter.return_value.count.return_value = (
            25
        )

        dataset = {"id": "test-dataset", "title": "Test Dataset", "extras": []}

        enhanced = enhance_dataset_for_indexing(dataset.copy())

        # Should calculate popularity score from views and downloads
        assert enhanced["view_count_30d"] == 25
        assert enhanced["popularity_score"] > 0


class TestSearchEnhancedController:
    """Test API controller endpoints"""

    def test_search_suggestions_endpoint(self):
        """Test search suggestions API endpoint"""
        from ckanext.search_enhanced.controller import SearchEnhancedController

        controller = SearchEnhancedController()

        # Mock request parameters
        with patch("ckanext.search_enhanced.controller.toolkit") as mock_toolkit:
            mock_toolkit.request.params.get.return_value = "fire"

            # Mock analytics suggestions
            with patch.object(
                controller, "_get_analytics_suggestions"
            ) as mock_analytics:
                with patch.object(
                    controller, "_get_autocomplete_suggestions"
                ) as mock_autocomplete:
                    mock_analytics.return_value = ["fire department", "fire safety"]
                    mock_autocomplete.return_value = [
                        {"title": "Fire Stats", "name": "fire-stats"}
                    ]

                    with patch.object(controller, "_return_json") as mock_return:
                        controller.search_suggestions()

                        # Should call _return_json with proper structure
                        call_args = mock_return.call_args[0][0]
                        assert "suggestions" in call_args
                        assert "autocomplete" in call_args
                        assert call_args["query"] == "fire"


if __name__ == "__main__":
    pytest.main([__file__])

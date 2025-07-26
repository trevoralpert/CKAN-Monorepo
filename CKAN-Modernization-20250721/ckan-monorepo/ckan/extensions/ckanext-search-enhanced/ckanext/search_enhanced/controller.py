import logging
import json
from typing import Dict, Any, List

from ckan.controllers.api import ApiController
import ckan.plugins.toolkit as toolkit
from ckan.common import response
from ckan import model


log = logging.getLogger(__name__)


class SearchEnhancedController(ApiController):
    """
    API Controller for Phase 3 Search Enhancement Features

    Provides endpoints for:
    - Search suggestions and autocomplete
    - Related datasets API
    - Enhanced search analytics
    """

    def search_suggestions(self):
        """
        GET /api/search/suggestions?q=<query>

        Returns search suggestions based on analytics and popular terms
        """
        try:
            query = toolkit.request.params.get("q", "").strip()

            if not query or len(query) < 2:
                return self._return_json({"suggestions": []})

            # Get suggestions from analytics data
            suggestions = self._get_analytics_suggestions(query)

            # Add autocomplete from existing dataset titles/names
            autocomplete = self._get_autocomplete_suggestions(query)

            result = {
                "suggestions": suggestions,
                "autocomplete": autocomplete,
                "query": query,
            }

            return self._return_json(result)

        except Exception as e:
            log.error(f"Error in search_suggestions: {e}")
            return self._return_json({"error": "Internal server error"}, status=500)

    def related_datasets(self):
        """
        GET /api/dataset/{id}/related

        Returns related datasets for a given dataset ID
        """
        try:
            dataset_id = toolkit.request.urlvars.get("id")
            if not dataset_id:
                return self._return_json({"error": "Dataset ID required"}, status=400)

            # Get the dataset
            context = {"user": toolkit.c.user, "ignore_auth": True}
            try:
                pkg_dict = toolkit.get_action("package_show")(
                    context, {"id": dataset_id}
                )
            except toolkit.ObjectNotFound:
                return self._return_json({"error": "Dataset not found"}, status=404)

            # Calculate related datasets
            related = self._calculate_related_datasets(pkg_dict)

            result = {
                "dataset_id": dataset_id,
                "related_datasets": related,
                "count": len(related),
            }

            return self._return_json(result)

        except Exception as e:
            log.error(f"Error in related_datasets: {e}")
            return self._return_json({"error": "Internal server error"}, status=500)

    def _get_analytics_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """Get search suggestions from analytics data"""
        try:
            from ckanext.analytics.models import AnalyticsEvent

            # Get popular search terms that start with or contain the query
            suggestions = (
                model.Session.query(
                    AnalyticsEvent.event_data["query"].astext,
                    model.func.count(AnalyticsEvent.id).label("frequency"),
                )
                .filter(
                    AnalyticsEvent.event_type == "search_query",
                    AnalyticsEvent.event_data["query"].astext.ilike(f"%{query}%"),
                    AnalyticsEvent.event_data["query"].astext != query,
                    AnalyticsEvent.event_data["query"].astext.isnot(None),
                )
                .group_by(AnalyticsEvent.event_data["query"].astext)
                .order_by(model.desc("frequency"))
                .limit(limit)
                .all()
            )

            return [
                sugg[0] for sugg in suggestions if sugg[0] and len(sugg[0]) > len(query)
            ]

        except Exception as e:
            log.debug(f"Analytics suggestions failed: {e}")
            return []

    def _get_autocomplete_suggestions(
        self, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get autocomplete suggestions from dataset titles and names"""
        try:
            context = {"user": toolkit.c.user, "ignore_auth": True}

            # Search for datasets matching the query
            search_dict = {
                "q": f"title:*{query}* OR name:*{query}*",
                "rows": limit,
                "include_private": False,
            }

            search_results = toolkit.get_action("package_search")(context, search_dict)

            autocomplete = []
            for dataset in search_results.get("results", []):
                autocomplete.append(
                    {
                        "id": dataset.get("id"),
                        "name": dataset.get("name"),
                        "title": dataset.get("title"),
                        "url": toolkit.url_for("dataset.read", id=dataset.get("name")),
                    }
                )

            return autocomplete

        except Exception as e:
            log.debug(f"Autocomplete suggestions failed: {e}")
            return []

    def _calculate_related_datasets(
        self, pkg_dict: Dict[str, Any], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Calculate related datasets (reuse logic from plugin)"""
        try:
            # Import the plugin to reuse the logic
            from ckanext.search_enhanced.plugin import SearchEnhancedPlugin

            plugin = SearchEnhancedPlugin()

            related = plugin._get_related_datasets(pkg_dict, limit)

            # Simplify the response for API
            api_response = []
            for dataset in related:
                api_response.append(
                    {
                        "id": dataset.get("id"),
                        "name": dataset.get("name"),
                        "title": dataset.get("title"),
                        "notes": dataset.get("notes", "")[:200] + "..."
                        if len(dataset.get("notes", "")) > 200
                        else dataset.get("notes", ""),
                        "organization": dataset.get("organization", {}).get("title"),
                        "similarity_score": dataset.get("similarity_score", 0),
                        "url": toolkit.url_for("dataset.read", id=dataset.get("name")),
                    }
                )

            return api_response

        except Exception as e:
            log.error(f"Error calculating related datasets: {e}")
            return []

    def _return_json(self, data: Dict[str, Any], status: int = 200) -> str:
        """Helper to return JSON response"""
        response.status_int = status
        response.content_type = "application/json"
        return json.dumps(data, indent=2)

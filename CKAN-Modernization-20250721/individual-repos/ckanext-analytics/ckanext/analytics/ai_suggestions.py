#!/usr/bin/env python3
"""
AI-Assisted Metadata Suggestion System

Provides intelligent suggestions for improving dataset metadata quality
using configurable Large Language Model providers.
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod

import requests
from ckan.common import config
import ckan.plugins.toolkit as toolkit

log = logging.getLogger(__name__)


class AIProvider(ABC):
    """Abstract base class for AI suggestion providers"""
    
    @abstractmethod
    def suggest_tags(self, title: str, description: str, existing_tags: List[str] = None) -> List[str]:
        """Suggest relevant tags for a dataset"""
        pass
    
    @abstractmethod
    def suggest_department(self, title: str, description: str) -> Tuple[str, float]:
        """Suggest department category with confidence score"""
        pass
    
    @abstractmethod
    def improve_title(self, title: str, description: str) -> str:
        """Suggest an improved title"""
        pass
    
    @abstractmethod
    def enhance_description(self, title: str, description: str) -> str:
        """Suggest an enhanced description"""
        pass
    
    @abstractmethod
    def assess_quality(self, dataset_dict: Dict) -> Dict[str, any]:
        """Assess overall dataset quality and suggest improvements"""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI-based suggestion provider"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
        if not self.api_key:
            log.warning("OpenAI API key not configured. AI suggestions will be limited.")
    
    def _make_request(self, messages: List[Dict], max_tokens: int = 150) -> Optional[str]:
        """Make request to OpenAI API"""
        if not self.api_key:
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            log.error(f"OpenAI API error: {e}")
            return None
    
    def suggest_tags(self, title: str, description: str, existing_tags: List[str] = None) -> List[str]:
        """Suggest relevant tags using OpenAI"""
        existing_str = f"Existing tags: {', '.join(existing_tags)}" if existing_tags else "No existing tags."
        
        messages = [
            {
                "role": "system",
                "content": "You are a data librarian helping with city government dataset tagging. Suggest 3-5 relevant, specific tags that help citizens find this dataset. Focus on: department, data type, topic, and use case. Return only a comma-separated list."
            },
            {
                "role": "user", 
                "content": f"Dataset Title: {title}\n\nDescription: {description}\n\n{existing_str}\n\nSuggest better tags:"
            }
        ]
        
        response = self._make_request(messages)
        if response:
            # Parse comma-separated tags
            tags = [tag.strip().lower() for tag in response.split(',')]
            # Filter out existing tags and clean up
            if existing_tags:
                existing_lower = [t.lower() for t in existing_tags]
                tags = [t for t in tags if t not in existing_lower]
            return [t for t in tags if t and len(t) > 2][:5]
        
        return []
    
    def suggest_department(self, title: str, description: str) -> Tuple[str, float]:
        """Suggest department category with confidence"""
        departments = [
            "fire", "police", "public-works", "finance", "parks-recreation",
            "planning-zoning", "water-utilities", "health", "transportation", 
            "mayor-admin", "other"
        ]
        
        dept_list = ", ".join(departments)
        messages = [
            {
                "role": "system",
                "content": f"You are a city government data analyst. Classify datasets by department. Available departments: {dept_list}. Respond with just the department name and confidence (0-1) like: 'fire,0.85'"
            },
            {
                "role": "user",
                "content": f"Title: {title}\n\nDescription: {description}\n\nWhich department?"
            }
        ]
        
        response = self._make_request(messages, max_tokens=50)
        if response:
            try:
                parts = response.split(',')
                dept = parts[0].strip().lower()
                confidence = float(parts[1].strip()) if len(parts) > 1 else 0.7
                
                if dept in departments:
                    return dept, confidence
            except:
                pass
        
        return "other", 0.5
    
    def improve_title(self, title: str, description: str) -> str:
        """Suggest improved title"""
        messages = [
            {
                "role": "system",
                "content": "You are a city data editor. Improve dataset titles to be clear, specific, and citizen-friendly. Keep under 80 characters. Focus on what, when, and scope. Return only the improved title."
            },
            {
                "role": "user",
                "content": f"Current Title: {title}\n\nDescription: {description}\n\nImproved title:"
            }
        ]
        
        response = self._make_request(messages, max_tokens=100)
        return response.strip('"') if response else title
    
    def enhance_description(self, title: str, description: str) -> str:
        """Suggest enhanced description"""
        messages = [
            {
                "role": "system",
                "content": "You are a city data editor. Enhance dataset descriptions to be clear and helpful for citizens. Include: what the data contains, how it's collected, update frequency, and how citizens can use it. Keep under 300 words."
            },
            {
                "role": "user",
                "content": f"Title: {title}\n\nCurrent Description: {description}\n\nEnhanced description:"
            }
        ]
        
        response = self._make_request(messages, max_tokens=250)
        return response.strip('"') if response and len(response) > len(description) else description
    
    def assess_quality(self, dataset_dict: Dict) -> Dict[str, any]:
        """Assess dataset quality and suggest improvements"""
        title = dataset_dict.get('title', '')
        description = dataset_dict.get('notes', '')
        tags = [t['name'] for t in dataset_dict.get('tags', [])]
        
        messages = [
            {
                "role": "system", 
                "content": "You are a data quality expert for city government. Assess dataset quality and suggest 2-3 specific improvements. Return JSON format: {\"score\": 0-100, \"issues\": [\"issue1\", \"issue2\"], \"improvements\": [\"improvement1\", \"improvement2\"]}"
            },
            {
                "role": "user",
                "content": f"Title: {title}\nDescription: {description}\nTags: {', '.join(tags)}\n\nAssess quality:"
            }
        ]
        
        response = self._make_request(messages, max_tokens=200)
        if response:
            try:
                return json.loads(response)
            except:
                pass
        
        return {"score": 70, "issues": ["Could not analyze"], "improvements": ["Manual review needed"]}


class MockAIProvider(AIProvider):
    """Mock provider for testing when no API key is available"""
    
    def suggest_tags(self, title: str, description: str, existing_tags: List[str] = None) -> List[str]:
        """Generate mock tag suggestions based on keywords"""
        text = f"{title} {description}".lower()
        
        # Simple keyword-based suggestions
        suggestions = []
        keywords = {
            'fire': ['fire-safety', 'emergency-response'],
            'police': ['public-safety', 'law-enforcement'], 
            'water': ['utilities', 'infrastructure'],
            'park': ['recreation', 'public-spaces'],
            'budget': ['finance', 'municipal-budget'],
            'traffic': ['transportation', 'traffic-data'],
            'health': ['public-health', 'community-health']
        }
        
        for keyword, tags in keywords.items():
            if keyword in text:
                suggestions.extend(tags)
        
        # Add generic suggestions
        if 'report' in text:
            suggestions.append('reports')
        if 'annual' in text:
            suggestions.append('annual-data')
        if 'monthly' in text:
            suggestions.append('monthly-data')
        
        # Filter existing tags
        if existing_tags:
            existing_lower = [t.lower() for t in existing_tags]
            suggestions = [s for s in suggestions if s not in existing_lower]
        
        return suggestions[:3]
    
    def suggest_department(self, title: str, description: str) -> Tuple[str, float]:
        """Simple department suggestion based on keywords"""
        text = f"{title} {description}".lower()
        
        dept_keywords = {
            'fire': ['fire', 'emergency', 'rescue', 'ems'],
            'police': ['police', 'crime', 'enforcement', 'safety'],
            'public-works': ['road', 'street', 'maintenance', 'infrastructure'],
            'finance': ['budget', 'finance', 'revenue', 'expenditure'],
            'parks-recreation': ['park', 'recreation', 'sports', 'playground'],
            'water-utilities': ['water', 'sewer', 'utility', 'drainage'],
            'health': ['health', 'medical', 'disease', 'clinic'],
            'transportation': ['traffic', 'transport', 'transit', 'vehicle'],
            'planning-zoning': ['zoning', 'planning', 'development', 'permit']
        }
        
        best_match = 'other'
        best_score = 0.3
        
        for dept, keywords in dept_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > best_score:
                best_match = dept
                best_score = min(0.8, score * 0.2 + 0.4)  # Cap at 0.8 for mock
        
        return best_match, best_score
    
    def improve_title(self, title: str, description: str) -> str:
        """Basic title improvement suggestions"""
        if len(title) < 20:
            return f"{title} - City Data"
        return title
    
    def enhance_description(self, title: str, description: str) -> str:
        """Basic description enhancement"""
        if len(description) < 50:
            return f"{description}\n\nThis dataset is maintained by the City and updated regularly for public access."
        return description
    
    def assess_quality(self, dataset_dict: Dict) -> Dict[str, any]:    
        """Mock quality assessment"""
        issues = []
        score = 80
        
        if not dataset_dict.get('notes') or len(dataset_dict.get('notes', '')) < 50:
            issues.append("Description too short")
            score -= 15
            
        if not dataset_dict.get('tags'):
            issues.append("No tags provided")  
            score -= 10
        
        improvements = []
        if issues:
            improvements = ["Add more detailed description", "Include relevant tags", "Specify update frequency"]
        
        return {
            "score": max(score, 30),
            "issues": issues,
            "improvements": improvements[:2]
        }


class AISuggestionService:
    """Main service for AI-powered metadata suggestions"""
    
    def __init__(self):
        self.provider = self._initialize_provider()
        self.suggestion_stats = {
            'suggestions_made': 0,
            'suggestions_accepted': 0,
            'by_type': {
                'tags': {'made': 0, 'accepted': 0},
                'department': {'made': 0, 'accepted': 0},
                'title': {'made': 0, 'accepted': 0},
                'description': {'made': 0, 'accepted': 0}
            }
        }
    
    def _initialize_provider(self) -> AIProvider:
        """Initialize the appropriate AI provider based on configuration"""
        provider_type = config.get('ckanext.analytics.ai_provider', 'mock').lower()
        
        if provider_type == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                log.info("Initializing OpenAI provider for AI suggestions")
                return OpenAIProvider(api_key)
            else:
                log.warning("OpenAI provider requested but no API key found. Using mock provider.")
                return MockAIProvider()
        else:
            log.info("Using mock AI provider for suggestions")
            return MockAIProvider()
    
    def get_comprehensive_suggestions(self, dataset_dict: Dict) -> Dict[str, any]:
        """Get comprehensive suggestions for a dataset"""
        title = dataset_dict.get('title', '')
        description = dataset_dict.get('notes', '')
        existing_tags = [t['name'] for t in dataset_dict.get('tags', [])]
        
        suggestions = {
            'dataset_id': dataset_dict.get('id'),
            'timestamp': datetime.now().isoformat(),
            'suggestions': {}
        }
        
        try:
            # Tag suggestions
            tag_suggestions = self.provider.suggest_tags(title, description, existing_tags)
            if tag_suggestions:
                suggestions['suggestions']['tags'] = {
                    'current': existing_tags,
                    'suggested': tag_suggestions,
                    'confidence': 0.8
                }
                self.suggestion_stats['by_type']['tags']['made'] += 1
            
            # Department suggestion
            dept_suggestion, confidence = self.provider.suggest_department(title, description)
            current_dept = dataset_dict.get('department')
            if dept_suggestion != current_dept:
                suggestions['suggestions']['department'] = {
                    'current': current_dept,
                    'suggested': dept_suggestion,
                    'confidence': confidence
                }
                self.suggestion_stats['by_type']['department']['made'] += 1
            
            # Title improvement
            title_suggestion = self.provider.improve_title(title, description)
            if title_suggestion != title and len(title_suggestion) > 0:
                suggestions['suggestions']['title'] = {
                    'current': title,
                    'suggested': title_suggestion,
                    'confidence': 0.7
                }
                self.suggestion_stats['by_type']['title']['made'] += 1
            
            # Description enhancement  
            desc_suggestion = self.provider.enhance_description(title, description)
            if desc_suggestion != description and len(desc_suggestion) > len(description):
                suggestions['suggestions']['description'] = {
                    'current': description,
                    'suggested': desc_suggestion,
                    'confidence': 0.6
                }
                self.suggestion_stats['by_type']['description']['made'] += 1
            
            # Overall quality assessment
            quality_assessment = self.provider.assess_quality(dataset_dict)
            suggestions['quality_assessment'] = quality_assessment
            
            self.suggestion_stats['suggestions_made'] += 1
            
        except Exception as e:
            log.error(f"Error generating suggestions: {e}")
            suggestions['error'] = str(e)
        
        return suggestions
    
    def accept_suggestion(self, dataset_id: str, suggestion_type: str, suggestion_data: Dict):
        """Record that a suggestion was accepted"""
        try:
            if suggestion_type in self.suggestion_stats['by_type']:
                self.suggestion_stats['by_type'][suggestion_type]['accepted'] += 1
                self.suggestion_stats['suggestions_accepted'] += 1
            
            log.info(f"Suggestion accepted: {suggestion_type} for dataset {dataset_id}")
            
        except Exception as e:
            log.error(f"Error recording suggestion acceptance: {e}")
    
    def get_suggestion_stats(self) -> Dict[str, any]:
        """Get suggestion usage statistics"""
        stats = self.suggestion_stats.copy()
        
        # Calculate acceptance rates
        for suggestion_type, type_stats in stats['by_type'].items():
            made = type_stats['made']
            accepted = type_stats['accepted']  
            type_stats['acceptance_rate'] = (accepted / made * 100) if made > 0 else 0
        
        stats['overall_acceptance_rate'] = (
            (stats['suggestions_accepted'] / stats['suggestions_made'] * 100) 
            if stats['suggestions_made'] > 0 else 0
        )
        
        return stats
    
    def batch_suggest_for_datasets(self, dataset_ids: List[str] = None, limit: int = 10) -> List[Dict]:
        """Generate suggestions for multiple datasets"""
        try:
            # Get datasets to process
            if dataset_ids:
                datasets = []
                for dataset_id in dataset_ids:
                    try:
                        context = {'ignore_auth': True}
                        dataset = toolkit.get_action('package_show')(context, {'id': dataset_id})
                        datasets.append(dataset)
                    except:
                        log.warning(f"Could not load dataset {dataset_id}")
            else:
                # Get recent datasets
                context = {'ignore_auth': True}
                search_result = toolkit.get_action('package_search')(
                    context, {'q': '*:*', 'rows': limit, 'sort': 'metadata_modified desc'}
                )
                datasets = search_result.get('results', [])
            
            suggestions_batch = []
            for dataset in datasets:
                suggestions = self.get_comprehensive_suggestions(dataset)
                if suggestions.get('suggestions'):
                    suggestions_batch.append(suggestions) 
            
            return suggestions_batch
            
        except Exception as e:
            log.error(f"Error in batch suggestion generation: {e}")
            return []


# Global service instance
_ai_service = None

def get_ai_service() -> AISuggestionService:
    """Get the global AI suggestion service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AISuggestionService()
    return _ai_service 
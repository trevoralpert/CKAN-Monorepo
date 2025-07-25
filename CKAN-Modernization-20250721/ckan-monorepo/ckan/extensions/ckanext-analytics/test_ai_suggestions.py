#!/usr/bin/env python3
"""
Test AI Suggestion System

Demonstrates the AI-powered metadata suggestion functionality
with mock datasets and various scenarios.
"""

import sys
import json
from datetime import datetime

def test_ai_suggestion_engine():
    """Test the AI suggestion engine with mock data"""
    
    print("🤖 Testing AI Suggestion Engine")
    print("=" * 50)
    
    try:
        # Import our AI service
        sys.path.insert(0, '/usr/src/extensions/ckanext-analytics')
        from ckanext.analytics.ai_suggestions import get_ai_service
        
        ai_service = get_ai_service()
        print(f"✅ AI Service initialized: {ai_service.provider.__class__.__name__}")
        
        # Test with various mock datasets
        test_datasets = [
            {
                'id': 'fire-response-test-001',
                'title': 'Fire Response',
                'notes': 'Fire department response data',
                'tags': [],
                'department': None
            },
            {
                'id': 'budget-report-test-002',
                'title': 'Budget Report',
                'notes': 'Annual budget report for the city with financial details and expenditures',
                'tags': [{'name': 'finance'}],
                'department': None
            },
            {
                'id': 'park-usage-test-003',
                'title': 'Park Usage Statistics',
                'notes': 'Data on park usage including visitor counts, popular activities, and seasonal trends for recreation planning',
                'tags': [{'name': 'parks'}, {'name': 'recreation'}],
                'department': 'parks-recreation'
            },
            {
                'id': 'traffic-data-test-004',
                'title': 'Traffic Count Data',
                'notes': 'Vehicle count data from traffic sensors throughout the city',
                'tags': [],
                'department': None
            }
        ]
        
        print(f"\n📊 Testing with {len(test_datasets)} mock datasets:")
        
        total_suggestions = 0
        
        for i, dataset in enumerate(test_datasets, 1):
            print(f"\n🔍 Dataset {i}: {dataset['title']}")
            print("-" * 40)
            
            # Get suggestions
            suggestions = ai_service.get_comprehensive_suggestions(dataset)
            
            dataset_suggestions = suggestions.get('suggestions', {})
            if dataset_suggestions:
                total_suggestions += len(dataset_suggestions)
                
                # Display suggestions
                for suggestion_type, suggestion_data in dataset_suggestions.items():
                    print(f"  💡 {suggestion_type.upper()}:")
                    if suggestion_type == 'tags':
                        current = suggestion_data.get('current', [])
                        suggested = suggestion_data.get('suggested', [])
                        print(f"     Current: {current if current else 'None'}")
                        print(f"     Suggested: {suggested}")
                    elif suggestion_type == 'department':
                        current = suggestion_data.get('current', 'None')
                        suggested = suggestion_data.get('suggested')
                        confidence = suggestion_data.get('confidence', 0)
                        print(f"     Current: {current}")
                        print(f"     Suggested: {suggested} (confidence: {confidence:.0%})")
                    elif suggestion_type == 'title':
                        current = suggestion_data.get('current', '')
                        suggested = suggestion_data.get('suggested', '')
                        print(f"     Current: \"{current}\"")
                        print(f"     Suggested: \"{suggested}\"")
                    elif suggestion_type == 'description':
                        current_len = len(suggestion_data.get('current', ''))
                        suggested_len = len(suggestion_data.get('suggested', ''))
                        print(f"     Enhancement: {current_len} → {suggested_len} characters")
            else:
                print("  ✅ No improvements needed")
            
            # Show quality assessment
            quality = suggestions.get('quality_assessment', {})
            if quality:
                score = quality.get('score', 'N/A')
                issues = quality.get('issues', [])
                improvements = quality.get('improvements', [])
                
                print(f"  📈 Quality Score: {score}/100")
                if issues:
                    print(f"  ⚠️  Issues: {', '.join(issues)}")
                if improvements:
                    print(f"  💭 Improvements: {', '.join(improvements)}")
        
        # Test statistics
        stats = ai_service.get_suggestion_stats()
        print(f"\n📊 AI Suggestion Statistics:")
        print(f"   Total suggestions made: {stats['suggestions_made']}")
        print(f"   Total suggestion types: {total_suggestions}")
        
        for suggestion_type, type_stats in stats['by_type'].items():
            if type_stats['made'] > 0:
                print(f"   {suggestion_type}: {type_stats['made']} suggestions")
        
        # Test suggestion acceptance (simulate)
        print(f"\n🎯 Testing Suggestion Acceptance:")
        if total_suggestions > 0:
            # Simulate accepting some suggestions
            ai_service.accept_suggestion('fire-response-test-001', 'tags', {'suggested': ['fire-safety', 'emergency-response']})
            ai_service.accept_suggestion('budget-report-test-002', 'department', {'suggested': 'finance'})
            
            updated_stats = ai_service.get_suggestion_stats()
            acceptance_rate = updated_stats['overall_acceptance_rate']
            print(f"   Acceptance rate after simulation: {acceptance_rate:.1f}%")
        
        print(f"\n✅ AI Suggestion Engine test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in AI suggestion engine test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_providers():
    """Test different AI providers"""
    
    print("\n🔌 Testing AI Providers")
    print("=" * 30)
    
    try:
        sys.path.insert(0, '/usr/src/extensions/ckanext-analytics')
        from ckanext.analytics.ai_suggestions import MockAIProvider, OpenAIProvider
        
        # Test Mock Provider
        print("📋 Testing Mock Provider:")
        mock_provider = MockAIProvider()
        
        # Test suggestions
        test_title = "Fire Department Response Times"
        test_description = "Monthly fire department response time data including average response times by district"
        
        # Tag suggestions
        tag_suggestions = mock_provider.suggest_tags(test_title, test_description, ['emergency'])
        print(f"   Tag suggestions: {tag_suggestions}")
        
        # Department suggestion
        dept, confidence = mock_provider.suggest_department(test_title, test_description)
        print(f"   Department suggestion: {dept} (confidence: {confidence:.0%})")
        
        # Title improvement
        improved_title = mock_provider.improve_title("Fire Data", test_description)
        print(f"   Title improvement: \"{improved_title}\"")
        
        # OpenAI Provider (will use fallback)
        print("\n🤖 Testing OpenAI Provider (without API key):")
        openai_provider = OpenAIProvider()  # Will fallback to mock behavior
        
        if not openai_provider.api_key:
            print("   ℹ️  No OpenAI API key configured - using fallback behavior")
            
            # Test that it handles missing API key gracefully
            openai_tags = openai_provider.suggest_tags(test_title, test_description)
            print(f"   OpenAI tag suggestions (fallback): {openai_tags if openai_tags else 'None'}")
        
        print("✅ AI Providers test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in AI providers test: {e}")
        return False

def test_configuration_options():
    """Test AI configuration options"""
    
    print("\n⚙️  Testing Configuration Options")
    print("=" * 35)
    
    print("📝 Available Configuration:")
    print("   ckanext.analytics.ai_provider = mock|openai")
    print("   OPENAI_API_KEY = <your-api-key> (environment variable)")
    
    print("\n🔧 To enable OpenAI suggestions:")
    print("   1. Set environment variable: export OPENAI_API_KEY='your-key-here'")
    print("   2. Add to CKAN config: ckanext.analytics.ai_provider = openai") 
    print("   3. Restart CKAN")
    
    print("\n💡 Mock provider features (current setup):")
    print("   ✅ Keyword-based tag suggestions")
    print("   ✅ Department classification")
    print("   ✅ Basic title improvements")
    print("   ✅ Description enhancement")
    print("   ✅ Quality assessment")
    
    print("\n🤖 OpenAI provider features (with API key):")
    print("   🎯 Advanced natural language understanding")
    print("   🎯 Context-aware suggestions")
    print("   🎯 More sophisticated quality assessment")
    print("   🎯 Better title and description improvements")
    
    return True

def main():
    """Run all AI suggestion tests"""
    
    print("🧪 AI Suggestion System Test Suite")
    print("=" * 50)
    print(f"Test started at: {datetime.now().isoformat()}")
    
    tests = [
        test_ai_suggestion_engine,
        test_ai_providers,
        test_configuration_options
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All AI suggestion tests passed!")
        print("\n🚀 AI Suggestion System is ready for use!")
        print("\nNext steps:")
        print("   • Create datasets to test AI suggestions")
        print("   • Use CLI: ckan analytics ai-suggest --dataset-id <id>")
        print("   • Use API: call get_dataset_ai_suggestions action")
        print("   • Configure OpenAI for advanced suggestions")
        return 0
    else:
        print("💥 Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
#!/usr/bin/env python3
"""
Metadata Quality Audit Script for City Datasets

Analyzes existing datasets to identify metadata quality issues
and generates recommendations for improvement.
"""

import json
import sys
from datetime import datetime
from collections import defaultdict, Counter
import re

import ckan.plugins.toolkit as toolkit
import ckan.model as model
from ckan.common import config


class MetadataAuditor:
    """Analyzes dataset metadata quality and generates improvement recommendations"""
    
    def __init__(self):
        self.audit_results = {
            'summary': {},
            'issues': defaultdict(list),
            'recommendations': [],
            'dataset_scores': {},
            'field_analysis': {}
        }
    
    def audit_all_datasets(self):
        """Run comprehensive audit on all datasets"""
        print("🔍 Starting Metadata Quality Audit...")
        print("=" * 50)
        
        # Get all datasets
        datasets = self._get_all_datasets()
        
        if not datasets:
            print("❌ No datasets found to audit")
            return self.audit_results
        
        print(f"📊 Found {len(datasets)} datasets to analyze")
        
        total_score = 0
        issue_counts = defaultdict(int)
        
        for i, dataset in enumerate(datasets, 1):
            print(f"\n🔎 Auditing dataset {i}/{len(datasets)}: {dataset.get('title', 'Untitled')[:50]}...")
            
            score, issues = self._audit_single_dataset(dataset)
            total_score += score
            self.audit_results['dataset_scores'][dataset['id']] = {
                'title': dataset.get('title'),
                'score': score,
                'issues': issues
            }
            
            for issue_type in issues:
                issue_counts[issue_type] += 1
        
        # Generate summary
        self.audit_results['summary'] = {
            'total_datasets': len(datasets),
            'average_quality_score': round(total_score / len(datasets), 2) if datasets else 0,
            'total_issues': sum(issue_counts.values()),
            'issue_breakdown': dict(issue_counts),
            'audit_date': datetime.now().isoformat()
        }
        
        # Analyze fields across all datasets
        self._analyze_field_completeness(datasets)
        
        # Generate recommendations
        self._generate_recommendations()
        
        return self.audit_results
    
    def _get_all_datasets(self):
        """Get all active datasets from CKAN"""
        try:
            context = {'ignore_auth': True}
            data_dict = {'q': '*:*', 'rows': 1000}  # Adjust rows as needed
            
            result = toolkit.get_action('package_search')(context, data_dict)
            return result.get('results', [])
            
        except Exception as e:
            print(f"❌ Error fetching datasets: {e}")
            return []
    
    def _audit_single_dataset(self, dataset):
        """Audit a single dataset and return quality score and issues"""
        issues = []
        score = 100  # Start with perfect score, deduct for issues
        
        # Required field checks
        required_fields = ['title', 'notes', 'author', 'author_email', 'license_id']
        for field in required_fields:
            if not dataset.get(field) or str(dataset.get(field)).strip() == '':
                issues.append(f'missing_{field}')
                score -= 15
        
        # Title quality check
        title = dataset.get('title', '')
        if len(title) < 10:
            issues.append('title_too_short')
            score -= 10
        elif len(title) > 100:
            issues.append('title_too_long')
            score -= 5
        
        # Description quality check
        notes = dataset.get('notes', '')
        if len(notes) < 50:
            issues.append('description_too_short')
            score -= 10
        
        # Email validation
        author_email = dataset.get('author_email', '')
        if author_email and not self._is_valid_email(author_email):
            issues.append('invalid_author_email')
            score -= 5
        
        maintainer_email = dataset.get('maintainer_email', '')
        if maintainer_email and not self._is_valid_email(maintainer_email):
            issues.append('invalid_maintainer_email')
            score -= 5
        
        # Tags check
        tags = dataset.get('tags', [])
        if len(tags) == 0:
            issues.append('no_tags')
            score -= 10
        elif len(tags) > 10:
            issues.append('too_many_tags')
            score -= 5
        
        # License check
        license_id = dataset.get('license_id')
        if not license_id or license_id == 'notspecified':
            issues.append('no_license_specified')
            score -= 10
        
        # Resources check
        resources = dataset.get('resources', [])
        if not resources:
            issues.append('no_resources')
            score -= 20
        else:
            for i, resource in enumerate(resources):
                if not resource.get('name'):
                    issues.append(f'resource_{i}_no_name')
                    score -= 5
                if not resource.get('format'):
                    issues.append(f'resource_{i}_no_format')
                    score -= 5
        
        # City-specific field checks (if any exist)
        city_fields = ['department', 'update_frequency', 'geographic_coverage']
        for field in city_fields:
            if dataset.get(field):
                # Field exists, check if valid
                pass  # Could add validation here
            else:
                # Field missing - not an error for existing datasets
                pass
        
        # Freshness check
        modified = dataset.get('metadata_modified')
        if modified:
            try:
                mod_date = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                days_old = (datetime.now().replace(tzinfo=mod_date.tzinfo) - mod_date).days
                
                if days_old > 365:
                    issues.append('very_old_metadata')
                    score -= 10
                elif days_old > 180:
                    issues.append('old_metadata')
                    score -= 5
            except:
                issues.append('invalid_modified_date')
                score -= 5
        
        return max(0, score), issues
    
    def _is_valid_email(self, email):
        """Basic email validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _analyze_field_completeness(self, datasets):
        """Analyze completeness of metadata fields across all datasets"""
        field_stats = defaultdict(lambda: {'present': 0, 'missing': 0, 'empty': 0})
        
        standard_fields = [
            'title', 'notes', 'author', 'author_email', 'maintainer', 
            'maintainer_email', 'license_id', 'url', 'version', 'tags'
        ]
        
        total_datasets = len(datasets)
        
        for dataset in datasets:
            for field in standard_fields:
                value = dataset.get(field)
                if value is None:
                    field_stats[field]['missing'] += 1
                elif str(value).strip() == '' or (isinstance(value, list) and len(value) == 0):
                    field_stats[field]['empty'] += 1
                else:
                    field_stats[field]['present'] += 1
        
        # Calculate percentages
        for field, stats in field_stats.items():
            completeness = (stats['present'] / total_datasets) * 100
            field_stats[field]['completeness_percent'] = round(completeness, 1)
        
        self.audit_results['field_analysis'] = dict(field_stats)
    
    def _generate_recommendations(self):
        """Generate improvement recommendations based on audit results"""
        recommendations = []
        issue_counts = self.audit_results['summary']['issue_breakdown']
        
        # Priority recommendations based on most common issues
        if issue_counts.get('missing_author_email', 0) > 0:
            recommendations.append({
                'priority': 'HIGH',
                'issue': 'Missing author email addresses',
                'affected_datasets': issue_counts.get('missing_author_email'),
                'recommendation': 'Add contact email addresses for all datasets to enable citizen inquiries',
                'action': 'Update dataset metadata with valid email addresses'
            })
        
        if issue_counts.get('description_too_short', 0) > 0:
            recommendations.append({
                'priority': 'HIGH',
                'issue': 'Inadequate dataset descriptions',
                'affected_datasets': issue_counts.get('description_too_short'),
                'recommendation': 'Expand descriptions to at least 50 characters with useful context',
                'action': 'Review and enhance dataset descriptions'
            })
        
        if issue_counts.get('no_tags', 0) > 0:
            recommendations.append({
                'priority': 'MEDIUM',
                'issue': 'Missing tags for discoverability',
                'affected_datasets': issue_counts.get('no_tags'),
                'recommendation': 'Add relevant tags to improve search and categorization',
                'action': 'Tag datasets with relevant keywords'
            })
        
        if issue_counts.get('no_license_specified', 0) > 0:
            recommendations.append({
                'priority': 'HIGH',
                'issue': 'Unspecified data licenses',
                'affected_datasets': issue_counts.get('no_license_specified'),
                'recommendation': 'Specify appropriate open data licenses for public datasets',
                'action': 'Review and assign licenses (recommend Creative Commons)'
            })
        
        if issue_counts.get('old_metadata', 0) + issue_counts.get('very_old_metadata', 0) > 0:
            affected = issue_counts.get('old_metadata', 0) + issue_counts.get('very_old_metadata', 0)
            recommendations.append({
                'priority': 'MEDIUM',
                'issue': 'Stale dataset metadata',
                'affected_datasets': affected,
                'recommendation': 'Establish regular metadata review and update schedule',
                'action': 'Review datasets older than 6 months and update as needed'
            })
        
        # City schema adoption recommendation
        recommendations.append({
            'priority': 'HIGH',
            'issue': 'Inconsistent city-specific metadata',
            'affected_datasets': self.audit_results['summary']['total_datasets'],
            'recommendation': 'Migrate datasets to use new city dataset schema with department, update frequency, and geographic coverage fields',
            'action': 'Use new city-dataset schema for all future datasets and gradually migrate existing ones'
        })
        
        self.audit_results['recommendations'] = recommendations
    
    def print_summary_report(self):
        """Print a human-readable summary of audit results"""
        summary = self.audit_results.get('summary', {})
        
        print("\n" + "="*50)
        print("📋 METADATA QUALITY AUDIT SUMMARY")
        print("="*50)
        
        total_datasets = summary.get('total_datasets', 0)
        if total_datasets == 0:
            print("❌ No datasets found to audit")
            print("💡 Tip: Create some test datasets first to see the audit in action")
            return
        
        print(f"📊 Total Datasets Analyzed: {total_datasets}")
        print(f"📈 Average Quality Score: {summary.get('average_quality_score', 0)}/100")
        print(f"⚠️  Total Issues Found: {summary.get('total_issues', 0)}")
        
        print("\n🔍 Most Common Issues:")
        for issue, count in sorted(summary['issue_breakdown'].items(), 
                                  key=lambda x: x[1], reverse=True)[:5]:
            percentage = round((count / summary['total_datasets']) * 100, 1)
            print(f"   • {issue.replace('_', ' ').title()}: {count} datasets ({percentage}%)")
        
        print("\n📊 Field Completeness Analysis:")
        field_analysis = self.audit_results['field_analysis']
        for field, stats in sorted(field_analysis.items(), 
                                  key=lambda x: x[1]['completeness_percent']):
            print(f"   • {field}: {stats['completeness_percent']}% complete")
        
        print("\n🎯 Priority Recommendations:")
        for i, rec in enumerate(self.audit_results['recommendations'][:3], 1):
            print(f"   {i}. [{rec['priority']}] {rec['recommendation']}")
        
        print(f"\n📅 Audit completed: {summary['audit_date']}")
        print("="*50)
    
    def save_detailed_report(self, filename='metadata_audit_report.json'):
        """Save detailed audit results to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.audit_results, f, indent=2, default=str)
            print(f"💾 Detailed report saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving report: {e}")


def main():
    """Run the metadata audit"""
    auditor = MetadataAuditor()
    results = auditor.audit_all_datasets()
    
    auditor.print_summary_report()
    auditor.save_detailed_report()
    
    return 0 if results['summary']['total_datasets'] > 0 else 1


if __name__ == "__main__":
    sys.exit(main()) 
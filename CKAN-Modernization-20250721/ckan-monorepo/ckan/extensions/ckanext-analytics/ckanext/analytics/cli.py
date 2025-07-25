import click
import datetime
from sqlalchemy import func, desc
from ckan.model import Session, Package, Resource, User
from ckanext.analytics.models import AnalyticsEvent, init_db, drop_db

@click.group()
def analytics():
    """Analytics commands."""
    pass

@analytics.command('init-db')
@click.option('--yes', is_flag=True, help='Confirm database initialization.')
def init_db_command(yes):
    """Initialize the analytics database tables."""
    if not yes and not click.confirm("This will create analytics tables. Continue?"):
        return
    init_db()
    click.echo("Analytics tables created successfully.")

@analytics.command('drop-db')
@click.option('--yes', is_flag=True, help='Confirm database drop.')
def drop_db_command(yes):
    """Drop the analytics database tables."""
    if not yes and not click.confirm("This will drop ALL analytics data. Continue?"):
        return
    drop_db()
    click.echo("Analytics tables dropped successfully.")

@analytics.command('stats')
@click.option('--days', default=30, type=int, help='Number of days to look back for statistics.')
def stats_command(days):
    """Display analytics statistics."""
    click.echo("\n📊 Most Popular Datasets (last {} days):".format(days))
    click.echo("--------------------------------------------------")
    
    # Get popular datasets
    popular_datasets = Session.query(
        Package.title, func.count(AnalyticsEvent.dataset_id).label('views')
    ).join(AnalyticsEvent, Package.id == AnalyticsEvent.dataset_id)\
    .filter(AnalyticsEvent.event_type == 'dataset_view')\
    .filter(AnalyticsEvent.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(days=days))\
    .group_by(Package.title)\
    .order_by(desc('views'))\
    .limit(10).all()

    if popular_datasets:
        for title, views in popular_datasets:
            click.echo(f"- {title}: {views} views")
    else:
        click.echo("No dataset views recorded.")

    click.echo("\n🔍 Popular Search Terms (last {} days):".format(days))
    click.echo("--------------------------------------------------")
    
    # Get popular search terms
    popular_search_terms = Session.query(
        AnalyticsEvent.event_data['query'].astext.label('query'), func.count(AnalyticsEvent.id).label('count')
    ).filter(AnalyticsEvent.event_type == 'search_query')\
    .filter(AnalyticsEvent.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(days=days))\
    .group_by(AnalyticsEvent.event_data['query'].astext)\
    .order_by(desc('count'))\
    .limit(10).all()

    if popular_search_terms:
        for query, count in popular_search_terms:
            if query:
                click.echo(f"- '{query}': {count} searches")
    else:
        click.echo("No search queries recorded.")

    click.echo("\n📈 Event Counts (last {} days):".format(days))
    click.echo("--------------------------------------------------")
    
    # Get event counts by type
    event_counts = Session.query(
        AnalyticsEvent.event_type, func.count(AnalyticsEvent.id).label('count')
    ).filter(AnalyticsEvent.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(days=days))\
    .group_by(AnalyticsEvent.event_type)\
    .order_by(desc('count'))\
    .all()

    if event_counts:
        for event_type, count in event_counts:
            click.echo(f"- {event_type}: {count} events")
    else:
        click.echo("No events recorded.")

@analytics.command('health-check')
def health_check_command():
    """Check analytics system health"""
    click.echo('🏥 Checking analytics system health...')
    
    issues = []
    
    # Check database tables
    try:
        count = Session.query(AnalyticsEvent).count()
        click.echo(f'✅ Database: {count} events in analytics_events table')
    except Exception as e:
        issues.append(f'❌ Database: {e}')
    
    # Check Redis connection
    try:
        from ckanext.analytics.cache import get_redis_client
        redis_client = get_redis_client()
        if redis_client:
            redis_client.ping()
            click.echo('✅ Redis: Connection successful')
        else:
            issues.append('⚠️  Redis: Not available (caching disabled)')
    except Exception as e:
        issues.append(f'❌ Redis: {e}')
    
    # Check plugin configuration
    try:
        import ckan.plugins.toolkit as toolkit
        plugins = toolkit.config.get('ckan.plugins', '')
        if isinstance(plugins, str):
            plugins_list = plugins.split()
        else:
            plugins_list = plugins or []
            
        if 'analytics' in plugins_list:
            click.echo('✅ Plugin: analytics plugin is enabled')
        else:
            issues.append('❌ Plugin: analytics plugin not enabled in ckan.plugins')
    except Exception as e:
        issues.append(f'❌ Plugin: {e}')
    
    # Check recent activity
    try:
        recent_count = Session.query(AnalyticsEvent).filter(
            AnalyticsEvent.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(hours=24)
        ).count()
        click.echo(f'📈 Activity: {recent_count} events in last 24 hours')
        
        if recent_count == 0:
            issues.append('⚠️  Activity: No recent events (system may not be capturing data)')
    except Exception as e:
        issues.append(f'❌ Activity: {e}')
    
    # Summary
    if issues:
        click.echo('\n🚨 Issues found:')
        for issue in issues:
            click.echo(f'  {issue}')
    else:
        click.echo('\n🎉 All systems healthy!')
    
    return len(issues) == 0

@analytics.command('benchmark')
@click.option('--events', default=100, type=int, help='Number of events to create for benchmarking')
def benchmark_command(events):
    """Run analytics performance benchmarks"""
    import time
    
    click.echo(f'🏃 Running analytics benchmarks...')
    click.echo(f'Creating {events} test events...')
    
    # Create test events
    start_time = time.time()
    
    test_events = []
    for i in range(events):
        event = AnalyticsEvent(
            event_type='dataset_view' if i % 3 == 0 else 'search_query' if i % 3 == 1 else 'resource_download',
            dataset_id=f'dataset-{i % 10}',
            resource_id=f'resource-{i % 10}' if i % 3 == 2 else None,
            session_hash=f'hash-{i % 20}',
            event_data={'query': f'term-{i % 5}'} if i % 3 == 1 else None,
            timestamp=datetime.datetime.utcnow() - datetime.timedelta(minutes=i % 60)
        )
        test_events.append(event)
    
    # Bulk insert
    Session.bulk_save_objects(test_events)
    Session.commit()
    
    creation_time = time.time() - start_time
    click.echo(f'✅ Created {events} events in {creation_time:.2f}s ({events/creation_time:.0f} events/sec)')
    
    # Test query performance
    start_time = time.time()
    popular = AnalyticsEvent.get_popular_datasets(days=30, limit=10)
    query_time = time.time() - start_time
    
    click.echo(f'📊 Query Results:')
    click.echo(f'  Popular datasets query: {query_time:.3f}s')
    click.echo(f'  Found {len(popular)} popular datasets')
    
    # Clean up test data
    click.echo('🧹 Cleaning up test data...')
    Session.query(AnalyticsEvent).filter(
        AnalyticsEvent.dataset_id.like('dataset-%')
    ).delete(synchronize_session=False)
    Session.commit()
    
    click.echo('✅ Benchmark complete!')

@analytics.command('audit-metadata')
@click.option('--save-report', default='metadata_audit_report.json', 
              help='Filename for detailed audit report')
def audit_metadata_command(save_report):
    """Audit metadata quality of all datasets and generate improvement recommendations."""
    click.echo("🔍 Starting Metadata Quality Audit...")
    
    try:
        from ckanext.analytics.metadata_audit import MetadataAuditor
        
        auditor = MetadataAuditor()
        results = auditor.audit_all_datasets()
        
        # Print summary to console
        auditor.print_summary_report()
        
        # Save detailed report
        if save_report:
            auditor.save_detailed_report(save_report)
        
        # Return status based on results
        total_datasets = results['summary'].get('total_datasets', 0)
        if total_datasets == 0:
            click.echo("❌ No datasets found to audit")
            return 1
        
        avg_score = results['summary'].get('average_quality_score', 0)
        if avg_score < 60:
            click.echo(f"⚠️  Warning: Average quality score ({avg_score}/100) is below recommended threshold")
        
        click.echo("✅ Metadata audit completed successfully!")
        return 0
        
    except Exception as e:
        click.echo(f"❌ Error during metadata audit: {e}")
        return 1

@analytics.command('ai-suggest')
@click.option('--dataset-id', help='Specific dataset ID to get suggestions for')
@click.option('--limit', default=5, help='Maximum number of datasets to process (when no dataset-id specified)')
@click.option('--provider', default='mock', help='AI provider to use (mock, openai)')
@click.option('--show-stats', is_flag=True, help='Show AI suggestion statistics')
def ai_suggest_command(dataset_id, limit, provider, show_stats):
    """Generate AI-powered metadata suggestions for datasets."""
    
    if show_stats:
        try:
            from ckanext.analytics.ai_suggestions import get_ai_service
            ai_service = get_ai_service()
            stats = ai_service.get_suggestion_stats()
            
            click.echo("🤖 AI Suggestion Statistics")
            click.echo("=" * 30)
            click.echo(f"Total suggestions made: {stats['suggestions_made']}")
            click.echo(f"Total suggestions accepted: {stats['suggestions_accepted']}")
            click.echo(f"Overall acceptance rate: {stats['overall_acceptance_rate']:.1f}%")
            
            click.echo("\nBy suggestion type:")
            for suggestion_type, type_stats in stats['by_type'].items():
                acceptance_rate = type_stats['acceptance_rate']
                click.echo(f"  {suggestion_type}: {type_stats['made']} made, {type_stats['accepted']} accepted ({acceptance_rate:.1f}%)")
            
            return 0
            
        except Exception as e:
            click.echo(f"❌ Error getting AI statistics: {e}")
            return 1
    
    click.echo(f"🤖 Generating AI metadata suggestions using {provider} provider...")
    
    try:
        from ckanext.analytics.ai_suggestions import get_ai_service
        ai_service = get_ai_service()
        
        if dataset_id:
            # Get suggestions for specific dataset
            try:
                import ckan.plugins.toolkit as toolkit
                context = {'ignore_auth': True}
                dataset = toolkit.get_action('package_show')(context, {'id': dataset_id})
                
                click.echo(f"\n📊 Dataset: {dataset.get('title', 'Untitled')}")
                click.echo("-" * 50)
                
                suggestions = ai_service.get_comprehensive_suggestions(dataset)
                
                if suggestions.get('suggestions'):
                    _display_suggestions(suggestions['suggestions'])
                else:
                    click.echo("✅ No improvements needed - dataset metadata looks good!")
                
                # Show quality assessment
                quality = suggestions.get('quality_assessment', {})
                if quality:
                    click.echo(f"\n📈 Quality Score: {quality.get('score', 'N/A')}/100")
                    
                    issues = quality.get('issues', [])
                    if issues:
                        click.echo("⚠️  Issues found:")
                        for issue in issues:
                            click.echo(f"   • {issue}")
                    
                    improvements = quality.get('improvements', [])
                    if improvements:
                        click.echo("💡 Suggested improvements:")
                        for improvement in improvements:
                            click.echo(f"   • {improvement}")
                
                return 0
                
            except Exception as e:
                click.echo(f"❌ Error processing dataset {dataset_id}: {e}")
                return 1
        else:
            # Batch processing
            suggestions_batch = ai_service.batch_suggest_for_datasets(limit=limit)
            
            if not suggestions_batch:
                click.echo("❌ No datasets found or no suggestions generated")
                return 1
            
            click.echo(f"✅ Generated suggestions for {len(suggestions_batch)} datasets")
            
            for i, suggestion_set in enumerate(suggestions_batch, 1):
                dataset_id = suggestion_set.get('dataset_id', 'Unknown')
                suggestions = suggestion_set.get('suggestions', {})
                
                click.echo(f"\n📊 Dataset {i}/{len(suggestions_batch)}: {dataset_id}")
                click.echo("-" * 50)
                
                if suggestions:
                    _display_suggestions(suggestions)
                else:
                    click.echo("✅ No improvements needed")
            
            return 0
            
    except Exception as e:
        click.echo(f"❌ Error generating AI suggestions: {e}")
        return 1

def _display_suggestions(suggestions):
    """Helper function to display suggestions in a formatted way"""
    
    if 'tags' in suggestions:
        tag_data = suggestions['tags']
        current = tag_data.get('current', [])
        suggested = tag_data.get('suggested', [])
        confidence = tag_data.get('confidence', 0)
        
        click.echo(f"🏷️  Tags (confidence: {confidence:.0%}):")
        click.echo(f"   Current: {', '.join(current) if current else 'None'}")
        click.echo(f"   Suggested: {', '.join(suggested)}")
    
    if 'department' in suggestions:
        dept_data = suggestions['department']
        current = dept_data.get('current', 'None')
        suggested = dept_data.get('suggested')
        confidence = dept_data.get('confidence', 0)
        
        click.echo(f"🏢 Department (confidence: {confidence:.0%}):")
        click.echo(f"   Current: {current}")
        click.echo(f"   Suggested: {suggested}")
    
    if 'title' in suggestions:
        title_data = suggestions['title']
        current = title_data.get('current', '')[:50] + '...' if len(title_data.get('current', '')) > 50 else title_data.get('current', '')
        suggested = title_data.get('suggested', '')[:50] + '...' if len(title_data.get('suggested', '')) > 50 else title_data.get('suggested', '')
        confidence = title_data.get('confidence', 0)
        
        click.echo(f"📝 Title (confidence: {confidence:.0%}):")
        click.echo(f"   Current: {current}")
        click.echo(f"   Suggested: {suggested}")
    
    if 'description' in suggestions:
        desc_data = suggestions['description']
        current_len = len(desc_data.get('current', ''))
        suggested_len = len(desc_data.get('suggested', ''))
        confidence = desc_data.get('confidence', 0)
        
        click.echo(f"📄 Description (confidence: {confidence:.0%}):")
        click.echo(f"   Current length: {current_len} characters")
        click.echo(f"   Suggested length: {suggested_len} characters")
        if suggested_len > current_len:
            click.echo(f"   📈 Improvement: +{suggested_len - current_len} characters")

@analytics.command('ai-apply')
@click.argument('dataset_id')
@click.option('--suggestion-type', 
              type=click.Choice(['tags', 'department', 'title', 'description', 'all']),
              help='Type of suggestion to apply')
@click.option('--yes', is_flag=True, help='Confirm application without prompting')
def ai_apply_command(dataset_id, suggestion_type, yes):
    """Apply AI suggestions to a dataset."""
    
    try:
        from ckanext.analytics.ai_suggestions import get_ai_service
        import ckan.plugins.toolkit as toolkit
        
        ai_service = get_ai_service()
        context = {'ignore_auth': True}
        
        # Get dataset and suggestions
        dataset = toolkit.get_action('package_show')(context, {'id': dataset_id})
        suggestions = ai_service.get_comprehensive_suggestions(dataset)
        
        available_suggestions = suggestions.get('suggestions', {})
        if not available_suggestions:
            click.echo("❌ No suggestions available for this dataset")
            return 1
        
        click.echo(f"📊 Dataset: {dataset.get('title', 'Untitled')}")
        click.echo(f"Available suggestions: {', '.join(available_suggestions.keys())}")
        
        if suggestion_type == 'all':
            types_to_apply = list(available_suggestions.keys())
        elif suggestion_type:
            if suggestion_type not in available_suggestions:
                click.echo(f"❌ No {suggestion_type} suggestion available")
                return 1
            types_to_apply = [suggestion_type]
        else:
            click.echo("❌ Please specify --suggestion-type")
            return 1
        
        # Confirm application
        if not yes:
            click.echo(f"\nAbout to apply {len(types_to_apply)} suggestion(s): {', '.join(types_to_apply)}")
            if not click.confirm("Continue?"):
                click.echo("Cancelled")
                return 0
        
        # Apply suggestions
        applied_count = 0
        for suggestion_type in types_to_apply:
            try:
                suggestion_data = available_suggestions[suggestion_type]
                
                # Use the API to apply the suggestion
                result = toolkit.get_action('accept_ai_suggestion')(context, {
                    'dataset_id': dataset_id,
                    'suggestion_type': suggestion_type,
                    'suggestion_data': suggestion_data,
                    'apply_suggestion': True
                })
                
                click.echo(f"✅ Applied {suggestion_type} suggestion")
                applied_count += 1
                
            except Exception as e:
                click.echo(f"❌ Error applying {suggestion_type}: {e}")
        
        if applied_count > 0:
            click.echo(f"\n🎉 Successfully applied {applied_count} suggestions to dataset!")
        
        return 0
        
    except Exception as e:
        click.echo(f"❌ Error applying AI suggestions: {e}")
        return 1

def get_commands():
    return [analytics]

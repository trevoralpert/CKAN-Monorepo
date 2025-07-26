#!/bin/bash

# Phase 3: Advanced Search & Discovery - Testing Setup Script
# Run this inside the CKAN Docker container

set -e

echo "🎯 Phase 3: Advanced Search & Discovery - Testing Setup"
echo "======================================================="
echo

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}📍 Current location: $(pwd)${NC}"
echo -e "${BLUE}📍 Python version: $(python --version)${NC}"
echo

# Step 1: Navigate to source directory
echo -e "${GREEN}Step 1: Navigating to source directory...${NC}"
cd /usr/src
echo -e "✅ Now in: $(pwd)"
echo

# Step 2: Install Phase 3 search-enhanced extension
echo -e "${GREEN}Step 2: Installing Phase 3 search-enhanced extension...${NC}"
if [ -d "./extensions/ckanext-search-enhanced" ]; then
    pip install -e ./extensions/ckanext-search-enhanced
    echo -e "✅ ckanext-search-enhanced installed"
else
    echo -e "${RED}❌ ckanext-search-enhanced directory not found${NC}"
    echo -e "${YELLOW}Available extensions:${NC}"
    ls -la extensions/ | grep ckanext
    exit 1
fi
echo

# Step 3: Install Phase 1 analytics extension (dependency)
echo -e "${GREEN}Step 3: Installing Phase 1 analytics extension...${NC}"
if [ -d "./extensions/ckanext-analytics" ]; then
    pip install -e ./extensions/ckanext-analytics
    echo -e "✅ ckanext-analytics installed"
else
    echo -e "${RED}❌ ckanext-analytics directory not found${NC}"
    exit 1
fi
echo

# Step 4: Install scheming for Phase 2 metadata
echo -e "${GREEN}Step 4: Installing scheming extension...${NC}"
if [ -d "./extensions/ckanext-scheming" ]; then
    pip install -e ./extensions/ckanext-scheming
    echo -e "✅ ckanext-scheming installed"
else
    echo -e "${YELLOW}⚠️ ckanext-scheming not found, trying to install from PyPI...${NC}"
    pip install ckanext-scheming
fi
echo

# Step 5: Install additional dependencies
echo -e "${GREEN}Step 5: Installing additional dependencies...${NC}"
pip install python-dateutil
pip install pyyaml
pip install redis
echo -e "✅ Additional dependencies installed"
echo

# Step 6: Create test configuration file
echo -e "${GREEN}Step 6: Creating test configuration...${NC}"
cat > test-phase3.ini << 'EOF'
#
# CKAN Phase 3 Testing Configuration
# Generated automatically for testing Advanced Search & Discovery features
#

[DEFAULT]

debug = true

[server:main]
use = egg:gunicorn#main
host = 0.0.0.0
port = 5000
workers = 1
worker_class = gevent
timeout = 30
keepalive = 2

[app:main]
use = egg:ckan
full_stack = true
cache_dir = /tmp/%(ckan.site_id)s/
beaker.session.key = ckan

# Site settings
ckan.site_id = default
ckan.site_url = http://localhost:5001
ckan.site_title = CKAN Phase 3 Testing
ckan.site_logo = /base/images/ckan-logo.png
ckan.site_description = Testing Advanced Search & Discovery Features

# Database settings
sqlalchemy.url = postgresql://ckan_default:pass@ckan-postgres/ckan_test
ckan.datastore.write_url = postgresql://ckan_default:pass@ckan-postgres/ckan_test
ckan.datastore.read_url = postgresql://ckan_default:pass@ckan-postgres/ckan_test

# Redis settings
ckan.redis.url = redis://ckan-redis:6379/0

# Search settings
solr_url = http://ckan-solr:8983/solr/ckan
ckan.search.solr_allowed_query_parsers = field

# File storage
ckan.storage_path = /var/lib/ckan

# Extensions - THIS IS THE KEY PART FOR PHASE 3 TESTING
ckan.plugins = datastore datapusher analytics search_enhanced scheming_datasets

# Phase 1: Analytics settings
ckanext.analytics.enable_debug = true
ckanext.analytics.track_api = true

# Phase 2: Scheming settings
scheming.dataset_schemas = ckanext.analytics:city_dataset_schema.yaml
scheming.presets = ckanext.scheming:presets.json

# Phase 3: Search Enhanced settings
ckanext.search_enhanced.related_datasets.limit = 5
ckanext.search_enhanced.suggestions.enabled = true
ckanext.search_enhanced.analytics.enabled = true
ckanext.search_enhanced.similarity.department_weight = 0.4
ckanext.search_enhanced.similarity.tags_weight = 0.3
ckanext.search_enhanced.similarity.analytics_weight = 0.2
ckanext.search_enhanced.similarity.organization_weight = 0.1

# Authorization settings
ckan.auth.anon_create_dataset = false
ckan.auth.create_unowned_dataset = false
ckan.auth.create_dataset_if_not_in_organization = false
ckan.auth.user_create_organizations = false
ckan.auth.user_create_groups = false
ckan.auth.user_delete_groups = false
ckan.auth.user_delete_organizations = false

# Logging configuration
[loggers]
keys = root, ckan, ckanext, sqlalchemy

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARNING
handlers = console

[logger_ckan]
level = INFO
handlers = console
qualname = ckan
propagate = 0

[logger_ckanext]
level = DEBUG
handlers = console
qualname = ckanext
propagate = 0

[logger_sqlalchemy]
level = WARNING
handlers = console
qualname = sqlalchemy.engine
propagate = 0

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(asctime)s %(levelname)-5.5s [%(name)s] %(message)s
EOF

echo -e "✅ test-phase3.ini created"
echo

# Step 7: Initialize databases
echo -e "${GREEN}Step 7: Initializing databases...${NC}"
echo -e "${YELLOW}Waiting for PostgreSQL to be ready...${NC}"
sleep 5

echo -e "Initializing CKAN database..."
ckan -c test-phase3.ini db init
echo -e "✅ CKAN database initialized"

echo -e "Initializing analytics database (Phase 1)..."
ckan -c test-phase3.ini analytics init-db
echo -e "✅ Analytics database initialized"
echo

# Step 8: Create sample data for testing
echo -e "${GREEN}Step 8: Creating sample test data...${NC}"

# Create admin user
echo -e "Creating admin user..."
ckan -c test-phase3.ini user add admin \
    email=admin@test.com \
    password=testpass123 \
    fullname="Test Admin"

# Make admin a sysadmin
ckan -c test-phase3.ini sysadmin add admin
echo -e "✅ Admin user created (username: admin, password: testpass123)"

# Create organization
echo -e "Creating test organization..."
ckan -c test-phase3.ini org add fire-dept \
    title="Fire Department" \
    description="Municipal Fire Department"
echo -e "✅ Fire Department organization created"
echo

# Step 9: Initialize search index
echo -e "${GREEN}Step 9: Initializing search index...${NC}"
echo -e "${YELLOW}Waiting for Solr to be ready...${NC}"
sleep 5

ckan -c test-phase3.ini search-index rebuild
echo -e "✅ Search index initialized"
echo

# Step 10: Create sample datasets for Phase 3 testing
echo -e "${GREEN}Step 10: Creating sample datasets for testing...${NC}"

# We'll create these via Python script since they need Phase 2 schema
python3 << 'PYTHON_EOF'
import ckan.lib.cli as cli
import ckan.model as model
from ckan.lib.helpers import url_for
import ckan.logic as logic
import datetime

# Initialize CKAN
cli.load_config('test-phase3.ini')
model.repo.init_db()

# Create context and data for datasets
context = {'user': 'admin', 'ignore_auth': True}

# Sample datasets with Phase 2 city schema metadata
datasets = [
    {
        'name': 'fire-response-times-2024',
        'title': 'Fire Department Response Times 2024',
        'notes': 'Average response times for fire department emergency calls throughout the city in 2024.',
        'owner_org': 'fire-dept',
        'extras': [
            {'key': 'department', 'value': 'fire'},
            {'key': 'update_frequency', 'value': 'monthly'},
            {'key': 'geographic_coverage', 'value': 'citywide'},
            {'key': 'data_quality_assessment', 'value': 'high'},
            {'key': 'public_access_level', 'value': 'public'},
            {'key': 'contact_email', 'value': 'fire@city.gov'},
            {'key': 'collection_method', 'value': 'automated'}
        ],
        'tags': [
            {'name': 'fire'},
            {'name': 'emergency'},
            {'name': 'response-times'},
            {'name': 'safety'}
        ]
    },
    {
        'name': 'fire-station-locations',
        'title': 'Fire Station Locations and Equipment',
        'notes': 'Geographic locations of all fire stations in the city with equipment inventory.',
        'owner_org': 'fire-dept',
        'extras': [
            {'key': 'department', 'value': 'fire'},
            {'key': 'update_frequency', 'value': 'quarterly'},
            {'key': 'geographic_coverage', 'value': 'citywide'},
            {'key': 'data_quality_assessment', 'value': 'high'},
            {'key': 'public_access_level', 'value': 'public'},
            {'key': 'contact_email', 'value': 'fire@city.gov'},
            {'key': 'collection_method', 'value': 'manual'}
        ],
        'tags': [
            {'name': 'fire'},
            {'name': 'stations'},
            {'name': 'equipment'},
            {'name': 'locations'}
        ]
    },
    {
        'name': 'building-permits-2024',
        'title': 'Building Permits Issued 2024',
        'notes': 'All building permits issued by the city in 2024, including residential and commercial.',
        'owner_org': 'fire-dept',
        'extras': [
            {'key': 'department', 'value': 'planning-zoning'},
            {'key': 'update_frequency', 'value': 'weekly'},
            {'key': 'geographic_coverage', 'value': 'citywide'},
            {'key': 'data_quality_assessment', 'value': 'medium'},
            {'key': 'public_access_level', 'value': 'public'},
            {'key': 'contact_email', 'value': 'planning@city.gov'},
            {'key': 'collection_method', 'value': 'automated'}
        ],
        'tags': [
            {'name': 'permits'},
            {'name': 'building'},
            {'name': 'construction'},
            {'name': 'zoning'}
        ]
    }
]

# Create the datasets
for dataset_data in datasets:
    try:
        dataset = logic.get_action('package_create')(context, dataset_data)
        print(f"✅ Created dataset: {dataset['title']}")
    except Exception as e:
        print(f"❌ Error creating dataset {dataset_data['name']}: {e}")

print("✅ Sample datasets created")
PYTHON_EOF

echo -e "✅ Sample datasets created for testing"
echo

# Final success message
echo -e "${GREEN}🎉 Phase 3 Testing Setup Complete!${NC}"
echo -e "${GREEN}====================================${NC}"
echo
echo -e "${BLUE}📋 Setup Summary:${NC}"
echo -e "   ✅ Extensions installed (analytics, search-enhanced, scheming)"
echo -e "   ✅ Configuration created (test-phase3.ini)"
echo -e "   ✅ Databases initialized"
echo -e "   ✅ Admin user created (admin/testpass123)"
echo -e "   ✅ Sample data created"
echo -e "   ✅ Search index ready"
echo
echo -e "${YELLOW}🚀 Ready to test! Next steps:${NC}"
echo -e "   1. Start CKAN: ckan -c test-phase3.ini run --host 0.0.0.0 --port 5000"
echo -e "   2. Open browser: http://localhost:5001"
echo -e "   3. Login with: admin / testpass123"
echo
echo -e "${BLUE}🧪 Phase 3 Features to Test:${NC}"
echo -e "   🏛️ City-specific faceted search at /dataset"
echo -e "   🔗 Related datasets on dataset pages"
echo -e "   📊 Search suggestions API at /api/search/suggestions?q=fire"
echo -e "   ⚡ Enhanced search with analytics integration"
echo
echo -e "${GREEN}Happy testing! 🎯${NC}" 
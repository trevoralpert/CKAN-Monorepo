#!/bin/bash

# Create updated script with all 42 repositories
cat > clone_individual_repos_updated.sh << 'SCRIPT_EOF'
#!/bin/bash

# CKAN Modernization Project - Clone Individual Repos Script
# This script clones your forked repositories into individual-repos/ directory

set -e

echo "🚀 CKAN Modernization - Clone Individual Repositories"
echo "====================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get GitHub username
GITHUB_USER=$(gh api user --jq .login)

if [ -z "$GITHUB_USER" ]; then
    echo -e "${RED}❌ Could not determine GitHub username${NC}"
    exit 1
fi

echo -e "${GREEN}✅ GitHub user: $GITHUB_USER${NC}"

# Complete list of repositories (42 total)
REPO_NAMES=(
    "ckan"
    "ckanext-archiver"
    "ckanext-basiccharts"
    "ckanext-canada"
    "ckanext-charts"
    "ckanext-cloudstorage"
    "ckanext-dashboard"
    "ckanext-datagovau"
    "ckanext-datagovuk"
    "ckanext-datajson"
    "ckanext-dcat"
    "ckanext-dcatapit"
    "ckanext-dgu"
    "ckanext-disqus"
    "ckanext-doi"
    "ckanext-envvars"
    "ckanext-fluent"
    "ckanext-ga-report"
    "ckanext-geodatagov"
    "ckanext-geoview"
    "ckanext-googleanalytics"
    "ckanext-harvest"
    "ckanext-hierarchy"
    "ckanext-iati"
    "ckanext-issues"
    "ckanext-ldap"
    "ckanext-mapviews"
    "ckanext-metrics_dashboard"
    "ckanext-nhm"
    "ckanext-oauth2"
    "ckanext-odata"
    "ckanext-pages"
    "ckanext-pdfview"
    "ckanext-qa"
    "ckanext-report"
    "ckanext-s3filestore"
    "ckanext-scheming"
    "ckanext-showcase"
    "ckanext-spatial"
    "ckanext-validation"
    "ckanext-versioned-datastore"
    "ckanext-viewhelpers"
    "ckanext-xloader"
)

# Function to get upstream repo URL for a repository
get_upstream_repo() {
    local repo_name=$1
    case $repo_name in
        "ckan") echo "https://github.com/ckan/ckan" ;;
        "ckanext-archiver") echo "https://github.com/ckan/ckanext-archiver" ;;
        "ckanext-basiccharts") echo "https://github.com/ckan/ckanext-basiccharts" ;;
        "ckanext-canada") echo "https://github.com/open-data/ckanext-canada" ;;
        "ckanext-charts") echo "https://github.com/DataShades/ckanext-charts" ;;
        "ckanext-cloudstorage") echo "https://github.com/okfn/ckanext-cloudstorage" ;;
        "ckanext-dashboard") echo "https://github.com/ckan/ckanext-dashboard" ;;
        "ckanext-datagovau") echo "https://github.com/datagovau/ckanext-datagovau" ;;
        "ckanext-datagovuk") echo "https://github.com/alphagov/ckanext-datagovuk" ;;
        "ckanext-datajson") echo "https://github.com/okfn/ckanext-datajson" ;;
        "ckanext-dcat") echo "https://github.com/ckan/ckanext-dcat" ;;
        "ckanext-dcatapit") echo "https://github.com/geosolutions-it/ckanext-dcatapit" ;;
        "ckanext-dgu") echo "https://github.com/datagovuk/ckanext-dgu" ;;
        "ckanext-disqus") echo "https://github.com/ckan/ckanext-disqus" ;;
        "ckanext-doi") echo "https://github.com/okfn/ckanext-doi" ;;
        "ckanext-envvars") echo "https://github.com/ckan/ckanext-envvars" ;;
        "ckanext-fluent") echo "https://github.com/ckan/ckanext-fluent" ;;
        "ckanext-ga-report") echo "https://github.com/datagovau/ckanext-ga-report" ;;
        "ckanext-geodatagov") echo "https://github.com/okfn/ckanext-geodatagov" ;;
        "ckanext-geoview") echo "https://github.com/ckan/ckanext-geoview" ;;
        "ckanext-googleanalytics") echo "https://github.com/ckan/ckanext-googleanalytics" ;;
        "ckanext-harvest") echo "https://github.com/ckan/ckanext-harvest" ;;
        "ckanext-hierarchy") echo "https://github.com/ckan/ckanext-hierarchy" ;;
        "ckanext-iati") echo "https://github.com/IATI/ckanext-iati" ;;
        "ckanext-issues") echo "https://github.com/ckan/ckanext-issues" ;;
        "ckanext-ldap") echo "https://github.com/okfn/ckanext-ldap" ;;
        "ckanext-mapviews") echo "https://github.com/ckan/ckanext-mapviews" ;;
        "ckanext-metrics_dashboard") echo "https://github.com/GSA/ckanext-metrics_dashboard" ;;
        "ckanext-nhm") echo "https://github.com/NaturalHistoryMuseum/ckanext-nhm" ;;
        "ckanext-oauth2") echo "https://github.com/okfn/ckanext-oauth2" ;;
        "ckanext-odata") echo "https://github.com/datagovau/ckanext-odata" ;;
        "ckanext-pages") echo "https://github.com/ckan/ckanext-pages" ;;
        "ckanext-pdfview") echo "https://github.com/ckan/ckanext-pdfview" ;;
        "ckanext-qa") echo "https://github.com/ckan/ckanext-qa" ;;
        "ckanext-report") echo "https://github.com/ckan/ckanext-report" ;;
        "ckanext-s3filestore") echo "https://github.com/okfn/ckanext-s3filestore" ;;
        "ckanext-scheming") echo "https://github.com/ckan/ckanext-scheming" ;;
        "ckanext-showcase") echo "https://github.com/ckan/ckanext-showcase" ;;
        "ckanext-spatial") echo "https://github.com/ckan/ckanext-spatial" ;;
        "ckanext-validation") echo "https://github.com/ckan/ckanext-validation" ;;
        "ckanext-versioned-datastore") echo "https://github.com/NaturalHistoryMuseum/ckanext-versioned-datastore" ;;
        "ckanext-viewhelpers") echo "https://github.com/ckan/ckanext-viewhelpers" ;;
        "ckanext-xloader") echo "https://github.com/ckan/ckanext-xloader" ;;
        *) echo "" ;;
    esac
}

# Function to clone a repository and set up remotes
clone_and_setup_repo() {
    local repo_name=$1
    local upstream_url=$(get_upstream_repo "$repo_name")
    
    if [ -z "$upstream_url" ]; then
        echo -e "${RED}❌ Unknown upstream URL for $repo_name${NC}"
        return 1
    fi
    
    echo "Processing: $repo_name"
    
    if [ -d "$repo_name" ]; then
        echo -e "${YELLOW}⚠️  Directory already exists: $repo_name${NC}"
        cd "$repo_name"
        
        # Check if upstream remote exists
        if git remote get-url upstream >/dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  Upstream remote already exists${NC}"
        else
            echo -e "${BLUE}🔗 Adding upstream remote${NC}"
            git remote add upstream "$upstream_url"
        fi
    else
        echo -e "${BLUE}📥 Cloning fork: $GITHUB_USER/$repo_name${NC}"
        if ! gh repo clone "$GITHUB_USER/$repo_name"; then
            echo -e "${RED}❌ Failed to clone $GITHUB_USER/$repo_name${NC}"
            return 1
        fi
        
        echo -e "${GREEN}✅ Successfully cloned: $repo_name${NC}"
        cd "$repo_name"
        
        echo -e "${BLUE}🔗 Adding upstream remote${NC}"
        git remote add upstream "$upstream_url"
    fi
    
    echo -e "${BLUE}📡 Fetching from upstream...${NC}"
    git fetch upstream
    
    cd ..
    echo
}

# Check GitHub CLI authentication
echo "Checking GitHub CLI authentication..."
if ! gh auth status >/dev/null 2>&1; then
    echo -e "${RED}❌ GitHub CLI authentication failed${NC}"
    echo "Please run: gh auth login"
    exit 1
fi

# Create individual-repos directory if it doesn't exist
INDIVIDUAL_REPOS_DIR="../individual-repos"
mkdir -p "$INDIVIDUAL_REPOS_DIR"
cd "$INDIVIDUAL_REPOS_DIR"

echo "Starting repository cloning process..."
echo "======================================"

# Clone repositories
for repo in "${REPO_NAMES[@]}"; do
    clone_and_setup_repo "$repo"
done

echo "======================================"
echo "Cloning process completed!"
echo -e "${GREEN}🎉 All repositories cloned successfully!${NC}"
echo ""
echo -e "${BLUE}✅ Individual repositories are now in: $INDIVIDUAL_REPOS_DIR/${NC}"
echo ""
echo "Directory structure:"
ls -la | head -10

echo ""
echo "Next step: Run ../scripts/setup_sync_workflow.sh"

SCRIPT_EOF

# Make the new script executable
chmod +x clone_individual_repos_updated.sh

echo "✅ Updated script created: clone_individual_repos_updated.sh"

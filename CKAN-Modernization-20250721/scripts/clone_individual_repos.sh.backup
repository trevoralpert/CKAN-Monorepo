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

# Define repository names (just the repo names, not full paths)
REPO_NAMES=(
    "ckan"
    "ckanext-spatial"
    "ckanext-dcat"
    "ckanext-harvest"
    "ckanext-scheming"
    "ckanext-pages"
    "ckanext-showcase" 
    "ckanext-pdfview"
    "ckanext-validation"
    "ckanext-issues"
    "ckanext-qa"
    "ckanext-charts"
    "ckanext-ga-report"
    "ckanext-iati"
    "ckanext-dgu"
    "ckanext-datagovuk"
    "ckanext-dcatapit"
    "ckanext-nhm"
    "ckanext-versioned-datastore"
    "ckanext-canada"
)

# Original upstream repositories for setting remotes (bash 3.2 compatible)
get_upstream_repo() {
    case "$1" in
        "ckan") echo "https://github.com/ckan/ckan" ;;
        "ckanext-spatial") echo "https://github.com/ckan/ckanext-spatial" ;;
        "ckanext-dcat") echo "https://github.com/ckan/ckanext-dcat" ;;
        "ckanext-harvest") echo "https://github.com/ckan/ckanext-harvest" ;;
        "ckanext-scheming") echo "https://github.com/ckan/ckanext-scheming" ;;
        "ckanext-pages") echo "https://github.com/ckan/ckanext-pages" ;;
        "ckanext-showcase") echo "https://github.com/ckan/ckanext-showcase" ;;
        "ckanext-pdfview") echo "https://github.com/ckan/ckanext-pdfview" ;;
        "ckanext-validation") echo "https://github.com/ckan/ckanext-validation" ;;
        "ckanext-issues") echo "https://github.com/ckan/ckanext-issues" ;;
        "ckanext-qa") echo "https://github.com/ckan/ckanext-qa" ;;
        "ckanext-charts") echo "https://github.com/ckan/ckanext-charts" ;;
        "ckanext-ga-report") echo "https://github.com/ckan/ckanext-ga-report" ;;
        "ckanext-iati") echo "https://github.com/ckan/ckanext-iati" ;;
        "ckanext-dgu") echo "https://github.com/datagovuk/ckanext-dgu" ;;
        "ckanext-datagovuk") echo "https://github.com/alphagov/ckanext-datagovuk" ;;
        "ckanext-dcatapit") echo "https://github.com/geosolutions-it/ckanext-dcatapit" ;;
        "ckanext-nhm") echo "https://github.com/NaturalHistoryMuseum/ckanext-nhm" ;;
        "ckanext-versioned-datastore") echo "https://github.com/NaturalHistoryMuseum/ckanext-versioned-datastore" ;;
        "ckanext-canada") echo "https://github.com/open-data/ckanext-canada" ;;
        *) echo "" ;;
    esac
}

# Function to clone a repository and set up remotes
clone_and_setup_repo() {
    local repo_name=$1
    local upstream_url=$(get_upstream_repo "$repo_name")
    
    echo -e "${BLUE}Processing: $repo_name${NC}"
    
    if [ -d "$repo_name" ]; then
        echo -e "${YELLOW}⚠️  Directory already exists: $repo_name${NC}"
        cd "$repo_name"
    else
        # Clone the forked repository
        echo -e "${BLUE}📥 Cloning fork: $GITHUB_USER/$repo_name${NC}"
        if gh repo clone "$GITHUB_USER/$repo_name"; then
            echo -e "${GREEN}✅ Successfully cloned: $repo_name${NC}"
            cd "$repo_name"
        else
            echo -e "${RED}❌ Failed to clone: $repo_name${NC}"
            return 1
        fi
    fi
    
    # Add upstream remote if it doesn't exist
    if ! git remote get-url upstream >/dev/null 2>&1; then
        echo -e "${BLUE}🔗 Adding upstream remote: $upstream_url${NC}"
        git remote add upstream "$upstream_url"
    else
        echo -e "${YELLOW}⚠️  Upstream remote already exists${NC}"
    fi
    
    # Fetch from upstream
    echo -e "${BLUE}📡 Fetching from upstream...${NC}"
    git fetch upstream
    
    cd ..
    return 0
}

# Main execution
main() {
    echo "Checking GitHub CLI authentication..."
    if ! gh auth status >/dev/null 2>&1; then
        echo -e "${RED}❌ GitHub CLI not authenticated. Run: gh auth login${NC}"
        exit 1
    fi
    
    # Create and navigate to individual-repos directory
    mkdir -p "../individual-repos"
    cd "../individual-repos"
    
    echo "Starting repository cloning process..."
    echo "======================================"
    
    failed_repos=()
    
    for repo_name in "${REPO_NAMES[@]}"; do
        if ! clone_and_setup_repo "$repo_name"; then
            failed_repos+=("$repo_name")
        fi
        echo
    done
    
    echo "======================================"
    echo "Cloning process completed!"
    
    if [ ${#failed_repos[@]} -eq 0 ]; then
        echo -e "${GREEN}🎉 All repositories cloned successfully!${NC}"
    else
        echo -e "${YELLOW}⚠️  Some repositories failed to clone:${NC}"
        for repo in "${failed_repos[@]}"; do
            echo -e "${RED}  - $repo${NC}"
        done
    fi
    
    echo
    echo -e "${GREEN}✅ Individual repositories are now in: ../individual-repos/${NC}"
    echo
    echo "Directory structure:"
    ls -la | grep '^d'
    
    echo
    echo "Next step: Run ../scripts/setup_sync_workflow.sh"
}

main "$@" 
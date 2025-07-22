#!/bin/bash

# CKAN Modernization Project - Repository Re-forking Script
# This script re-forks all repositories that exist in our monorepo

set -e

echo "🚀 CKAN Modernization - Repository Re-forking Script"
echo "=================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Define all repositories to fork (bash 3.2 compatible)
REPO_PATHS="ckan/ckan ckan/ckanext-spatial ckan/ckanext-dcat ckan/ckanext-harvest ckan/ckanext-scheming ckan/ckanext-pages ckan/ckanext-showcase ckan/ckanext-pdfview ckan/ckanext-validation ckan/ckanext-issues ckan/ckanext-qa ckan/ckanext-charts ckan/ckanext-ga-report ckan/ckanext-iati datagovuk/ckanext-dgu alphagov/ckanext-datagovuk geosolutions-it/ckanext-dcatapit NaturalHistoryMuseum/ckanext-nhm NaturalHistoryMuseum/ckanext-versioned-datastore open-data/ckanext-canada"

get_repo_url() {
    echo "https://github.com/$1"
}

# Function to check if repository exists and is accessible
check_repo_exists() {
    local repo_url=$1
    if gh api "repos/${repo_url#https://github.com/}" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to fork a repository
fork_repository() {
    local repo_path=$1
    local repo_url=$(get_repo_url "$repo_path")
    local repo_name=$(basename "$repo_path")
    
    echo -e "${BLUE}Processing: $repo_name${NC}"
    
    if ! check_repo_exists "$repo_url"; then
        echo -e "${RED}❌ Repository not accessible: $repo_url${NC}"
        return 1
    fi
    
    # Check if fork already exists
    if gh repo view "$repo_name" >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Fork already exists: $repo_name${NC}"
        return 0
    fi
    
    # Fork the repository
    echo -e "${BLUE}🍴 Forking $repo_path...${NC}"
    if gh repo fork "$repo_path" --clone=false; then
        echo -e "${GREEN}✅ Successfully forked: $repo_name${NC}"
    else
        echo -e "${RED}❌ Failed to fork: $repo_name${NC}"
        return 1
    fi
}

# Main execution
main() {
    echo "Checking GitHub CLI authentication..."
    if ! gh auth status >/dev/null 2>&1; then
        echo -e "${RED}❌ GitHub CLI not authenticated. Run: gh auth login${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ GitHub CLI authenticated${NC}"
    echo
    
    # Create individual-repos directory if it doesn't exist
    mkdir -p "../individual-repos"
    
    echo "Starting repository forking process..."
    echo "======================================"
    
    failed_repos=()
    
    for repo_path in $REPO_PATHS; do
        if ! fork_repository "$repo_path"; then
            failed_repos+=("$repo_path")
        fi
        echo
    done
    
    echo "======================================"
    echo "Forking process completed!"
    
    if [ ${#failed_repos[@]} -eq 0 ]; then
        echo -e "${GREEN}🎉 All repositories forked successfully!${NC}"
    else
        echo -e "${YELLOW}⚠️  Some repositories failed to fork:${NC}"
        for repo in "${failed_repos[@]}"; do
            echo -e "${RED}  - $repo${NC}"
        done
    fi
    
    echo
    echo "Next steps:"
    echo "1. Run: ./clone_individual_repos.sh to clone your forks"
    echo "2. Run: ./setup_sync_workflow.sh to configure sync workflow"
}

main "$@" 
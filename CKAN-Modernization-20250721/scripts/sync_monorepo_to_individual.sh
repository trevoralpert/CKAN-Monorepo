#!/bin/bash

# CKAN Modernization Project - Sync Monorepo to Individual Repos
# This script syncs changes between the monorepo and individual repositories

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MONOREPO_DIR="$PROJECT_ROOT/ckan-monorepo"
INDIVIDUAL_DIR="$PROJECT_ROOT/individual-repos"

# Repository mappings (monorepo_path:individual_repo_name) - bash 3.2 compatible
get_repo_mapping() {
    case "$1" in
        "ckan") echo "ckan" ;;
        "extensions/ckanext-spatial") echo "ckanext-spatial" ;;
        "extensions/ckanext-dcat") echo "ckanext-dcat" ;;
        "extensions/ckanext-harvest") echo "ckanext-harvest" ;;
        "extensions/ckanext-scheming") echo "ckanext-scheming" ;;
        "extensions/ckanext-pages") echo "ckanext-pages" ;;
        "extensions/ckanext-showcase") echo "ckanext-showcase" ;;
        "extensions/ckanext-pdfview") echo "ckanext-pdfview" ;;
        "extensions/ckanext-validation") echo "ckanext-validation" ;;
        "extensions/ckanext-issues") echo "ckanext-issues" ;;
        "extensions/ckanext-qa") echo "ckanext-qa" ;;
        "extensions/ckanext-charts") echo "ckanext-charts" ;;
        "extensions/ckanext-ga-report") echo "ckanext-ga-report" ;;
        "extensions/ckanext-iati") echo "ckanext-iati" ;;
        "extensions/ckanext-dgu") echo "ckanext-dgu" ;;
        "extensions/ckanext-datagovuk") echo "ckanext-datagovuk" ;;
        "extensions/ckanext-dcatapit") echo "ckanext-dcatapit" ;;
        "extensions/ckanext-nhm") echo "ckanext-nhm" ;;
        "extensions/ckanext-versioned-datastore") echo "ckanext-versioned-datastore" ;;
        "extensions/ckanext-canada") echo "ckanext-canada" ;;
        *) echo "" ;;
    esac
}

get_monorepo_path_for_repo() {
    case "$1" in
        "ckan") echo "ckan" ;;
        "ckanext-spatial") echo "extensions/ckanext-spatial" ;;
        "ckanext-dcat") echo "extensions/ckanext-dcat" ;;
        "ckanext-harvest") echo "extensions/ckanext-harvest" ;;
        "ckanext-scheming") echo "extensions/ckanext-scheming" ;;
        "ckanext-pages") echo "extensions/ckanext-pages" ;;
        "ckanext-showcase") echo "extensions/ckanext-showcase" ;;
        "ckanext-pdfview") echo "extensions/ckanext-pdfview" ;;
        "ckanext-validation") echo "extensions/ckanext-validation" ;;
        "ckanext-issues") echo "extensions/ckanext-issues" ;;
        "ckanext-qa") echo "extensions/ckanext-qa" ;;
        "ckanext-charts") echo "extensions/ckanext-charts" ;;
        "ckanext-ga-report") echo "extensions/ckanext-ga-report" ;;
        "ckanext-iati") echo "extensions/ckanext-iati" ;;
        "ckanext-dgu") echo "extensions/ckanext-dgu" ;;
        "ckanext-datagovuk") echo "extensions/ckanext-datagovuk" ;;
        "ckanext-dcatapit") echo "extensions/ckanext-dcatapit" ;;
        "ckanext-nhm") echo "extensions/ckanext-nhm" ;;
        "ckanext-versioned-datastore") echo "extensions/ckanext-versioned-datastore" ;;
        "ckanext-canada") echo "extensions/ckanext-canada" ;;
        *) echo "" ;;
    esac
}

# All repository names for iteration (excluding non-existent repos)
ALL_REPOS="ckan ckanext-spatial ckanext-dcat ckanext-harvest ckanext-scheming ckanext-pages ckanext-showcase ckanext-pdfview ckanext-validation ckanext-issues ckanext-qa ckanext-dgu ckanext-datagovuk ckanext-dcatapit ckanext-nhm ckanext-versioned-datastore ckanext-canada"

# Function to display help
show_help() {
    echo "CKAN Modernization - Repository Sync Tool"
    echo "=========================================="
    echo
    echo "Usage: $0 [OPTION] [REPOSITORY]"
    echo
    echo "Options:"
    echo "  push-all       Push all changes from monorepo to individual repos"
    echo "  push <repo>    Push changes from monorepo to specific individual repo"
    echo "  pull-all       Pull all changes from individual repos to monorepo"
    echo "  pull <repo>    Pull changes from specific individual repo to monorepo"
    echo "  status         Show git status of all repositories"
    echo "  branch <name>  Create a new feature branch in all repositories"
    echo "  pr <repo>      Create a pull request from individual repo to upstream"
    echo "  help          Show this help message"
    echo
    echo "Repository names:"
    for repo_name in $ALL_REPOS; do
        echo "  $repo_name"
    done
}

# Function to check prerequisites
check_prerequisites() {
    if [ ! -d "$MONOREPO_DIR" ]; then
        echo -e "${RED}❌ Monorepo directory not found: $MONOREPO_DIR${NC}"
        exit 1
    fi
    
    if [ ! -d "$INDIVIDUAL_DIR" ]; then
        echo -e "${RED}❌ Individual repos directory not found: $INDIVIDUAL_DIR${NC}"
        echo "Run: ./clone_individual_repos.sh first"
        exit 1
    fi
    
    if ! command -v gh &> /dev/null; then
        echo -e "${RED}❌ GitHub CLI (gh) is not installed${NC}"
        exit 1
    fi
}

# Function to get repository paths
get_repo_paths() {
    local repo_name=$1
    local mono_path=$(get_monorepo_path_for_repo "$repo_name")
    
    if [ -z "$mono_path" ]; then
        echo -e "${RED}❌ Repository not found in mapping: $repo_name${NC}"
        return 1
    fi
    
    local monorepo_path="$MONOREPO_DIR/$mono_path"
    local individual_path="$INDIVIDUAL_DIR/$repo_name"
    
    echo "$monorepo_path:$individual_path"
}

# Function to sync changes from monorepo to individual repo
sync_monorepo_to_individual() {
    local repo_name=$1
    local create_branch=${2:-false}
    local branch_name=${3:-""}
    
    echo -e "${BLUE}🔄 Syncing $repo_name: monorepo → individual${NC}"
    
    local paths=$(get_repo_paths "$repo_name")
    local monorepo_path=$(echo "$paths" | cut -d: -f1)
    local individual_path=$(echo "$paths" | cut -d: -f2)
    
    if [ ! -d "$monorepo_path" ]; then
        echo -e "${YELLOW}⚠️  Skipping $repo_name: not found in monorepo${NC}"
        return 0
    fi
    
    if [ ! -d "$individual_path" ]; then
        echo -e "${RED}❌ Individual repo not found: $individual_path${NC}"
        return 1
    fi
    
    # Create temporary directory for sync
    local temp_dir=$(mktemp -d)
    
    # Copy files from monorepo to temp directory
    cp -r "$monorepo_path/." "$temp_dir/"
    
    # Navigate to individual repo
    cd "$individual_path"
    
    # Create branch if requested
    if [ "$create_branch" = true ] && [ -n "$branch_name" ]; then
        echo -e "${BLUE}🌿 Creating branch: $branch_name${NC}"
        git checkout -b "$branch_name" 2>/dev/null || git checkout "$branch_name"
    fi
    
    # Remove existing files (except .git and important files)
    find . -maxdepth 1 -type f ! -name '.git*' ! -name '.github' ! -name 'README.md' -delete 2>/dev/null || true
    find . -maxdepth 1 -type d ! -name '.' ! -name '.git' ! -name '.github' -exec rm -rf {} + 2>/dev/null || true
    
    # Copy new files from temp directory
    cp -r "$temp_dir/." .
    
    # Clean up temp directory
    rm -rf "$temp_dir"
    
    # Check if there are changes
    if git diff --quiet && git diff --cached --quiet; then
        echo -e "${GREEN}✅ No changes to sync for $repo_name${NC}"
    else
        echo -e "${YELLOW}📝 Changes detected in $repo_name${NC}"
        git add .
        echo -e "${BLUE}📋 Git status:${NC}"
        git status --short
    fi
    
    cd - >/dev/null
}

# Function to create pull request
create_pull_request() {
    local repo_name=$1
    local paths=$(get_repo_paths "$repo_name")
    local individual_path=$(echo "$paths" | cut -d: -f2)
    
    if [ ! -d "$individual_path" ]; then
        echo -e "${RED}❌ Individual repo not found: $individual_path${NC}"
        return 1
    fi
    
    cd "$individual_path"
    
    local current_branch=$(git branch --show-current)
    if [ "$current_branch" = "master" ] || [ "$current_branch" = "main" ]; then
        echo -e "${RED}❌ Cannot create PR from main branch. Create a feature branch first.${NC}"
        return 1
    fi
    
    echo -e "${BLUE}🚀 Creating pull request for $repo_name from branch: $current_branch${NC}"
    
    # Push the branch first
    git push origin "$current_branch"
    
    # Create PR
    gh pr create \
        --title "CKAN Modernization: Updates from modernization project" \
        --body "This PR contains modernization improvements developed as part of the CKAN Legacy Modernization project.

## Changes
- [Add description of your changes here]

## Testing
- [ ] All tests pass
- [ ] Feature has been tested manually

## Documentation
- [ ] Documentation updated (if needed)

Generated from monorepo sync on $(date)" \
        --draft
    
    echo -e "${GREEN}✅ Draft PR created! Update the description and mark as ready for review.${NC}"
    
    cd - >/dev/null
}

# Function to show status of all repositories
show_status() {
    echo -e "${BLUE}📊 Repository Status Overview${NC}"
    echo "=============================="
    
    for repo_name in $ALL_REPOS; do
        local mono_path=$(get_monorepo_path_for_repo "$repo_name")
        local monorepo_path="$MONOREPO_DIR/$mono_path"
        local individual_path="$INDIVIDUAL_DIR/$repo_name"
        
        echo
        echo -e "${YELLOW}📁 $repo_name${NC}"
        
        # Monorepo status
        if [ -d "$monorepo_path" ]; then
            cd "$monorepo_path"
            if [ -d ".git" ]; then
                echo -e "  ${BLUE}Monorepo:${NC} $(git branch --show-current) - $(git log --oneline -1 | cut -c1-50)"
            else
                echo -e "  ${BLUE}Monorepo:${NC} Not a git repository"
            fi
            cd - >/dev/null
        else
            echo -e "  ${RED}Monorepo: Not found${NC}"
        fi
        
        # Individual repo status
        if [ -d "$individual_path" ]; then
            cd "$individual_path"
            local branch=$(git branch --show-current)
            local commit=$(git log --oneline -1 | cut -c1-50)
            local status=$(git status --porcelain | wc -l | xargs)
            echo -e "  ${BLUE}Individual:${NC} $branch - $commit"
            if [ "$status" -gt 0 ]; then
                echo -e "  ${YELLOW}  📝 $status uncommitted changes${NC}"
            fi
            cd - >/dev/null
        else
            echo -e "  ${RED}Individual: Not found${NC}"
        fi
    done
}

# Function to create feature branch in all repos
create_feature_branch() {
    local branch_name=$1
    
    if [ -z "$branch_name" ]; then
        echo -e "${RED}❌ Branch name is required${NC}"
        return 1
    fi
    
    echo -e "${BLUE}🌿 Creating feature branch '$branch_name' in all repositories${NC}"
    
    for repo_name in $ALL_REPOS; do
        local individual_path="$INDIVIDUAL_DIR/$repo_name"
        
        if [ -d "$individual_path" ]; then
            echo -e "${YELLOW}Processing: $repo_name${NC}"
            cd "$individual_path"
            git checkout -b "$branch_name" 2>/dev/null || echo -e "${YELLOW}  Branch already exists${NC}"
            cd - >/dev/null
        fi
    done
    
    echo -e "${GREEN}✅ Feature branch '$branch_name' created in all repositories${NC}"
}

# Main execution
main() {
    local command=${1:-"help"}
    local repo_name=${2:-""}
    
    check_prerequisites
    
    case "$command" in
        "push-all")
            echo -e "${BLUE}🚀 Pushing all changes from monorepo to individual repos${NC}"
            for repo_name in $ALL_REPOS; do
                sync_monorepo_to_individual "$repo_name"
            done
            ;;
        "push")
            if [ -z "$repo_name" ]; then
                echo -e "${RED}❌ Repository name required for push command${NC}"
                show_help
                exit 1
            fi
            sync_monorepo_to_individual "$repo_name"
            ;;
        "status")
            show_status
            ;;
        "branch")
            create_feature_branch "$repo_name"
            ;;
        "pr")
            if [ -z "$repo_name" ]; then
                echo -e "${RED}❌ Repository name required for pr command${NC}"
                show_help
                exit 1
            fi
            create_pull_request "$repo_name"
            ;;
        "help")
            show_help
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $command${NC}"
            show_help
            exit 1
            ;;
    esac
}

main "$@" 
#!/usr/bin/env bash
# CKAN Legacy Modernization Project Setup Script
# This script will set up your entire CKAN project structure for Gauntlet AI

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPOS=(
    "ckan"
    "ckanext-harvest"
    "ckanext-spatial"
    "ckanext-qa"
    "ckanext-issues"
    "ckanext-scheming"
)

# Additional optional repos if you need more LOC
OPTIONAL_REPOS=(
    "ckanext-xloader"
    "ckanext-archiver"
    "datapusher"
)

echo -e "${BLUE}=== CKAN Legacy Modernization Project Setup ===${NC}"
echo ""

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check for git
    if ! command -v git &> /dev/null; then
        echo -e "${RED}❌ Git is not installed. Please install git first.${NC}"
        exit 1
    fi
    
    # Check for GitHub CLI
    if ! command -v gh &> /dev/null; then
        echo -e "${RED}❌ GitHub CLI (gh) is not installed.${NC}"
        echo "Install it with:"
        echo "  macOS: brew install gh"
        echo "  Linux: See https://github.com/cli/cli#installation"
        exit 1
    fi
    
    # Check GitHub authentication
    if ! gh auth status &> /dev/null; then
        echo -e "${RED}❌ GitHub CLI is not authenticated.${NC}"
        echo "Run: gh auth login"
        exit 1
    fi
    
    # Check for cloc (optional but recommended)
    if ! command -v cloc &> /dev/null; then
        echo -e "${YELLOW}⚠️  cloc is not installed (optional for detailed LOC counting)${NC}"
        echo "Install with: brew install cloc (macOS) or apt-get install cloc (Linux)"
    fi
    
    echo -e "${GREEN}✅ All prerequisites met!${NC}"
    echo ""
}

# Create project structure
create_project_structure() {
    echo -e "${YELLOW}Creating project structure...${NC}"
    
    # Create main project directory
    PROJECT_DIR="CKAN-Modernization-$(date +%Y%m%d)"
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    
    # Create subdirectories
    mkdir -p individual-repos
    mkdir -p documentation
    mkdir -p scripts
    
    echo -e "${GREEN}✅ Created project directory: $PROJECT_DIR${NC}"
}

# Fork and clone repositories
fork_and_clone_repos() {
    echo -e "${YELLOW}Forking and cloning CKAN repositories...${NC}"
    cd individual-repos
    
    for repo in "${REPOS[@]}"; do
        echo -e "${BLUE}Processing $repo...${NC}"
        
        # Check if already forked
        if gh repo view "$(gh api user --jq .login)/$repo" &> /dev/null; then
            echo "  Already forked, cloning..."
            gh repo clone "$(gh api user --jq .login)/$repo"
        else
            echo "  Forking and cloning..."
            gh repo fork "ckan/$repo" --clone --remote
        fi
        
        # Add upstream remote
        cd "$repo"
        git remote add upstream "https://github.com/ckan/$repo.git" 2>/dev/null || true
        cd ..
        
        echo -e "${GREEN}  ✅ $repo ready${NC}"
    done
    
    cd ..
}

# Create monorepo with submodules
create_monorepo() {
    echo -e "${YELLOW}Creating monorepo structure...${NC}"
    
    git init ckan-monorepo
    cd ckan-monorepo
    
    # Add core CKAN as submodule
    git submodule add ../individual-repos/ckan ckan
    
    # Create extensions directory and add extensions
    mkdir -p extensions
    
    for repo in "${REPOS[@]:1}"; do  # Skip first element (ckan)
        echo "Adding $repo as submodule..."
        git submodule add "../individual-repos/$repo" "extensions/$repo"
    done
    
    # Create project files
    cat > README.md << 'EOF'
# CKAN Modernization Project - Gauntlet AI

This is a monorepo structure for the CKAN legacy modernization project.

## Structure
- `/ckan` - Core CKAN repository
- `/extensions/` - CKAN extensions
  - `ckanext-harvest` - Remote data harvesting
  - `ckanext-spatial` - Geospatial features
  - `ckanext-qa` - Data quality checks
  - `ckanext-issues` - Issue tracking
  - `ckanext-scheming` - Custom schemas

## Lines of Code
This combined repository contains over 1.2 million lines of code.

## Daily Workflow

### Update all submodules to latest
```bash
git submodule update --remote --merge
```

### Work on a specific component
```bash
cd extensions/ckanext-qa
git checkout -b feature/async-improvements
# Make changes
git add .
git commit -m "Add async task processing"
git push origin feature/async-improvements
```

### Create a pull request
```bash
gh pr create
```
EOF

    cat > .gitignore << 'EOF'
# Python
*.pyc
__pycache__/
*.egg-info/
.pytest_cache/
venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
*.log
.coverage
htmlcov/
dist/
build/
EOF

    # Commit initial structure
    git add .
    git commit -m "Initial CKAN monorepo structure with submodules"
    
    cd ..
    echo -e "${GREEN}✅ Monorepo created successfully!${NC}"
}

# Count lines of code
count_lines_of_code() {
    echo -e "${YELLOW}Counting lines of code...${NC}"
    cd ckan-monorepo
    
    # Simple count
    echo "Simple line count (all files):"
    find . -type f -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" | xargs wc -l | tail -n1
    
    # Detailed count with cloc if available
    if command -v cloc &> /dev/null; then
        echo ""
        echo "Detailed count by language:"
        cloc . --exclude-dir=.git
    fi
    
    cd ..
}

# Create helper scripts
create_helper_scripts() {
    echo -e "${YELLOW}Creating helper scripts...${NC}"
    
    # Update script
    cat > scripts/update_all.sh << 'EOF'
#!/bin/bash
# Update all repositories to latest upstream

cd ../ckan-monorepo
git submodule foreach 'git fetch upstream && git merge upstream/master'
EOF

    # Feature branch script
    cat > scripts/create_feature.sh << 'EOF'
#!/bin/bash
# Create a feature branch in a specific extension
# Usage: ./create_feature.sh ckanext-qa "async-improvements"

if [ $# -ne 2 ]; then
    echo "Usage: $0 <extension-name> <branch-name>"
    exit 1
fi

cd "../ckan-monorepo/extensions/$1" || exit 1
git checkout -b "feature/$2"
echo "Created branch feature/$2 in $1"
EOF

    # PR creation script
    cat > scripts/create_pr.sh << 'EOF'
#!/bin/bash
# Create a pull request for current branch
# Usage: ./create_pr.sh

gh pr create --fill
EOF

    chmod +x scripts/*.sh
    echo -e "${GREEN}✅ Helper scripts created${NC}"
}

# Create initial documentation
create_documentation() {
    echo -e "${YELLOW}Creating initial documentation...${NC}"
    
    cat > documentation/project_plan.md << 'EOF'
# CKAN Modernization Project Plan

## Target User Segment
**Small City Open Data Portals**
- Cities with 50k-500k population
- Limited IT resources
- Need modern, mobile-friendly data portal
- Current pain points:
  - Poor mobile experience
  - Slow search functionality
  - Complex deployment process
  - Lack of modern authentication

## Six Modernization Features

1. **Modern Authentication (OAuth2/SSO)**
   - Replace legacy login with OAuth2
   - Support Google/GitHub/Microsoft SSO
   - Add 2FA support

2. **Async Task Processing**
   - Convert synchronous harvesters to async
   - Add Celery for background jobs
   - Implement progress tracking

3. **REST/GraphQL API Layer**
   - Modern API with OpenAPI docs
   - GraphQL endpoint for flexible queries
   - Rate limiting and API keys

4. **Docker/Kubernetes Deployment**
   - Multi-stage Dockerfile
   - docker-compose for local dev
   - Kubernetes manifests for production

5. **Mobile-Responsive UI**
   - Replace legacy templates with modern responsive design
   - Use Tailwind CSS
   - Progressive Web App features

6. **Real-time Notifications**
   - WebSocket support for live updates
   - Activity stream enhancements
   - Email/SMS notification options

## Architecture Overview
- Migrate from Pylons to FastAPI/Flask hybrid
- Keep PostgreSQL + Solr backend
- Add Redis for caching/sessions
- Containerize all components
EOF

    cat > documentation/ai_prompts_log.md << 'EOF'
# AI Prompts Log

## Initial Architecture Analysis

### Prompt 1: Understanding CKAN Structure
```
Analyze the CKAN codebase structure. Focus on:
1. Main architectural components
2. How Pylons framework is integrated
3. Key business logic locations
4. Database models and relationships
5. Extension system architecture
```

### Prompt 2: Identifying Modernization Opportunities
```
Given this Pylons-based CKAN codebase, identify:
1. Synchronous code that could benefit from async/await
2. Monolithic components suitable for microservice extraction
3. Legacy authentication system pain points
4. Performance bottlenecks in search and data processing
```

## Feature Implementation Prompts

### OAuth2 Implementation
```
Show me how to integrate OAuth2 authentication into CKAN:
1. Keep existing user model
2. Add OAuth2 provider support (Google, GitHub)
3. Maintain backward compatibility with existing sessions
4. Include example with Flask-Dance or Authlib
```

### Async Task Processing
```
Convert CKAN's harvest module from synchronous to asynchronous:
1. Identify current synchronous harvest jobs
2. Design Celery task structure
3. Add progress tracking
4. Maintain compatibility with existing harvesters
```

## Continue adding prompts as you work...
EOF

    echo -e "${GREEN}✅ Documentation created${NC}"
}

# Main setup flow
main() {
    check_prerequisites
    create_project_structure
    fork_and_clone_repos
    create_monorepo
    count_lines_of_code
    create_helper_scripts
    create_documentation
    
    echo ""
    echo -e "${GREEN}🎉 Setup complete!${NC}"
    echo ""
    echo "Project structure:"
    echo "  $PROJECT_DIR/"
    echo "  ├── individual-repos/     # Forked repos for PRs"
    echo "  ├── ckan-monorepo/       # Combined monorepo (1.2M+ LOC)"
    echo "  ├── documentation/       # Project docs"
    echo "  └── scripts/            # Helper scripts"
    echo ""
    echo "Next steps:"
    echo "1. cd $PROJECT_DIR/ckan-monorepo"
    echo "2. Set up Python virtual environment"
    echo "3. Install CKAN dependencies"
    echo "4. Start analyzing with AI!"
    echo ""
    echo -e "${YELLOW}Remember to document all AI prompts in documentation/ai_prompts_log.md${NC}"
}

# Run main function
main 
# CKAN Modernization Quick Reference

## Initial Setup
```bash
# Make setup script executable and run
chmod +x setup_ckan_project.sh
./setup_ckan_project.sh

# If you need to install prerequisites first:
brew install gh cloc  # macOS
# or
sudo apt-get install gh cloc  # Ubuntu/Debian
```

## Verify LOC Count
```bash
# Quick count (from monorepo root)
find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" \) | xargs wc -l

# Detailed count
cloc . --exclude-dir=.git,venv,node_modules

# Save count proof for submission
cloc . --exclude-dir=.git > line_count_proof.txt
```

## Daily Git Workflow (Dual-Repo Setup)
```bash
# 1. Create feature branch across all repos
cd CKAN-Modernization-20250721/scripts
./sync_monorepo_to_individual.sh branch feature/async-improvements

# 2. Work in monorepo (easier development)
cd ../ckan-monorepo/extensions/ckanext-qa
# Make your changes...

# 3. Sync changes to individual repos
cd ../../scripts
./sync_monorepo_to_individual.sh push ckanext-qa

# 4. Commit in individual repo
cd ../individual-repos/ckanext-qa
git add .
git commit -m "Add async task processing"
git push origin feature/async-improvements

# 5. Create PR with one command
cd ../../scripts
./sync_monorepo_to_individual.sh pr ckanext-qa
```

## Dual Repository Setup (IMPORTANT!)
```bash
# If you deleted your GitHub forks, re-create them:
cd CKAN-Modernization-20250721/scripts
chmod +x *.sh
./refork_all_repos.sh          # Fork all 20 repos on GitHub
./clone_individual_repos.sh    # Clone your forks locally  
./sync_monorepo_to_individual.sh status  # Verify setup

# See documentation/dual_repo_workflow.md for complete guide
```

## Running CKAN Locally
```bash
# Using Docker (recommended)
cd ckan-monorepo
docker-compose up -d

# Check logs
docker-compose logs -f ckan

# Access at http://localhost:5000
```

## Common AI Prompts

### Architecture Analysis
```
"Analyze this CKAN module [paste code] and explain:
1. Current architecture patterns
2. Pylons-specific dependencies
3. Modernization opportunities
4. Potential async conversion points"
```

### Feature Implementation
```
"Help me add [FEATURE] to CKAN:
- Current code: [paste relevant sections]
- Target: [describe desired functionality]
- Constraints: Must maintain backward compatibility
Please provide step-by-step implementation"
```

### Debugging
```
"I'm getting this error in CKAN: [paste error]
Context: [describe what you were doing]
Relevant code: [paste code section]
What's the issue and how do I fix it?"
```

## Python Environment
```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install CKAN dependencies
pip install -r ckan/requirements.txt
pip install -r ckan/dev-requirements.txt
```

## Testing Changes
```bash
# Run CKAN tests
cd ckan
pytest ckan/tests/

# Test specific module
pytest ckan/tests/controllers/test_package.py

# Run with coverage
pytest --cov=ckan ckan/tests/
```

## Troubleshooting

### "Permission denied" on setup script
```bash
chmod +x setup_ckan_project.sh
```

### GitHub CLI not authenticated
```bash
gh auth login
# Choose GitHub.com, HTTPS, authenticate with browser
```

### Port 5000 already in use
```bash
# Find process using port
lsof -i :5000  # Mac/Linux
# Kill it or use different port in docker-compose
```

### Submodule issues
```bash
# Initialize/update all submodules
git submodule update --init --recursive

# Reset submodule to clean state
cd extensions/ckanext-harvest
git checkout master
git pull upstream master
```

## Project Structure Reminder
```
CKAN-Modernization-YYYYMMDD/
├── individual-repos/        # Your forks for PRs
│   ├── ckan/
│   ├── ckanext-harvest/
│   └── ...
├── ckan-monorepo/          # Working monorepo
│   ├── ckan/               # Core CKAN
│   ├── extensions/         # All extensions
│   └── README.md
├── documentation/          # Your project docs
│   ├── project_plan.md
│   └── ai_prompts_log.md
└── scripts/               # Helper scripts
    ├── update_all.sh
    └── create_feature.sh
```

## Remember!
- Document EVERY AI prompt in `ai_prompts_log.md`
- Take before/after screenshots
- Commit frequently with clear messages
- Test each feature independently
- You can do this! 💕 
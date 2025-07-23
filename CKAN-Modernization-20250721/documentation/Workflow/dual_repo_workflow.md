# CKAN Modernization: Dual Repository Workflow Guide

This guide explains how to work with both the monorepo (for development) and individual forks (for PRs) simultaneously.

## 🎯 **The Problem We're Solving**

We need to:
1. **Develop efficiently** in a monorepo (all extensions together)
2. **Create PRs** from individual forks back to upstream repositories
3. **Keep both in sync** without manual copy-paste hell

## 📁 **Directory Structure**

After setup, you'll have:

```
CKAN-Modernization-20250721/
├── ckan-monorepo/              # Development workspace
│   ├── ckan/                   # Core CKAN
│   └── extensions/             # All extensions
│       ├── ckanext-spatial/
│       ├── ckanext-dcat/
│       └── ...
├── individual-repos/           # Individual forks for PRs
│   ├── ckan/                   # Your fork of ckan/ckan
│   ├── ckanext-spatial/        # Your fork of ckan/ckanext-spatial
│   ├── ckanext-dcat/           # Your fork of ckan/ckanext-dcat
│   └── ...
└── scripts/                    # Automation scripts
    ├── refork_all_repos.sh
    ├── clone_individual_repos.sh
    └── sync_monorepo_to_individual.sh
```

## 🚀 **Initial Setup**

### Step 1: Re-fork All Repositories

```bash
cd CKAN-Modernization-20250721/scripts
chmod +x *.sh
./refork_all_repos.sh
```

This creates forks of all 20 repositories on your GitHub account.

### Step 2: Clone Individual Forks

```bash
./clone_individual_repos.sh
```

This clones your forks locally and sets up upstream remotes.

### Step 3: Verify Setup

```bash
./sync_monorepo_to_individual.sh status
```

Should show both monorepo and individual repo status for all extensions.

## 🔄 **Daily Development Workflow**

### Scenario 1: Starting a New Feature

```bash
# 1. Create feature branch in all individual repos
./sync_monorepo_to_individual.sh branch feature/oauth2-integration

# 2. Work in the monorepo (easier development)
cd ../ckan-monorepo/extensions/ckanext-spatial
# Make your changes...

# 3. Test everything together in monorepo
docker-compose up -d

# 4. Sync changes to individual repos
cd ../../scripts
./sync_monorepo_to_individual.sh push-all
```

### Scenario 2: Working on Specific Extension

```bash
# 1. Create feature branch
./sync_monorepo_to_individual.sh branch feature/async-improvements

# 2. Work in monorepo
cd ../ckan-monorepo/extensions/ckanext-qa
# Make changes to QA extension...

# 3. Sync only this extension
cd ../../scripts
./sync_monorepo_to_individual.sh push ckanext-qa

# 4. Go to individual repo to commit and test
cd ../individual-repos/ckanext-qa
git add .
git commit -m "Add async task processing to QA extension"
git push origin feature/async-improvements
```

### Scenario 3: Creating Pull Requests

```bash
# 1. Ensure changes are synced and committed
./sync_monorepo_to_individual.sh push ckanext-spatial
cd ../individual-repos/ckanext-spatial
git add .
git commit -m "Add OAuth2 integration for spatial features"

# 2. Create PR directly from script
cd ../../scripts
./sync_monorepo_to_individual.sh pr ckanext-spatial

# 3. Script creates a draft PR - edit description and submit!
```

## 📋 **Command Reference**

### Sync Script Commands

```bash
# Push all changes from monorepo to individual repos
./sync_monorepo_to_individual.sh push-all

# Push specific repo
./sync_monorepo_to_individual.sh push ckanext-spatial

# Show status of all repositories
./sync_monorepo_to_individual.sh status

# Create feature branch in all repos
./sync_monorepo_to_individual.sh branch feature/my-new-feature

# Create pull request (must be on feature branch)
./sync_monorepo_to_individual.sh pr ckanext-spatial

# Show help
./sync_monorepo_to_individual.sh help
```

## 🎯 **Best Practices**

### Development Workflow

1. **Always develop in monorepo** - easier testing, cross-extension dependencies
2. **Sync frequently** - don't let changes pile up
3. **Use feature branches** - one feature per branch across all repos
4. **Test in monorepo first** - ensure everything works together

### Git Hygiene

1. **Commit regularly** in individual repos after syncing
2. **Use descriptive commit messages**
3. **Keep feature branches focused** - one feature per branch
4. **Update from upstream** before starting new features

### PR Strategy

1. **Create draft PRs early** - get feedback on direction
2. **Update PR descriptions** - explain your changes thoroughly
3. **Test thoroughly** - include test cases
4. **Document changes** - update READMEs and docs

## 🔧 **Advanced Scenarios**

### Handling Conflicts

If you get merge conflicts when syncing:

```bash
# Check status
./sync_monorepo_to_individual.sh status

# Go to problematic repo
cd ../individual-repos/ckanext-spatial

# Resolve conflicts manually
git status
# Edit conflicted files...
git add .
git commit -m "Resolve sync conflicts"

# Continue with workflow
```

### Updating from Upstream

```bash
# Update all individual repos from upstream
for repo in ../individual-repos/*/; do
    cd "$repo"
    git fetch upstream
    git checkout main || git checkout master
    git merge upstream/main || git merge upstream/master
    git push origin main || git push origin master
    cd - > /dev/null
done
```

### Working with Multiple Features

```bash
# Create different feature branches for different work
./sync_monorepo_to_individual.sh branch feature/oauth2-integration
# Work on OAuth2...
git add . && git commit -m "OAuth2 work"

# Switch to different feature
./sync_monorepo_to_individual.sh branch feature/mobile-responsive
# Work on mobile UI...
git add . && git commit -m "Mobile UI improvements"
```

## 🚨 **Troubleshooting**

### "Repository not found" errors
- Ensure you've run `./refork_all_repos.sh` successfully
- Check your GitHub account has the forks

### "No changes to sync" but you made changes
- Verify you're working in the monorepo, not individual repos
- Check the monorepo path is correct

### Sync script fails
- Ensure both directories exist: `../ckan-monorepo` and `../individual-repos`
- Check Git working directories are clean
- Verify GitHub CLI is authenticated: `gh auth status`

### Permission denied on scripts
```bash
chmod +x scripts/*.sh
```

## 📈 **Workflow Example: Complete Feature**

Here's a complete example of implementing OAuth2 across multiple extensions:

```bash
# 1. Setup
cd CKAN-Modernization-20250721/scripts
./sync_monorepo_to_individual.sh branch feature/oauth2-integration

# 2. Develop in monorepo
cd ../ckan-monorepo

# Edit core CKAN for OAuth2 base
# Edit extensions/ckanext-spatial for OAuth2 spatial features  
# Edit extensions/ckanext-dcat for OAuth2 DCAT features

# 3. Test everything together
docker-compose up -d
# Test your OAuth2 implementation...

# 4. Sync all changes
cd ../scripts
./sync_monorepo_to_individual.sh push-all

# 5. Commit changes in individual repos
cd ../individual-repos
for repo in */; do
    cd "$repo"
    if [[ $(git status --porcelain) ]]; then
        git add .
        git commit -m "Add OAuth2 integration support"
        git push origin feature/oauth2-integration
    fi
    cd ..
done

# 6. Create PRs
cd ../scripts
./sync_monorepo_to_individual.sh pr ckan
./sync_monorepo_to_individual.sh pr ckanext-spatial
./sync_monorepo_to_individual.sh pr ckanext-dcat
```

## 🎉 **Success Metrics**

You'll know this workflow is working when:
- ✅ You can develop efficiently in the monorepo
- ✅ Changes sync automatically to individual repos
- ✅ PRs are created with one command
- ✅ No manual copy-paste between repositories
- ✅ All repos stay in sync and up-to-date

---

**Remember**: The monorepo is for development convenience, individual repos are for contributing back to the community! 💕 
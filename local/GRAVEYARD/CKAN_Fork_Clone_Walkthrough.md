# CKAN Forking & Cloning Walkthrough

## Pre-flight Checklist

### 1. Install GitHub CLI (if needed)
```bash
# macOS
brew install gh

# Ubuntu/Debian
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

### 2. Authenticate GitHub CLI
```bash
gh auth login
```
- Choose: GitHub.com
- Choose: HTTPS
- Choose: Login with a web browser
- Follow the browser prompts

### 3. Verify Authentication
```bash
gh auth status
```
You should see: "✓ Logged in to github.com as [your-username]"

## Option 1: Manual Process (Understanding What Happens)

### Step 1: Fork Each Repository on GitHub

Visit each repo and click "Fork" button:
1. https://github.com/ckan/ckan → Fork
2. https://github.com/ckan/ckanext-harvest → Fork  
3. https://github.com/ckan/ckanext-spatial → Fork
4. https://github.com/ckan/ckanext-qa → Fork
5. https://github.com/ckan/ckanext-issues → Fork
6. https://github.com/ckan/ckanext-scheming → Fork

After forking, you'll have:
- `[your-username]/ckan`
- `[your-username]/ckanext-harvest`
- etc.

### Step 2: Create Project Structure
```bash
# Create main project directory
mkdir CKAN-Modernization-Project
cd CKAN-Modernization-Project

# Create subdirectories
mkdir individual-repos
mkdir documentation
mkdir scripts
```

### Step 3: Clone Your Forks
```bash
cd individual-repos

# Clone each fork (replace YOUR_USERNAME with your GitHub username)
git clone git@github.com:YOUR_USERNAME/ckan.git
git clone git@github.com:YOUR_USERNAME/ckanext-harvest.git
git clone git@github.com:YOUR_USERNAME/ckanext-spatial.git
git clone git@github.com:YOUR_USERNAME/ckanext-qa.git
git clone git@github.com:YOUR_USERNAME/ckanext-issues.git
git clone git@github.com:YOUR_USERNAME/ckanext-scheming.git
```

### Step 4: Add Upstream Remotes
```bash
# For each repo, add the original CKAN repo as 'upstream'
cd ckan
git remote add upstream https://github.com/ckan/ckan.git
cd ..

cd ckanext-harvest
git remote add upstream https://github.com/ckan/ckanext-harvest.git
cd ..

# Repeat for all repos...
```

### Step 5: Create the Monorepo
```bash
cd .. # Back to project root
git init ckan-monorepo
cd ckan-monorepo

# Add repos as submodules
git submodule add ../individual-repos/ckan ckan
mkdir extensions
git submodule add ../individual-repos/ckanext-harvest extensions/ckanext-harvest
git submodule add ../individual-repos/ckanext-spatial extensions/ckanext-spatial
git submodule add ../individual-repos/ckanext-qa extensions/ckanext-qa
git submodule add ../individual-repos/ckanext-issues extensions/ckanext-issues
git submodule add ../individual-repos/ckanext-scheming extensions/ckanext-scheming

# Commit the monorepo structure
git add .
git commit -m "Initial CKAN monorepo with submodules"
```

## Option 2: Automated Process (Using the Script)

### Step 1: Make Script Executable
```bash
chmod +x setup_ckan_project.sh
```

### Step 2: Run the Script
```bash
./setup_ckan_project.sh
```

### What the Script Does:

1. **Checks Prerequisites**
   - ✓ Git installed?
   - ✓ GitHub CLI installed?
   - ✓ GitHub CLI authenticated?
   - ⚠️  cloc installed? (optional)

2. **Creates Project Structure**
   ```
   CKAN-Modernization-20241210/
   ├── individual-repos/
   ├── documentation/
   └── scripts/
   ```

3. **Forks & Clones Each Repo**
   - Checks if you already forked (won't duplicate)
   - Clones your fork locally
   - Adds upstream remote automatically

4. **Creates Monorepo**
   - Initializes git repo
   - Adds all repos as submodules
   - Creates README and .gitignore
   - Commits structure

5. **Counts Lines of Code**
   - Shows total LOC (should be ~1.2M)
   - Detailed breakdown if cloc is installed

6. **Creates Helper Scripts**
   - `update_all.sh` - Update from upstream
   - `create_feature.sh` - Create feature branches
   - `create_pr.sh` - Open pull requests

## After Setup: Verify Everything

### Check Your Forks on GitHub
Visit: https://github.com/YOUR_USERNAME?tab=repositories

You should see:
- ckan (forked from ckan/ckan)
- ckanext-harvest (forked from ckan/ckanext-harvest)
- etc.

### Check Local Structure
```bash
cd CKAN-Modernization-20241210
tree -L 2
```

Should show:
```
.
├── ckan-monorepo/
│   ├── ckan/
│   └── extensions/
├── documentation/
│   ├── ai_prompts_log.md
│   └── project_plan.md
├── individual-repos/
│   ├── ckan/
│   ├── ckanext-harvest/
│   └── ...
└── scripts/
    ├── create_feature.sh
    └── update_all.sh
```

### Verify LOC Count
```bash
cd ckan-monorepo
find . -name "*.py" -o -name "*.js" -o -name "*.html" | xargs wc -l
```

Should show: ~1,200,000+ total lines

## Common Issues & Fixes

### "Permission denied (publickey)"
```bash
# You're using SSH but haven't set up SSH keys
# Either switch to HTTPS or set up SSH keys:
gh auth refresh -s write:public_key
```

### "Repository already exists"
```bash
# You already forked this repo
# The script handles this, but manually you can:
gh repo view YOUR_USERNAME/ckan
```

### "gh: command not found"
```bash
# GitHub CLI not installed
# Go back to Pre-flight Checklist step 1
```

### Submodule issues
```bash
# If submodules get confused:
git submodule update --init --recursive
```

## Next Steps After Cloning

1. **Set up Python environment**
```bash
cd ckan-monorepo/ckan
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Run CKAN with Docker** (easier)
```bash
cd ckan-monorepo
# We'll create docker-compose.yml on Day 3
```

3. **Start Day 1 Archaeological Dig**
Open the Day_1_Architecture_Archaeology_Guide.md and begin!

---

*Pro tip: The automated script does all of this in about 2-3 minutes. But understanding the manual process helps when you need to debug or add more repos later!* 
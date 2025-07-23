# Git History Cleanup & Security Audit Guide

## 🚨 **Situation Summary**

**Secret Exposed**: `SECRET_KEY = [REDACTED-SECRET-REMOVED]`  
**First Committed**: commit `c0e1ad9` (July 22, 2025)  
**Repository**: Public GitHub repository  
**Origin**: Auto-generated during CKAN setup (not from upstream CKAN)

## 🔧 **Step 1: Remove Secret from Git History**

### Option A: Recent Commit - Interactive Rebase (Recommended)
```bash
# If the secret was introduced in recent commits
git rebase -i HEAD~5  # Adjust number based on how far back

# In the editor, change 'pick' to 'edit' for commit c0e1ad9
# When rebase stops at that commit:
git reset HEAD~1
# Fix the file (remove secret, use environment variable)
git add CKAN-Modernization-20250721/ckan-monorepo/ckan/ckan-test.ini
git commit -m "security: Use environment variable for SECRET_KEY"
git rebase --continue
```

### Option B: Filter-Branch (Nuclear Option)
```bash
# WARNING: This rewrites entire repository history
git filter-branch --force --env-filter '
    if [ "$GIT_COMMIT" = "c0e1ad9bd0b8a3c00f4ff8cc2bcfb52925f2791d" ]; then
        export GIT_AUTHOR_DATE="$(date)"
        export GIT_COMMITTER_DATE="$(date)"
    fi
' --tree-filter '
    if [ -f "CKAN-Modernization-20250721/ckan-monorepo/ckan/ckan-test.ini" ]; then
        sed -i "s/SECRET_KEY = [REDACTED]/SECRET_KEY = %(ENV_SECRET_KEY)s/g" CKAN-Modernization-20250721/ckan-monorepo/ckan/ckan-test.ini
    fi
' --prune-empty --tag-name-filter cat -- --all

# Clean up
git reset --hard
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --aggressive --prune=now
```

### Option C: BFG Repo-Cleaner (Safest)
```bash
# Install BFG (if you have Java)
# Download from: https://rtyley.github.io/bfg-repo-cleaner/

# Create a file with the secret
echo "[REDACTED-SECRET]" > secrets.txt

# Clean the repository
java -jar bfg.jar --replace-text secrets.txt --no-blob-protection .git

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

## 🔄 **Step 2: Force Push Changes**

⚠️ **WARNING**: This will rewrite public history. Coordinate with any collaborators!

```bash
# After history cleanup:
git push --force-with-lease origin main

# If that fails (others have pulled):
git push --force origin main
```

## 🔍 **Step 3: Session Invalidation**

Since the SECRET_KEY was exposed, any existing sessions could be compromised:

### Local Development
```bash
# Clear any local CKAN sessions/cookies
# In your browser: Clear cookies for localhost:5001
# Or programmatically:
docker-compose -f docker-compose.arm64.yml exec ckan ckan -c ckan-test.ini db clean
```

### If This Was Production (Hypothetical)
```bash
# Force all users to re-login
ckan -c production.ini user reset-sessions
# Or manually clear session storage (Redis/database)
```

## 📊 **Step 4: Access Auditing**

### GitHub Repository Access
```bash
# Check who has accessed your repository
curl -H "Authorization: token YOUR_GITHUB_TOKEN" \
     -H "Accept: application/vnd.github.v3+json" \
     https://api.github.com/repos/YOUR_USERNAME/REPO_NAME/traffic/views

# Check repository clones/downloads
curl -H "Authorization: token YOUR_GITHUB_TOKEN" \
     -H "Accept: application/vnd.github.v3+json" \
     https://api.github.com/repos/YOUR_USERNAME/REPO_NAME/traffic/clones
```

### Application Access Logs
```bash
# Check CKAN access logs (if any exist)
docker-compose -f docker-compose.arm64.yml logs ckan | grep -E "(login|session|auth)"

# Check for unusual database activity
docker-compose -f docker-compose.arm64.yml exec ckan-postgres psql -U ckan -c "
SELECT * FROM activity 
WHERE timestamp > '2025-07-22'::date 
ORDER BY timestamp DESC;"
```

### Network Security
```bash
# Check if your local CKAN was accessible externally
netstat -tulpn | grep :5001
lsof -i :5001

# Review firewall rules
sudo ufw status  # Linux
pfctl -sr        # macOS
```

## 🛡️ **Step 5: Implement Prevention Measures**

### Pre-commit Hooks
```bash
# Install git-secrets
git secrets --install
git secrets --register-aws

# Add custom patterns
git secrets --add 'SECRET_KEY.*[=:].*[A-Za-z0-9+/]{20,}'
git secrets --add --allowed 'SECRET_KEY.*%(ENV_.*'

# Scan existing repository
git secrets --scan-history
```

### GitHub Security
```bash
# Enable GitHub secret scanning alerts
# Go to: Settings > Security & analysis > Secret scanning
# Enable: "Secret scanning" and "Push protection"
```

### Environment Variables
```bash
# Set up proper environment management
echo 'ENV_SECRET_KEY=your-new-secret-here' > .env
echo '.env' >> .gitignore
echo '*.env' >> .gitignore
echo '!.env.example' >> .gitignore
```

## ✅ **Step 6: Verification Checklist**

- [ ] Secret removed from git history
- [ ] New secret generated and secured in environment variable
- [ ] Force push completed successfully
- [ ] Pre-commit hooks installed and tested
- [ ] GitHub security features enabled
- [ ] Team/collaborators notified of history rewrite
- [ ] All local environments updated with new secret
- [ ] Documentation updated with new security practices

## 🆘 **Emergency Contacts**

If you suspect the secret was actively exploited:
1. **Immediately** rotate all secrets
2. **Review** all recent activity logs
3. **Consider** taking the application offline temporarily
4. **Contact** your security team or GitHub support if needed

## 📝 **Timeline for This Incident**

- **July 22, 2025**: Secret first committed in `c0e1ad9`
- **July 23, 2025**: Secret detected by security monitoring
- **July 23, 2025**: Secret rotated and moved to environment variable
- **Next**: Git history cleanup (use this guide)

Remember: This was caught quickly, the secret was generated (not manually created), and no evidence of exploitation has been found. The risk is manageable with proper cleanup. 
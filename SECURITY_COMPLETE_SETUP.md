# 🔐 CKAN Complete Security Setup Guide

**This document provides a comprehensive security framework to prevent secret exposure in your CKAN project.**

---

## 🚨 **Why This Matters**

Your GitHub account has been suspended **twice** due to hardcoded secrets. This comprehensive system ensures it never happens again by:

1. **Preventing** secrets from being committed in the first place
2. **Detecting** any accidental secret exposure immediately  
3. **Managing** secrets securely across all environments
4. **Monitoring** for security vulnerabilities continuously

---

## 🎯 **Quick Start (5 Minutes)**

### 1. Generate Your Secrets
```bash
# Generate all required secrets automatically
./scripts/generate_secrets.sh
```

### 2. Install Pre-commit Hooks
```bash
# Install pre-commit (prevents secret commits)
pip install pre-commit
pre-commit install
```

### 3. Test the Security System
```bash
# This should be blocked by pre-commit hooks
echo "SECRET_KEY=test123" >> test_file.py
git add test_file.py
git commit -m "test" # This will FAIL - which is good!
rm test_file.py
```

### 4. Verify Your Setup
```bash
# Check that .env exists and is secure
ls -la .env  # Should show 600 permissions
head -3 .env # Should show generated secrets
```

---

## 📁 **File Structure Overview**

```
CKAN-Fork/
├── .env                    # 🔐 YOUR SECRETS (never commit!)
├── .env.example           # 📋 Template for others  
├── .gitignore             # 🚫 Prevents secret commits
├── .pre-commit-config.yaml # 🛡️ Automated security scanning
├── scripts/
│   └── generate_secrets.sh # 🔑 Secret generation tool
└── SECURITY_COMPLETE_SETUP.md # 📖 This guide
```

---

## 🔧 **Detailed Setup Instructions**

### **Step 1: Environment Variables System**

#### A. Use the Secret Generator (Recommended)
```bash
./scripts/generate_secrets.sh
```

#### B. Manual Setup (Advanced)
```bash
# Copy template
cp .env.example .env

# Generate secure secret
python3 -c "import secrets; print('ENV_SECRET_KEY=' + secrets.token_urlsafe(32))" >> .env

# Set secure permissions  
chmod 600 .env
```

### **Step 2: Pre-commit Security Hooks**

#### A. Install Pre-commit
```bash
# Using pip
pip install pre-commit

# Using conda
conda install -c conda-forge pre-commit

# Using homebrew (macOS)
brew install pre-commit
```

#### B. Install the Hooks
```bash
# Install hooks in your repository
pre-commit install

# Install hooks for all supported Git hooks
pre-commit install --install-hooks
```

#### C. Test the Security System
```bash
# This should FAIL (which means it's working!)
echo "SECRET_KEY=hardcoded_secret" > test_secret.py
git add test_secret.py
git commit -m "test commit"  # Will be blocked!

# Clean up
rm test_secret.py
```

### **Step 3: Docker Environment Integration**

Your `docker-compose.arm64.yml` is already configured to use environment variables:

```yaml
environment:
  ENV_SECRET_KEY: ${CKAN_SECRET_KEY:-test-secret-key-for-development-only}
```

To use your generated secrets with Docker:
```bash
# Export your secret for Docker
export CKAN_SECRET_KEY=$(grep ENV_SECRET_KEY .env | cut -d= -f2)

# Start CKAN with your secrets
docker-compose -f CKAN-Modernization-20250721/ckan-monorepo/ckan/test-infrastructure/docker-compose.arm64.yml up
```

---

## 🛡️ **Security Features Explained**

### **1. Multi-Layer Secret Detection**

| Tool | Purpose | When It Runs |
|------|---------|--------------|
| **detect-secrets** | Baseline secret scanning | Every commit |
| **trufflehog** | Advanced pattern detection | Every commit |
| **custom patterns** | CKAN-specific secrets | Every commit |
| **GitGuardian** | Cloud-based monitoring | Every push |

### **2. File Protection**

The `.gitignore` file prevents these sensitive files from being committed:
- `.env` and `.env.*` files
- `*.ini` files (except templates)
- `keys/`, `secrets/`, `certs/` directories
- Any file containing credentials

### **3. Automated Validation**

Pre-commit hooks check for:
- Hardcoded database URLs
- API keys and tokens
- AWS credentials
- Private keys
- Large files that might contain secrets

---

## 🔍 **How to Use Secrets in Your Code**

### **✅ CORRECT - Environment Variables**

```python
import os
from ckan.common import config

# In Python code
secret_key = os.environ.get('ENV_SECRET_KEY')
db_url = config.get('sqlalchemy.url')  # From CKAN config

# In CKAN config files (.ini)
SECRET_KEY = %(ENV_SECRET_KEY)s
sqlalchemy.url = %(CKAN_SQLALCHEMY_URL)s
```

### **❌ WRONG - Hardcoded Values**

```python
# NEVER DO THIS!
SECRET_KEY = "hardcoded-secret-example-never-do-this"
DATABASE_URL = "postgresql://user:password@localhost/db"
API_KEY = "sk-example-never-hardcode-keys"
```

---

## 🏗️ **Environment-Specific Setup**

### **Development Environment**
```bash
# Use the generated .env file
source .env  # Or let your IDE load it automatically
```

### **Testing Environment**
```bash
# Create separate test secrets
cp .env .env.test
# Modify .env.test with test-specific values
export ENV_SECRET_KEY=$(grep ENV_SECRET_KEY .env.test | cut -d= -f2)
```

### **Production Environment**
```bash
# Use a proper secret management service
# Examples:
export ENV_SECRET_KEY=$(aws secretsmanager get-secret-value --secret-id prod/ckan/secret-key --query SecretString --output text)
export ENV_SECRET_KEY=$(kubectl get secret ckan-secrets -o jsonpath='{.data.secret-key}' | base64 -d)
```

---

## 🔄 **Secret Rotation Process**

### **Monthly Rotation (Recommended)**

1. **Generate New Secrets**
   ```bash
   ./scripts/generate_secrets.sh
   ```

2. **Update All Environments**
   ```bash
   # Development
   source .env
   
   # Production (example)
   aws secretsmanager update-secret --secret-id prod/ckan/secret-key \
     --secret-string $(grep ENV_SECRET_KEY .env | cut -d= -f2)
   ```

3. **Restart Services**
   ```bash
   # Docker
   docker-compose restart
   
   # Kubernetes
   kubectl rollout restart deployment/ckan
   ```

4. **Verify Everything Works**
   ```bash
   curl -I http://localhost:5000  # Should return 200 OK
   ```

---

## 🚨 **Emergency Response Plan**

### **If Secrets Are Exposed:**

#### **Immediate Actions (< 5 minutes)**
1. **Rotate ALL secrets immediately**
   ```bash
   ./scripts/generate_secrets.sh
   source .env
   docker-compose restart
   ```

2. **Check git history**
   ```bash
   git log --all -S "EXPOSED_SECRET_HERE"
   ```

3. **Force push cleaned history** (if needed)
   ```bash
   # Only if secret is in recent commits
   git rebase -i HEAD~5  # Edit last 5 commits
   git push --force-with-lease
   ```

#### **Follow-up Actions (< 1 hour)**
1. **Audit access logs** for suspicious activity
2. **Invalidate all user sessions**
3. **Monitor for unusual API usage**
4. **Update incident documentation**

#### **Prevention Measures (< 24 hours)**
1. **Review and improve pre-commit hooks**
2. **Conduct team security training**
3. **Implement additional monitoring**

---

## 🧪 **Testing Your Security Setup**

### **Test 1: Pre-commit Hook Functionality**
```bash
# This should FAIL
echo 'SECRET_KEY = "hardcoded_secret"' > temp_test.py
git add temp_test.py
git commit -m "test" # Should be blocked!
rm temp_test.py
```

### **Test 2: Environment Variable Loading**
```bash
# This should show your actual secret (first 10 chars)
python3 -c "import os; print('Secret loaded:', os.environ.get('ENV_SECRET_KEY', 'NOT_FOUND')[:10] + '...')"
```

### **Test 3: CKAN Integration**
```bash
# Start CKAN and verify it uses environment variables
docker-compose -f CKAN-Modernization-20250721/ckan-monorepo/ckan/test-infrastructure/docker-compose.arm64.yml up -d
docker-compose logs ckan | grep -i secret # Should show environment variable reference
```

---

## 📊 **Security Checklist**

### **Initial Setup** ✅
- [ ] `.env` file created with secure secrets
- [ ] `.env` file has 600 permissions (`-rw-------`)
- [ ] Pre-commit hooks installed and tested
- [ ] `.gitignore` updated with security patterns
- [ ] Secret generation script is executable

### **Daily Development** ✅
- [ ] Never commit `.env` files
- [ ] Use `%(ENV_VAR_NAME)s` pattern in config files
- [ ] Test pre-commit hooks before important commits
- [ ] Check that secrets aren't in logs or error messages

### **Periodic Maintenance** ✅
- [ ] Rotate secrets monthly
- [ ] Update dependencies (pre-commit, tools)
- [ ] Review and update security documentation
- [ ] Audit team access and permissions

### **Emergency Preparedness** ✅
- [ ] Know how to rotate secrets quickly
- [ ] Have monitoring in place for secret exposure
- [ ] Document incident response procedures
- [ ] Test backup and recovery procedures

---

## 🔗 **Additional Resources**

### **Security Tools**
- [detect-secrets](https://github.com/Yelp/detect-secrets) - Secret detection
- [pre-commit](https://pre-commit.com/) - Git hook management
- [git-secrets](https://github.com/awslabs/git-secrets) - AWS-focused secret prevention

### **Secret Management Services**
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
- [Azure Key Vault](https://azure.microsoft.com/en-us/services/key-vault/)
- [HashiCorp Vault](https://www.vaultproject.io/)
- [Google Secret Manager](https://cloud.google.com/secret-manager)

### **Security Best Practices**
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [CKAN Security Guidelines](https://docs.ckan.org/en/latest/maintaining/security.html)

---

## 🎯 **Success Metrics**

Your security setup is working correctly when:

- ✅ Pre-commit hooks prevent secret commits
- ✅ No hardcoded secrets in any committed files
- ✅ Environment variables are used throughout
- ✅ `.env` files are never committed to git
- ✅ CKAN starts successfully with environment variables
- ✅ Team follows security procedures consistently
- ✅ Regular secret rotation occurs without issues

---

## 📞 **Need Help?**

If you encounter issues:

1. **Check the logs**: Most tools provide detailed error messages
2. **Test individual components**: Isolate the problem
3. **Review this documentation**: Ensure all steps were followed
4. **Check tool documentation**: Each tool has comprehensive guides

**Remember**: Security is an ongoing process, not a one-time setup! 🔐

---

*This security framework ensures your CKAN project follows industry best practices and prevents accidental secret exposure. Keep this documentation updated as your security needs evolve.* 
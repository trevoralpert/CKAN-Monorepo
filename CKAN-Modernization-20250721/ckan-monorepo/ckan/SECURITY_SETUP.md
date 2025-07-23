# CKAN Security Setup Guide

## 🚨 Secret Management Best Practices

### The Problem
Your security monitoring system correctly identified that the CKAN SECRET_KEY was exposed in the public repository. This is a serious security vulnerability.

### Why This Matters
- **Flask Session Security**: The SECRET_KEY signs session cookies and security tokens
- **Authentication Bypass**: Exposed keys allow attackers to forge valid sessions
- **Data Integrity**: Compromised keys can lead to unauthorized access

## ✅ Immediate Actions Taken

1. **✅ Replaced Exposed Key**: Changed to environment variable reference
2. **✅ Updated Configuration**: Now uses `%(ENV_SECRET_KEY)s` 

## 🔧 Required Setup Steps

### 1. Set Environment Variable

```bash
# Generate a new secret key
export ENV_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Or set it manually:
export ENV_SECRET_KEY="your-generated-secret-key-here"
```

### 2. Docker Environment Setup

Add to your docker-compose.arm64.yml environment section:

```yaml
services:
  ckan:
    environment:
      ENV_SECRET_KEY: ${ENV_SECRET_KEY}
      # ... other environment variables
```

### 3. Local Development

Create a `.env` file (never commit this!):
```bash
ENV_SECRET_KEY=tUcaKt0kEj9gT0rVZJW-Suzp-qgdbQ3VbJvIFo8K4Ro
```

Add to `.gitignore`:
```
.env
*.env
!.env.example
```

## 🔄 Git History Cleanup

The old secret is still in git history. To remove it:

```bash
# Option 1: Remove specific commit (if recent)
git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch ckan-test.ini' --prune-empty --tag-name-filter cat -- --all

# Option 2: Use git-secrets to prevent future exposure
git secrets --install
git secrets --register-aws
```

## 🛡️ Future Prevention

### 1. Pre-commit Hooks
```bash
pip install pre-commit
# Add secret scanning to .pre-commit-config.yaml
```

### 2. Environment Variable Pattern
Always use this pattern in config files:
```ini
SECRET_KEY = %(ENV_SECRET_KEY)s
DATABASE_URL = %(ENV_DATABASE_URL)s
API_KEY = %(ENV_API_KEY)s
```

### 3. Production Considerations
- Use AWS Secrets Manager, Azure Key Vault, or similar
- Rotate secrets regularly
- Monitor for secret exposure
- Use different secrets for different environments

## 🔍 Security Checklist

- [ ] SECRET_KEY changed and using environment variable
- [ ] Old secret removed from git history  
- [ ] .env files added to .gitignore
- [ ] Pre-commit hooks configured
- [ ] Team educated on secret management
- [ ] Production secrets using proper secret management service

## 📞 Emergency Response

If secrets are exposed:
1. **Immediately rotate** all exposed secrets
2. **Audit logs** for potential unauthorized access
3. **Update all environments** with new secrets
4. **Review and revoke** any sessions that may have been compromised
5. **Implement monitoring** for future exposures

Remember: **Security is everyone's responsibility!** 
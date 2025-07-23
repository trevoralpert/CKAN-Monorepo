#!/bin/bash

# CKAN Secret Generation Script
# This script generates secure random secrets for CKAN development
# Usage: ./scripts/generate_secrets.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'  
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔐 CKAN Secret Generation Script${NC}"
echo -e "${BLUE}=================================${NC}"
echo

# Check if .env already exists
if [[ -f ".env" ]]; then
    echo -e "${YELLOW}⚠️  .env file already exists!${NC}"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Aborted. Existing .env file preserved.${NC}"
        exit 1
    fi
    echo -e "${YELLOW}📝 Backing up existing .env to .env.backup$(date +%Y%m%d_%H%M%S)${NC}"
    cp .env ".env.backup$(date +%Y%m%d_%H%M%S)"
fi

# Function to generate secure random string
generate_secret() {
    local length=${1:-32}
    python3 -c "import secrets; print(secrets.token_urlsafe($length))"
}

# Function to generate secure password
generate_password() {
    local length=${1:-16}
    python3 -c "import secrets, string; chars=string.ascii_letters+string.digits+'!@#$%^&*'; print(''.join(secrets.choice(chars) for _ in range($length)))"
}

echo -e "${GREEN}🔑 Generating secure secrets...${NC}"
echo

# Generate secrets
SECRET_KEY=$(generate_secret 32)
DB_PASSWORD=$(generate_password 20)
SOLR_PASSWORD=$(generate_password 16) 
EMAIL_PASSWORD=$(generate_password 16)
AWS_ACCESS_KEY=$(generate_secret 20)
AWS_SECRET_KEY=$(generate_secret 40)

# Get user input for customizable values
echo -e "${BLUE}📝 Please provide the following information:${NC}"
echo

read -p "CKAN Site URL (default: http://localhost:5000): " SITE_URL
SITE_URL=${SITE_URL:-"http://localhost:5000"}

read -p "CKAN Site ID (default: default): " SITE_ID  
SITE_ID=${SITE_ID:-"default"}

read -p "Email address for SMTP (leave empty if not using): " SMTP_EMAIL

read -p "SMTP server (default: smtp.gmail.com): " SMTP_SERVER
SMTP_SERVER=${SMTP_SERVER:-"smtp.gmail.com"}

echo

# Create .env file
echo -e "${GREEN}📄 Creating .env file...${NC}"

cat > .env << EOF
# CKAN Environment Variables
# Generated on: $(date)
# DO NOT COMMIT THIS FILE TO VERSION CONTROL!

# =============================================================================
# SECURITY CRITICAL - Generated automatically
# =============================================================================

ENV_SECRET_KEY=${SECRET_KEY}

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

CKAN_SQLALCHEMY_URL=postgresql://ckan_default:${DB_PASSWORD}@localhost/ckan_default
CKAN_DATASTORE_WRITE_URL=postgresql://datastore_write:${DB_PASSWORD}@localhost/datastore_default  
CKAN_DATASTORE_READ_URL=postgresql://datastore_read:${DB_PASSWORD}@localhost/datastore_default

# =============================================================================
# SEARCH CONFIGURATION
# =============================================================================

CKAN_SOLR_URL=http://127.0.0.1:8983/solr/ckan
CKAN_SOLR_USER=solr_user
CKAN_SOLR_PASSWORD=${SOLR_PASSWORD}

# =============================================================================
# CACHE AND SESSION STORAGE
# =============================================================================

CKAN_REDIS_URL=redis://localhost:6379/0

# =============================================================================
# SITE CONFIGURATION
# =============================================================================

CKAN_SITE_ID=${SITE_ID}
CKAN_SITE_URL=${SITE_URL}
CKAN_STORAGE_PATH=/var/lib/ckan/default

# =============================================================================
# EMAIL CONFIGURATION
# =============================================================================

CKAN_SMTP_SERVER=${SMTP_SERVER}
CKAN_SMTP_STARTTLS=True
CKAN_SMTP_USER=${SMTP_EMAIL}
CKAN_SMTP_PASSWORD=${EMAIL_PASSWORD}
CKAN_SMTP_MAIL_FROM=${SMTP_EMAIL}

# =============================================================================
# DATA SERVICES
# =============================================================================

CKAN_DATAPUSHER_URL=http://datapusher:8800
CKAN_MAX_UPLOAD_SIZE_MB=50

# =============================================================================
# DEVELOPMENT SETTINGS
# =============================================================================

CKAN_DEBUG=False
FLASK_ENV=development

# =============================================================================
# AWS CREDENTIALS (Optional)
# =============================================================================

# AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY}
# AWS_SECRET_ACCESS_KEY=${AWS_SECRET_KEY}
# AWS_BUCKET_NAME=your-ckan-bucket

EOF

# Set secure permissions
chmod 600 .env

echo -e "${GREEN}✅ .env file created successfully!${NC}"
echo
echo -e "${YELLOW}🔐 Generated Secrets Summary:${NC}"
echo -e "   • Main Secret Key: ${SECRET_KEY:0:10}... (32 chars)"
echo -e "   • Database Password: ${DB_PASSWORD:0:5}... (20 chars)"  
echo -e "   • Solr Password: ${SOLR_PASSWORD:0:5}... (16 chars)"
echo -e "   • Email Password: ${EMAIL_PASSWORD:0:5}... (16 chars)"
echo

echo -e "${BLUE}📋 Next Steps:${NC}"
echo -e "   1. Review and customize the generated .env file"
echo -e "   2. Update your database with the new passwords"
echo -e "   3. Configure your email settings if needed"  
echo -e "   4. Test your CKAN installation"
echo

echo -e "${RED}⚠️  IMPORTANT SECURITY REMINDERS:${NC}"
echo -e "   • The .env file contains sensitive information"
echo -e "   • Never commit .env files to version control"
echo -e "   • Use different secrets for each environment"
echo -e "   • Rotate secrets regularly (quarterly recommended)"
echo -e "   • Store production secrets in a secure secret manager"
echo

echo -e "${GREEN}🎉 Secret generation completed!${NC}" 
#!/bin/bash

# Phase 3: Advanced Search & Discovery - Testing Setup Script
# Run this inside the CKAN Docker container

set -e

echo "🎯 Phase 3: Advanced Search & Discovery - Testing Setup"
echo "======================================================="
echo

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}📍 Current location: $(pwd)${NC}"
echo -e "${BLUE}📍 Python version: $(python --version)${NC}"
echo

# Step 1: Navigate to source directory
echo -e "${GREEN}Step 1: Navigating to source directory...${NC}"
cd /usr/src
echo -e "✅ Now in: $(pwd)"
echo

# Step 2: Install Phase 3 search-enhanced extension
echo -e "${GREEN}Step 2: Installing Phase 3 search-enhanced extension...${NC}"
if [ -d "./extensions/ckanext-search-enhanced" ]; then
    pip install -e ./extensions/ckanext-search-enhanced
    echo -e "✅ ckanext-search-enhanced installed"
else
    echo -e "${RED}❌ ckanext-search-enhanced directory not found${NC}"
    echo -e "${YELLOW}Available extensions:${NC}"
    ls -la extensions/ | grep ckanext
    exit 1
fi
echo

# Step 3: Install Phase 1 analytics extension (dependency)
echo -e "${GREEN}Step 3: Installing Phase 1 analytics extension...${NC}"
if [ -d "./extensions/ckanext-analytics" ]; then
    pip install -e ./extensions/ckanext-analytics
    echo -e "✅ ckanext-analytics installed"
else
    echo -e "${RED}❌ ckanext-analytics directory not found${NC}"
    exit 1
fi
echo

# Step 4: Install additional dependencies
echo -e "${GREEN}Step 4: Installing additional dependencies...${NC}"
pip install python-dateutil pyyaml redis ckanext-scheming
echo -e "✅ Additional dependencies installed"
echo

echo -e "${GREEN}🎉 Basic setup complete! Now copy this script to the container and run it.${NC}"

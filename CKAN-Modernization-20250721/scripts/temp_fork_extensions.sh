#!/bin/bash

# List of extensions that need forking
EXTENSIONS=(
    "ckanext-archiver"
    "ckanext-basiccharts" 
    "ckanext-bcgov"
    "ckanext-charts"
    "ckanext-cloudstorage"
    "ckanext-dashboard"
    "ckanext-datagovau"
    "ckanext-datajson"
    "ckanext-dcatde"
    "ckanext-disqus"
    "ckanext-doi"
    "ckanext-envvars"
    "ckanext-fluent"
    "ckanext-ga-report"
    "ckanext-geodatagov"
    "ckanext-geoview"
    "ckanext-googleanalytics"
    "ckanext-hierarchy"
    "ckanext-iati"
    "ckanext-ldap"
    "ckanext-mapviews"
    "ckanext-metrics_dashboard"
    "ckanext-oauth2"
    "ckanext-odata"
    "ckanext-privatedatasets"
    "ckanext-report"
    "ckanext-s3filestore"
    "ckanext-switzerland"
    "ckanext-udc"
    "ckanext-versioning"
    "ckanext-viewhelpers"
    "ckanext-xloader"
)

# Common organizations to try
ORGS=("ckan" "okfn" "datagovau" "datagovuk" "GSA" "IATI" "DataShades" "keitaroinc")

forked_repos=()
failed_repos=()

for ext in "${EXTENSIONS[@]}"; do
    echo "🔍 Trying to fork $ext..."
    forked=false
    
    for org in "${ORGS[@]}"; do
        if gh repo fork "$org/$ext" --clone=false 2>/dev/null; then
            echo "✅ Successfully forked $org/$ext"
            forked_repos+=("$org/$ext")
            forked=true
            break
        fi
    done
    
    if [ "$forked" = false ]; then
        echo "❌ Could not fork $ext from any organization"
        failed_repos+=("$ext")
    fi
done

echo ""
echo "📊 Fork Results:"
echo "✅ Successfully forked: ${#forked_repos[@]} repositories"
echo "❌ Failed to fork: ${#failed_repos[@]} repositories"

if [ ${#failed_repos[@]} -gt 0 ]; then
    echo ""
    echo "Failed repositories:"
    for repo in "${failed_repos[@]}"; do
        echo "  - $repo"
    done
fi

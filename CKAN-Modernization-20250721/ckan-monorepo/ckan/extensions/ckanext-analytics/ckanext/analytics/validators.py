import re
from ckan.common import _
import ckan.plugins.toolkit as toolkit


def email_validator(value):
    """Validate email address format"""
    if not value:
        return value
    
    # Basic email validation regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, value):
        raise toolkit.Invalid(_('Please enter a valid email address'))
    
    return value


def department_validator(value):
    """Validate department selection"""
    valid_departments = [
        'fire', 'police', 'public-works', 'finance', 'parks-recreation',
        'planning-zoning', 'water-utilities', 'health', 'transportation',
        'mayor-admin', 'other'
    ]
    
    if value not in valid_departments:
        raise toolkit.Invalid(_('Please select a valid department'))
    
    return value


def update_frequency_validator(value):
    """Validate update frequency selection"""
    valid_frequencies = [
        'real-time', 'daily', 'weekly', 'monthly', 'quarterly', 
        'annually', 'as-needed', 'one-time'
    ]
    
    if value not in valid_frequencies:
        raise toolkit.Invalid(_('Please select a valid update frequency'))
    
    return value


def data_quality_validator(value):
    """Validate data quality score"""
    valid_scores = ['high', 'medium', 'low', 'unknown']
    
    if value not in valid_scores:
        raise toolkit.Invalid(_('Please select a valid data quality score'))
    
    return value


def geographic_coverage_validator(value):
    """Validate geographic coverage selection"""
    valid_coverage = [
        'citywide', 'ward-district', 'neighborhood', 'address-specific', 
        'regional', 'other'
    ]
    
    if value not in valid_coverage:
        raise toolkit.Invalid(_('Please select a valid geographic coverage'))
    
    return value


def public_access_validator(value):
    """Validate public access level"""
    valid_levels = ['public', 'restricted', 'confidential']
    
    if value not in valid_levels:
        raise toolkit.Invalid(_('Please select a valid access level'))
    
    return value


def collection_method_validator(value):
    """Validate data collection method"""
    valid_methods = [
        'automated', 'manual-entry', 'survey', 'third-party', 
        'citizen-reported', 'other'
    ]
    
    if value not in valid_methods:
        raise toolkit.Invalid(_('Please select a valid collection method'))
    
    return value 
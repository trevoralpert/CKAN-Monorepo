#!/usr/bin/env python3
"""
Simple test to verify city dataset schema is loaded correctly
"""

import os
import sys
import yaml

def test_schema_structure():
    """Test that our schema file has the correct structure"""
    schema_path = "/usr/src/extensions/ckanext-scheming/ckanext/scheming/city_dataset_schema.yaml"
    
    try:
        with open(schema_path, 'r') as f:
            schema = yaml.safe_load(f)
        
        print("✅ Schema file loaded successfully")
        print(f"   Dataset type: {schema.get('dataset_type')}")
        print(f"   Fields count: {len(schema.get('dataset_fields', []))}")
        print(f"   Resource fields: {len(schema.get('resource_fields', []))}")
        
        # Check key fields exist
        field_names = [f['field_name'] for f in schema.get('dataset_fields', [])]
        required_fields = ['department', 'update_frequency', 'geographic_coverage', 'public_access_level']
        
        missing_fields = [f for f in required_fields if f not in field_names]
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        else:
            print("✅ All required city-specific fields present")
        
        # Check department choices
        dept_field = next((f for f in schema['dataset_fields'] if f['field_name'] == 'department'), None)
        if dept_field and dept_field.get('choices'):
            dept_count = len(dept_field['choices'])
            print(f"✅ Department field has {dept_count} choices")
        else:
            print("❌ Department field missing or no choices")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading schema: {e}")
        return False

def test_validator_import():
    """Test that our custom validators can be imported"""
    try:
        sys.path.insert(0, '/usr/src/extensions/ckanext-analytics')
        from ckanext.analytics import validators
        
        print("✅ Validators module imported successfully")
        
        # Test email validator
        test_email = validators.email_validator("test@city.gov")
        print(f"✅ Email validator working: {test_email}")
        
        # Test department validator  
        test_dept = validators.department_validator("fire")
        print(f"✅ Department validator working: {test_dept}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing validators: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing City Dataset Schema Implementation")
    print("=" * 50)
    
    schema_ok = test_schema_structure()
    print()
    
    validators_ok = test_validator_import()
    print()
    
    if schema_ok and validators_ok:
        print("🎉 All tests passed! City dataset schema is ready.")
        return 0
    else:
        print("💥 Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
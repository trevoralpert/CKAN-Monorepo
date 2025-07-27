#!/usr/bin/env python3
"""
CKAN 2.12.0a0 Configuration Fix
===============================

This script fixes the configuration loading issue in CKAN 2.12.0a0 by ensuring
the global config object is properly synced with the INI file before CKAN starts.

Usage: python startup_fix.py [config_file]
"""

import sys
import os
import logging

def fix_ckan_config(config_file='demo.ini'):
    """Fix CKAN configuration loading issue"""
    try:
        print(f"🔧 CKAN 2.12.0a0 Config Fix - Loading from {config_file}")
        
        # Import CKAN modules
        from ckan.cli import load_config
        from ckan.common import config as global_config
        
        # Load config from file
        if not os.path.exists(config_file):
            print(f"❌ Config file not found: {config_file}")
            return False
            
        fresh_config = load_config(config_file)
        print(f"✅ Loaded {len(fresh_config)} config values from {config_file}")
        
        # Sync with global config
        global_config.clear()
        global_config.update(fresh_config)
        
        # Verify sync worked
        plugins = global_config.get('ckan.plugins')
        scheming = global_config.get('scheming.dataset_schemas')
        
        print(f"✅ Plugins: {plugins}")
        print(f"✅ Scheming: {scheming}")
        
        if plugins and scheming:
            print("🎉 Config sync successful!")
            return True
        else:
            print("❌ Config sync incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Config fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'demo.ini'
    success = fix_ckan_config(config_file)
    sys.exit(0 if success else 1) 
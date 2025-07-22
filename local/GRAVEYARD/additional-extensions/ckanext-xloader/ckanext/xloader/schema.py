# encoding: utf-8

from six import text_type as str

import ckan.plugins as p
import ckanext.datastore.logic.schema as dsschema

get_validator = p.toolkit.get_validator

not_missing = get_validator('not_missing')
not_empty = get_validator('not_empty')
resource_id_exists = get_validator('resource_id_exists')
package_id_exists = get_validator('package_id_exists')
ignore_missing = get_validator('ignore_missing')
empty = get_validator('empty')
boolean_validator = get_validator('boolean_validator')
int_validator = get_validator('int_validator')
OneOf = get_validator('OneOf')
ignore_not_sysadmin = get_validator('ignore_not_sysadmin')
unicode_safe = get_validator('unicode_safe')


def xloader_submit_schema():
    schema = {
        'resource_id': [not_missing, not_empty, unicode_safe],
        'id': [ignore_missing],
        'set_url_type': [ignore_missing, boolean_validator],
        'ignore_hash': [ignore_missing, boolean_validator],
        'sync': [ignore_missing, boolean_validator, ignore_not_sysadmin],
        '__junk': [empty],
        '__before': [dsschema.rename('id', 'resource_id')]
    }
    return schema

from ckan import model
from ckan.plugins.toolkit import h, config

def dsaudit_resource_url(package_id, resource_id):
    pkg = model.Package.get(package_id)
    if not pkg:
        return '#'
    return h.url_for(
        pkg.type + '_resource.read',
        id=pkg.name,
        resource_id=resource_id,
    )

def dsaudit_data_columns(data):
    if data.get('fields'):
        return [f['id'] for f in data['fields']]
    if data.get('records'):
        return data['records'][0].keys()
    return []

def dsaudit_preview_records():
    return int(config.get('ckanext.dsaudit.preview_records', 12))

import os
import mock
import inspect
import nose.tools
import pylons.config as config

import ckan.plugins as p
import ckanext.mapviews.plugin as plugin


url_is_relative_or_in_same_domain = plugin.url_is_relative_or_in_same_domain
Invalid = p.toolkit.Invalid


def test_url_is_relative_or_in_same_domain_accepts_urls_on_same_domain():
    site_url = config.get('ckan.site_url')
    url = site_url + "/dataset/something"

    assert url_is_relative_or_in_same_domain(url) == url


def test_url_is_relative_or_in_same_domain_accepts_relative_urls():
    url = "/dataset/something"
    assert url_is_relative_or_in_same_domain(url) == url


@nose.tools.raises(Invalid)
def test_url_is_relative_or_in_same_domain_raises_if_not_on_the_same_domain():
    url_is_relative_or_in_same_domain("http://some-other-domain.com")


class TestNavigableMap(object):

    @classmethod
    def setup_class(cls):
        p.load('navigablemap')
        cls.plugin = p.get_plugin('navigablemap')

    @classmethod
    def teardown_class(cls):
        p.unload('navigablemap')

    def test_plugin_templates_path_is_added_to_config(self):
        filename = inspect.getfile(inspect.currentframe())
        path = os.path.dirname(filename)
        templates_path = os.path.abspath(path + "/../theme/templates")

        assert templates_path in config['extra_template_paths'], templates_path

    def test_can_view_is_true_when_datastore_is_active(self):
        active_datastore_data_dict = {
            'resource': { 'datastore_active': True }
        }
        assert self.plugin.can_view(active_datastore_data_dict)

    def test_can_view_is_false_when_datastore_is_inactive(self):
        inactive_datastore_data_dict = {
            'resource': { 'datastore_active': False }
        }
        assert not self.plugin.can_view(inactive_datastore_data_dict)

    def test_view_template_is_correct(self):
        view_template = self.plugin.view_template({}, {})
        assert view_template == 'navigablemap_view.html'

    def test_form_template_is_correct(self):
        form_template = self.plugin.form_template({}, {})
        assert form_template == 'navigablemap_form.html'

    def test_schema_exists(self):
        schema = self.plugin.info()['schema']
        assert schema is not None, 'Plugin should define schema'

    def test_schema_has_geojson_url(self):
        schema = self.plugin.info()['schema']
        assert schema.get('geojson_url') is not None, \
            'Schema should define "geojson_url"'

    def test_schema_geojson_url_isnt_empty(self):
        schema = self.plugin.info()['schema']
        not_empty = p.toolkit.get_validator('not_empty')
        assert not_empty in schema['geojson_url'], \
            '"geojson_url" should not be empty'

    def test_schema_geojson_url_is_relative_or_in_same_domain(self):
        schema = self.plugin.info()['schema']

        assert url_is_relative_or_in_same_domain in schema['geojson_url'], \
            '"geojson_url" should be relative or in same domain'

    def test_schema_has_geojson_key_field(self):
        schema = self.plugin.info()['schema']
        assert schema.get('geojson_key_field') is not None, \
            'Schema should define "geojson_key_field"'

    def test_schema_geojson_key_field_isnt_empty(self):
        schema = self.plugin.info()['schema']
        not_empty = p.toolkit.get_validator('not_empty')
        assert not_empty in schema['geojson_key_field'], \
            '"geojson_key_field" should not be empty'

    def test_schema_has_resource_key_field(self):
        schema = self.plugin.info()['schema']
        assert schema.get('resource_key_field') is not None, \
            'Schema should define "resource_key_field"'

    def test_schema_resource_key_field_isnt_empty(self):
        schema = self.plugin.info()['schema']
        not_empty = p.toolkit.get_validator('not_empty')
        assert not_empty in schema['resource_key_field'], \
            '"resource_key_field" should not be empty'

    def test_schema_has_resource_label_field(self):
        schema = self.plugin.info()['schema']
        assert schema.get('resource_label_field') is not None, \
            'Schema should define "resource_label_field"'

    def test_schema_resource_label_field_isnt_empty(self):
        schema = self.plugin.info()['schema']
        not_empty = p.toolkit.get_validator('not_empty')
        assert not_empty in schema['resource_label_field'], \
            '"resource_label_field" should not be empty'

    def test_schema_has_redirect_to_url(self):
        schema = self.plugin.info()['schema']
        assert schema.get('redirect_to_url') is not None, \
            'Schema should define "redirect_to_url"'

    def test_schema_redirect_to_url_isnt_required(self):
        schema = self.plugin.info()['schema']
        ignore_missing = p.toolkit.get_validator('ignore_missing')
        assert ignore_missing in schema['redirect_to_url'], \
            '"redirect_to_url" should not be required'

    def test_schema_has_filter_fields(self):
        schema = self.plugin.info()['schema']
        assert schema.get('filter_fields') is not None, \
            'Schema should define "filter_fields"'

    def test_schema_filter_fields_isnt_required(self):
        schema = self.plugin.info()['schema']
        ignore_missing = p.toolkit.get_validator('ignore_missing')
        assert ignore_missing in schema['filter_fields'], \
            '"filter_fields" should not be required'

    def test_plugin_isnt_iframed(self):
        iframed = self.plugin.info().get('iframed', True)
        assert not iframed, 'Plugin should not be iframed'

    @mock.patch('ckan.plugins.toolkit.get_action')
    def test_setup_template_variables_adds_resource(self, _):
        resource = {
            'id': 'resource_id',
        }

        template_variables = self._setup_template_variables(resource)

        assert 'resource' in template_variables
        assert template_variables['resource'] == resource

    @mock.patch('ckan.plugins.toolkit.get_action')
    def test_setup_template_variables_adds_resource_view(self, _):
        resource_view = {
            'id': 'resource_id',
            'other_attribute': 'value'
        }

        template_variables = \
            self._setup_template_variables(resource_view=resource_view)

        assert 'resource_view' in template_variables
        assert template_variables['resource_view'] == resource_view

    @mock.patch('ckan.plugins.toolkit.get_action')
    def test_setup_template_variables_resource_view_converts_filter_fields_to_list(self, _):
        resource_view = {
            'filter_fields': 'value'
        }

        template_variables = \
            self._setup_template_variables(resource_view=resource_view)

        resource_view = template_variables['resource_view']
        assert resource_view['filter_fields'] == ['value']

    @mock.patch('ckan.plugins.toolkit.get_action')
    def test_setup_template_variables_adds_geojson_resources(self, get_action):
        fields = [
            {
                'name': 'Map',
                'url': 'http://demo.ckan.org/map.json',
            }
        ]
        expected_fields = [{
            'text': 'Map',
            'value': 'http://demo.ckan.org/map.json'
        }]

        get_action.return_value.return_value = {
            'count': 1L,
            'results': fields
        }
        template_variables = self._setup_template_variables()

        returned_fields = template_variables.get('geojson_resources')
        assert returned_fields is not None
        assert returned_fields == expected_fields

    @mock.patch('ckan.plugins.toolkit.get_action')
    def test_setup_template_variables_adds_fields_without_the_id(self, get_action):
        fields = [
            {'id': '_id', 'type': 'int4'},
            {'id': 'price', 'type': 'numeric'},
        ]
        expected_fields = [{'value': 'price'}]

        get_action.return_value.return_value = {
            'fields': fields,
            'records': {}
        }
        template_variables = self._setup_template_variables()

        returned_fields = template_variables.get('fields')
        assert returned_fields is not None
        assert returned_fields == expected_fields

    @mock.patch('ckan.plugins.toolkit.get_action')
    def test_setup_template_variables_adds_numeric_fields(self, get_action):
        fields = [
            {'id': '_id', 'type': 'int4'},
            {'id': 'price', 'type': 'numeric'},
            {'id': 'name', 'type': 'text'}
        ]
        expected_fields = [{'value': 'price'}]

        get_action.return_value.return_value = {
            'fields': fields,
            'records': {}
        }
        template_variables = self._setup_template_variables()

        returned_fields = template_variables.get('numeric_fields')
        assert returned_fields is not None
        assert returned_fields == expected_fields

    @mock.patch('ckan.plugins.toolkit.get_action')
    def test_setup_template_variables_adds_textual_fields(self, get_action):
        fields = [
            {'id': '_id', 'type': 'int4'},
            {'id': 'price', 'type': 'numeric'},
            {'id': 'name', 'type': 'text'}
        ]
        expected_fields = [{'value': 'name'}]

        get_action.return_value.return_value = {
            'fields': fields,
            'records': {}
        }
        template_variables = self._setup_template_variables()

        returned_fields = template_variables.get('textual_fields')
        assert returned_fields is not None
        assert returned_fields == expected_fields

    @mock.patch('ckan.plugins.toolkit.get_action')
    def test_setup_template_variables_adds_default_filter_fields(self, get_action):
        template_variables = self._setup_template_variables()

        filter_fields = template_variables['resource_view'].get('filter_fields')
        assert filter_fields is not None
        assert filter_fields == []

    def _setup_template_variables(self, resource={'id': 'id'}, resource_view={}):
        context = {}
        data_dict = {
            'resource': resource,
            'resource_view': resource_view
        }
        return self.plugin.setup_template_variables(context, data_dict)


class TestChoroplethMap(object):

    @classmethod
    def setup_class(cls):
        p.load('choroplethmap')
        cls.plugin = p.get_plugin('choroplethmap')

    @classmethod
    def teardown_class(cls):
        p.unload('choroplethmap')

    def test_view_template_is_correct(self):
        view_template = self.plugin.view_template({}, {})
        assert view_template == 'choroplethmap_view.html'

    def test_form_template_is_correct(self):
        form_template = self.plugin.form_template({}, {})
        assert form_template == 'choroplethmap_form.html'

    def test_schema_has_resource_value_field(self):
        schema = self.plugin.info()['schema']
        assert schema.get('resource_value_field') is not None, \
            'Schema should define "resource_value_field"'

    def test_schema_resource_value_field_isnt_empty(self):
        schema = self.plugin.info()['schema']
        not_empty = p.toolkit.get_validator('not_empty')
        assert not_empty in schema['resource_value_field'], \
            '"resource_value_field" should not be empty'

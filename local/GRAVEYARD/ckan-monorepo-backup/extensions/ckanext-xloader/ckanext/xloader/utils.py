# encoding: utf-8

import json
import datetime
import re

from six import text_type as str, binary_type

from ckan import model
from ckan.lib import search
from collections import defaultdict
from decimal import Decimal

import ckan.plugins as p
from ckan.plugins.toolkit import config, h, _

from .job_exceptions import JobError

from logging import getLogger


log = getLogger(__name__)

from urllib.parse import urlunparse, urlparse

# resource.formats accepted by ckanext-xloader. Must be lowercase here.
DEFAULT_FORMATS = [
    "csv",
    "application/csv",
    "xls",
    "xlsx",
    "tsv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "ods",
    "application/vnd.oasis.opendocument.spreadsheet",
]


class XLoaderFormats(object):
    formats = None

    @classmethod
    def is_it_an_xloader_format(cls, format_):
        if cls.formats is None:
            cls._formats = config.get("ckanext.xloader.formats")
            if cls._formats is not None:
                # use config value. preserves empty list as well.
                cls._formats = cls._formats.lower().split()
            else:
                cls._formats = DEFAULT_FORMATS
        if not format_:
            return False
        return format_.lower() in cls._formats


def requires_successful_validation_report():
    return p.toolkit.asbool(config.get('ckanext.xloader.validation.requires_successful_report', False))


def awaiting_validation(res_dict):
    """
    Checks the existence of a logic action from the ckanext-validation
    plugin, thus supporting any extending of the Validation Plugin class.

    Checks ckanext.xloader.validation.requires_successful_report config
    option value.

    Checks ckanext.xloader.validation.enforce_schema config
    option value. Then checks the Resource's validation_status.
    """
    if not requires_successful_validation_report():
        # validation.requires_successful_report is turned off, return right away
        return False

    try:
        # check for one of the main actions from ckanext-validation
        # in the case that users extend the Validation plugin class
        # and rename the plugin entry-point.
        p.toolkit.get_action('resource_validation_show')
        is_validation_plugin_loaded = True
    except KeyError:
        is_validation_plugin_loaded = False

    if not is_validation_plugin_loaded:
        # the validation plugin is not loaded but required, log a warning
        log.warning('ckanext.xloader.validation.requires_successful_report requires the ckanext-validation plugin to be activated.')
        return False

    if (p.toolkit.asbool(config.get('ckanext.xloader.validation.enforce_schema', True))
            or res_dict.get('schema', None)) and res_dict.get('validation_status', None) != 'success':

        # either validation.enforce_schema is turned on or it is off and there is a schema,
        # we then explicitly check for the `validation_status` report to be `success``
        return True

    # at this point, we can assume that the Resource is not waiting for Validation.
    # or that the Resource does not have a Validation Schema and we are not enforcing schemas.
    return False


def resource_data(id, resource_id, rows=None):

    if p.toolkit.request.method == "POST":

        context = {
            "ignore_auth": True,
        }
        resource_dict = p.toolkit.get_action("resource_show")(
            context,
            {
                "id": resource_id,
            },
        )

        if awaiting_validation(resource_dict):
            h.flash_error(_("Cannot upload resource %s to the DataStore "
                            "because the resource did not pass validation yet.") % resource_id)
            return p.toolkit.redirect_to(
                "xloader.resource_data", id=id, resource_id=resource_id
            )

        try:
            p.toolkit.get_action("xloader_submit")(
                None,
                {
                    "resource_id": resource_id,
                    "ignore_hash": True,  # user clicked the reload button
                },
            )
        except p.toolkit.ValidationError:
            pass

        return p.toolkit.redirect_to(
            "xloader.resource_data", id=id, resource_id=resource_id
        )

    try:
        pkg_dict = p.toolkit.get_action("package_show")(None, {"id": id})
        resource = p.toolkit.get_action("resource_show")(None, {"id": resource_id})
    except (p.toolkit.ObjectNotFound, p.toolkit.NotAuthorized):
        return p.toolkit.abort(404, p.toolkit._("Resource not found"))

    try:
        xloader_status = p.toolkit.get_action("xloader_status")(
            None, {"resource_id": resource_id}
        )
    except p.toolkit.ObjectNotFound:
        xloader_status = {}
    except p.toolkit.NotAuthorized:
        return p.toolkit.abort(403, p.toolkit._("Not authorized to see this page"))

    extra_vars = {
        "status": xloader_status,
        "resource": resource,
        "pkg_dict": pkg_dict,
    }
    if rows:
        extra_vars["rows"] = rows
    return p.toolkit.render(
        "xloader/resource_data.html",
        extra_vars=extra_vars,
    )


def get_xloader_user_apitoken():
    """ Returns the API Token for authentication.

    xloader actions require an authenticated user to perform the actions. This
    method returns the api_token set in the config file and defaults to the
    site_user.
    """
    api_token = p.toolkit.config.get('ckanext.xloader.api_token')
    if api_token and api_token != 'NOT_SET':
        return api_token
    raise p.toolkit.ValidationError({u'ckanext.xloader.api_token': u'NOT_SET, please provide valid api token'})



def _modify_url(input_url: str, base_url: str) -> str:
    """ Modifies the input URL with base_url provided.

    Args:
        input_url (str): The original URL to potentially modify
        base_url (str): The base URL to compare/replace against
    Returns:
        str: The modified URL with replaced scheme and netloc
    """
    parsed_input_url = urlparse(input_url)
    parsed_base_url = urlparse(base_url)
    # Do not modify non-HTTP(S) URLs (e.g., ftp://)
    if parsed_input_url.scheme not in ("http", "https"):
        return input_url
    # replace scheme: "http/https" and netloc:"//<user>:<password>@<host>:<port>/<url-path>"
    new_url = urlunparse(
    (parsed_base_url.scheme,
     parsed_base_url.netloc,
     parsed_input_url.path,
     parsed_input_url.params,
     parsed_input_url.query,
     parsed_input_url.fragment))
    return new_url


def modify_input_url(input_url: str) -> str:
    """Returns a potentially modified CKAN URL.

    This function takes a possible CKAN URL and potentially modifies its base URL while preserving the path,
    query parameters, and fragments. The modification occurs only if three conditions are met:
    1. The base URL of the input matches the configured CKAN site URL (ckan.site_url).
    2. A `ckanext.xloader.site_url` is configured in the settings.
    3. A `ckanext.xloader.site_url_ignore_path_regex` if configured in the settings and does not match.

    Args:
        input_url (str): The original CKAN URL to potentially modify
    Returns:
        str: Either the modified URL with new base URL from xloader_site_url,
             or the original URL if conditions aren't met
    """

    xloader_site_url = config.get('ckanext.xloader.site_url')
    if not xloader_site_url:
        return input_url

    parsed_input_url = urlparse(input_url)
    input_base_url = f"{parsed_input_url.scheme}://{parsed_input_url.netloc}"
    parsed_ckan_site_url = urlparse(config.get('ckan.site_url'))
    ckan_base_url = f"{parsed_ckan_site_url.scheme}://{parsed_ckan_site_url.netloc}"

    xloader_ignore_regex = config.get('ckanext.xloader.site_url_ignore_path_regex')

    #Don't alter non-matching base url's.
    if input_base_url != ckan_base_url:
        return input_url
    #And not any urls on the ignore regex
    elif xloader_ignore_regex and re.search(xloader_ignore_regex, input_url):
        return input_url

    return _modify_url(input_url, xloader_site_url)


def set_resource_metadata(update_dict):
    '''
    Set appropriate datastore_active flag on CKAN resource.

    Called after creation or deletion of DataStore table.
    '''
    # We're modifying the resource extra directly here to avoid a
    # race condition, see issue #3245 for details and plan for a
    # better fix

    q = model.Session.query(model.Resource). \
        with_for_update(of=model.Resource). \
        filter(model.Resource.id == update_dict['resource_id'])
    resource = q.one()

    # update extras in database for record
    extras = resource.extras
    extras.update(update_dict)
    q.update({'extras': extras}, synchronize_session=False)

    model.Session.commit()

    # get package with updated resource from solr
    # find changed resource, patch it and reindex package
    psi = search.PackageSearchIndex()
    solr_query = search.PackageSearchQuery()
    q = {
        'q': 'id:"{0}"'.format(resource.package_id),
        'fl': 'data_dict',
        'wt': 'json',
        'fq': 'site_id:"%s"' % p.toolkit.config.get('ckan.site_id'),
        'rows': 1
    }
    for record in solr_query.run(q)['results']:
        solr_data_dict = json.loads(record['data_dict'])
        for resource in solr_data_dict['resources']:
            if resource['id'] == update_dict['resource_id']:
                resource.update(update_dict)
                psi.index_package(solr_data_dict)
                break


def column_count_modal(rows):
    """ Return the modal value of columns in the row_set's
    sample. This can be assumed to be the number of columns
    of the table.

    Copied from messytables.
    """
    counts = defaultdict(int)
    for row in rows:
        length = len([c for c in row if c != ''])
        if length > 1:
            counts[length] += 1
    if not len(counts):
        return 0
    return max(list(counts.items()), key=lambda k_v: k_v[1])[0]


def headers_guess(rows, tolerance=1):
    """ Guess the offset and names of the headers of the row set.
    This will attempt to locate the first row within ``tolerance``
    of the mode of the number of rows in the row set sample.

    The return value is a tuple of the offset of the header row
    and the names of the columns.

    Copied from messytables.
    """
    rows = list(rows)
    modal = column_count_modal(rows)
    for i, row in enumerate(rows):
        length = len([c for c in row if c != ''])
        if length >= modal - tolerance:
            # TODO: use type guessing to check that this row has
            # strings and does not conform to the type schema of
            # the table.
            return i, row
    return 0, []


TYPES = [int, bool, str, binary_type, datetime.datetime, float, Decimal]


def type_guess(rows, types=TYPES, strict=False):
    """ The type guesser aggregates the number of successful
    conversions of each column to each type, weights them by a
    fixed type priority and select the most probable type for
    each column based on that figure. It returns a list of
    ``CellType``. Empty cells are ignored.

    Strict means that a type will not be guessed
    if parsing fails for a single cell in the column."""
    guesses = []
    if strict:
        at_least_one_value = []
        for ri, row in enumerate(rows):
            diff = len(row) - len(guesses)
            for _i in range(diff):
                typesdict = {}
                for type in types:
                    typesdict[type] = 0
                guesses.append(typesdict)
                at_least_one_value.append(False)
            for ci, cell in enumerate(row):
                if not cell:
                    continue
                for type in list(guesses[ci].keys()):
                    if not isinstance(cell, type):
                        guesses[ci].pop(type)
                at_least_one_value[ci] = True if guesses[ci] else False
        # no need to set guessing weights before this
        # because we only accept a type if it never fails
        for i, guess in enumerate(guesses):
            for type in guess:
                guesses[i][type] = 1
        # in case there were no values at all in the column,
        # we just set the guessed type to string
        for i, v in enumerate(at_least_one_value):
            if not v:
                guesses[i] = {str: 1}
    else:
        for i, row in enumerate(rows):
            diff = len(row) - len(guesses)
            for _i in range(diff):
                guesses.append(defaultdict(int))
            for i, cell in enumerate(row):
                # add string guess so that we have at least one guess
                guesses[i][str] = guesses[i].get(str, 1)
                if not cell:
                    continue
                for type in types:
                    if isinstance(cell, type):
                        guesses[i][type] += 1
        _columns = []
    _columns = []
    for guess in guesses:
        # this first creates an array of tuples because we want the types to be
        # sorted. Even though it is not specified, python chooses the first
        # element in case of a tie
        # See: http://stackoverflow.com/a/6783101/214950
        guesses_tuples = [(t, guess[t]) for t in types if t in guess]
        if not guesses_tuples:
            raise JobError('Failed to guess types')
        _columns.append(max(guesses_tuples, key=lambda t_n: t_n[1])[0])
    return _columns


def datastore_resource_exists(resource_id):
    context = {'model': model, 'ignore_auth': True}
    try:
        response = p.toolkit.get_action('datastore_search')(context, dict(
            id=resource_id, limit=0))
    except p.toolkit.ObjectNotFound:
        return False
    return response or {'fields': []}

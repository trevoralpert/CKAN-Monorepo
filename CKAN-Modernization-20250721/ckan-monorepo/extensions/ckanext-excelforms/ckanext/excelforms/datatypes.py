from six import text_type

import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

from ckanext.excelforms.errors import BadExcelData


def canonicalize(
        dirty, dstore_tag, primary_key, choice_field=False):
    """
    Canonicalize dirty input from xlrd to align with
    recombinant.json datastore type specified in dstore_tag.

    Except for "=" Excel functions the purpose of this function is not
    to validate the data, just help format it so that it's more likely
    to be accepted when loaded into the datastore, and refuse to
    pass NULL values as parts of a primary key.

    :param dirty: dirty cell content as read through xlrd
    :type dirty: object
    :param dstore_tag: datastore_type specifier in (JSON) schema for cell
    :type dstore_tag: str
    :param primary_key: True if this field is part of the PK
    :type primary_key: bool
    :padam choice_field: 'full' if this field is a full-text choice field,
        True if this is a normal choice field, False otherwise
    :type choice_field: 'full', True or False

    :return: Canonicalized cell input
    :rtype: unicode, None or list of unicode values (_text)

    Raises BadExcelData on formula cells
    """
    if dirty is None:
        # use common value for blank cells
        dirty = u""

    if isinstance(dirty, text_type):
        if not dirty.strip():
            # whitespace-only values
            dirty = u""
        # excel, you keep being you
        if dirty == u'=FALSE()':
            dirty = u'FALSE'
        elif dirty == u'=TRUE()':
            dirty = u'TRUE'
        if dirty.startswith('='):
            raise BadExcelData('Formulas are not supported')

    if dstore_tag == '_text':
        dirty = text_type(dirty)
        if not dirty.strip():
            return []
        return [s.strip() for s in text_type(dirty).split(',')]

    if 'int' in dstore_tag:  # bigint, int4 etc.
        canon = re.sub(r'[$,\s]', '', text_type(dirty))
        try:
            d = Decimal(canon)
            if not d % 1:  # truncate trailing .00's
                return text_type(d // 1)
        except InvalidOperation:
            pass

    if dstore_tag == 'money':
        # User has overridden Excel format string, probably adding currency
        # markers or digit group separators (e.g.,fr-CA uses 1$ (not $1)).
        # Accept only "DDDDD.DD", discard other characters
        canon = re.sub(r'[$,\s]', '', text_type(dirty))
        try:
            d = Decimal(canon)
            return text_type(d)
        except InvalidOperation:
            pass

    if dstore_tag == 'date' and isinstance(dirty, datetime):
        return u'%04d-%02d-%02d' % (dirty.year, dirty.month, dirty.day)

    dirty = text_type(dirty)

    if choice_field == 'full':  # "code:full-text" style, just need code
        dirty = dirty.split(':')[0].strip()
    elif choice_field:
        dirty = dirty.strip()

    # accidental control characters and whitespace around primary keys
    # leads to unpleasantness
    if primary_key:
        dirty = dirty.strip()
        dirty = re.sub(u'[\x00-\x1f]', '', dirty)

    if dstore_tag != 'text' and not primary_key and not dirty:
        return None
    return dirty

# -*- coding: utf-8 -*-
import six
from six.moves.urllib.parse import (
        quote, quote_plus, unquote, unquote_plus, urlparse,
        urlencode as original_urlencode)

from features.util.encoding import force_str

def urlencode(query, doseq=0):
    """
    A version of Python's urllib.urlencode() function that can operate on
    unicode strings. The parameters are first cast to UTF-8 encoded strings and
    then encoded as per normal.
    """
    if hasattr(query, 'items'):
        query = query.items()

    return original_urlencode(
        [(force_str(k),
         [force_str(i) for i in v] if isinstance(v, (list,tuple)) else force_str(v))
            for k, v in query],
        doseq)
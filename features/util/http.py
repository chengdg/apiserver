# -*- coding: utf-8 -*-


import six
from six.moves.urllib.parse import (
        quote, quote_plus, unquote, unquote_plus, urlparse,
        urlencode as original_urlencode)

import urllib, urllib2
from features.util.encoding import force_str
import json

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
            
import logging
def request(url, data, method):
    data = urllib.urlencode(data)
    print data
    if method == "post":
        req = urllib2.Request(
            url, data)
        
    else:
        # data = urllib.urlencode(data)
        url = url + "&" + data
        req = urllib2.Request(url)
    response = urllib2.urlopen(req).read()
    logging.info('<<<>>>>>>>1')
    logging.info(response)
    logging.info('<<<>>>>>>>2')
    return json.loads(response)


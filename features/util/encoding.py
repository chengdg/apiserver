# -*- coding: utf-8 -*-


import six

def force_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to smart_bytes, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if not isinstance(s, (unicode, str)):
        s = str(s)

    if not isinstance(s, bytes):
        return s.encode(encoding, errors)
    else:
        return s

    # if isinstance(s, six.memoryview):
    #     s = bytes(s)
    # if isinstance(s, bytes):
    #     if encoding == 'utf-8':
    #         return s
    #     else:
    #         return s.decode('utf-8', errors).encode(encoding, errors)
    # if strings_only and (s is None or isinstance(s, int)):
    #     return s
    # if isinstance(s, Promise):
    #     return six.text_type(s).encode(encoding, errors)
    # if not isinstance(s, six.string_types):
    #     try:
    #         if six.PY3:
    #             return six.text_type(s).encode(encoding)
    #         else:
    #             return bytes(s)
    #     except UnicodeEncodeError:
    #         if isinstance(s, Exception):
    #             # An Exception subclass containing non-ASCII data that doesn't
    #             # know how to print itself properly. We shouldn't raise a
    #             # further exception.
    #             return b' '.join([force_bytes(arg, encoding, strings_only,
    #                     errors) for arg in s])
    #         return six.text_type(s).encode(encoding, errors)
    # else:
    #     return s.encode(encoding, errors)

force_bytes = force_str
# -*- coding: utf-8 -*-
"""
使用redis构建的锁

"""
import uuid

import math

from core.cache.utils import r
from core.exceptionutil import unicode_full_stack
from core.watchdog.utils import watchdog_alert

DEFAULT_CONN = r


def get_wapi_lock(lockname, lock_timeout=1):
	try:
		conn = DEFAULT_CONN
		identifier = '1'
		lockname = 'lock:' + lockname
		lock_timeout = int(math.ceil(lock_timeout))
		if conn.set(name=lockname, value=identifier, nx=True, ex=lock_timeout):
			return identifier
		else:
			return False
	except:
		watchdog_alert(unicode_full_stack())
		return True



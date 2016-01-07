# -*- coding: utf-8 -*-
"""
基于MySQL的watchdog存储
"""

from datetime import datetime
#import json
#import settings
#from pymongo import Connection
import logging
from .models import Message, WeappMessage

"""
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weapp.settings")
"""

class MySQLWatchdog(object):
	"""
	基于MySQL的watchdog
	"""

	def __init__(self):
		#self.connection = None
		#self.db = None
		#self.connect(settings.WATCHDOG_CONFIG['SERVER_HOST'], settings.WATCHDOG_CONFIG['SERVER_PORT'], settings.WATCHDOG_CONFIG['DATABASE'])
		pass
		
	#def get_now(self):
	#	return datetime.now().strftime('%Y-%m-%d %H:%M:%S')		

	def log(self, level, source, message, detail, account_info=''):
		"""
		记录WAPI的信息
		"""
		try:
			#created_at = self.get_now()
			Message.create(type=source, message=message, severity=level, user_id=account_info)
		except Exception as e:
			logging.info("level:{}, source:{}, message:{}, detail:{}, account_info:{}".format(level, source, message, detail, account_info))
			logging.error('Exception: {}'.format(str(e)))
		return

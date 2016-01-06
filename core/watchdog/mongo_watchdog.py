# -*- coding: utf-8 -*-
"""
需要 pymongo 2.5
```
pip install "pymongo==2.5"
```

"""

from datetime import datetime
import json
import settings
from pymongo import Connection
import logging

"""
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weapp.settings")
"""

class MongoWatchdog(object):
	"""
	基于MongoDB的watchdog
	"""

	def __init__(self):
		self.connection = None
		self.db = None
		self.connect(settings.WATCHDOG_CONFIG['SERVER_HOST'], settings.WATCHDOG_CONFIG['SERVER_PORT'], settings.WATCHDOG_CONFIG['DATABASE'])

	def connect(self, host, port, db):
		self.connection = Connection(host, port)
		self.db = self.connection[db]

	def get_now(self):
		return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	def params_to_str(self, params):
		"""
		将params转成字符串
		"""
		try:
			str = json.dumps(params)
		except:
			# params有时是QueryDict对象
			str = '{}'.format(params)
		return str

	def log(self, level, source, message, detail, account_info=''):
		"""
		记录WAPI的信息
		"""
		try:
			created_at = self.get_now()
			record = {
				'level': level,
				'source': source,
				'message': message,
				'detail': detail,
				'created_at': created_at,
				'account_info': account_info,
			}
			self.db.log.insert(record)
		except Exception as e:
			logging.info("level:{}, source:{}, message:{}, detail:{}, account_info:{}".format(level, source, message, detail, account_info))
			logging.error('Exception: {}'.format(str(e)))
			# 重连数据库
			#self.connect(settings.WATCHDOG_CONFIG['SERVER_HOST'], settings.WATCHDOG_CONFIG['SERVER_PORT'], settings.WATCHDOG_CONFIG['DATABASE'])
			#self.log(level, source, message, detail, account_info)
		return

if __name__=="__main__":
	log = MongoWatchdog()
	#log.log("dev", "test", {"param1":"hello", "param2":"world"}, 1)

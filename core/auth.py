# -*- coding: utf-8 -*-

class UserProfile:
	"""
	模拟webapp_owner_user_profile，用于cache调用
	"""
	def __init__(self, webapp_id=0, user_id=0):
		self.webapp_id = webapp_id
		self.user_id = user_id


class DummyRequest(object):
	"""
	模拟Django Request
	"""
	def __init__(self):
		pass

class DummyModel(object):
	"""
	模拟数据库Model
	"""

	def __init__(self):
		pass

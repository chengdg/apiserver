#coding: utf8
"""@package business.wzcard.wzcard_resource
微众卡资源

"""

from business import model as business_model
from wapi.decorators import param_required

class WZCardResource(business_model.Resource):
	"""
	已分配的微众卡资源
	"""
	__slots__ = (
		'type',
		'used_wzcards',
	)

	@staticmethod
	@param_required([])
	def get(args):
		"""
		工厂方法，创建WZCardResource
		"""
		return None


	def __init__(self, type, used_wzcards):
		business_model.Resource.__init__(self)
		
		self.used_wzcards = used_wzcards
		self.type = type

	def get_type(self):
		return self.type
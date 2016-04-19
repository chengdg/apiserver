#coding: utf8
"""@package business.wzcard.wzcard_resource
表示已分配的微众卡资源

"""

from business import model as business_model
#from eaglet.decorator import param_required

class WZCardResource(business_model.Resource):
	"""
	已分配的微众卡资源
	"""
	__slots__ = (
		'type',
		'used_wzcards',
	)


	def __init__(self, type, used_wzcards):
		"""
		根据type和used_wzcards构造WZCardResource

		"""
		business_model.Resource.__init__(self)
		
		self.used_wzcards = used_wzcards
		self.type = type


	def get_type(self):
		return self.type

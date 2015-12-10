#coding: utf8
"""@package business.wzcard.wzcard_resource_allocator
微众卡资源分配器
"""

from business import model as business_model

class WZCardAllocator(business_model.Service):
	"""
	微众卡资源分配器
	"""
	__slots__ = (
		)
	
	def __init__(self, webapp_owner, webapp_user):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user			

	def release(self, resources):
		"""
		释放微众卡资源
		"""
		pass

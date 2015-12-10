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
		business_model.Service.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user			


	def allocate_resource(self, order, purchase_info):
		"""
		分配微众卡资源

		@note 流程：(1) 获取微众卡信息；(2) 依次扣除微众卡金额；(3) 返回微众卡资源
		"""
		pass


	def release(self, resources):
		"""
		释放微众卡资源

		@note 退回微众卡账户
		"""
		pass

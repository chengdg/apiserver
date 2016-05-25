# coding: utf8
"""@package business.wzcard.wzcard_resource
表示已分配的微众卡资源

"""

from business import model as business_model


class WZCardResource(business_model.Resource):
	"""
	已分配的微众卡资源
	"""
	__slots__ = (
		'type',
		'trade_id',
		'order_id'
	)

	def __init__(self, type, order_id, trade_id):
		"""
		根据type和used_wzcards构造WZCardResource

		"""
		business_model.Resource.__init__(self)
		self.order_id = order_id
		self.trade_id = trade_id
		self.type = type

	def get_type(self):
		return self.type

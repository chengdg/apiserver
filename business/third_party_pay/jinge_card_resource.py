# coding: utf8
"""@package business.third_party_pay.jinge_card_resource
表示已分配的锦歌饭卡资源

"""

from business import model as business_model


class JinGeCardResource(business_model.Resource):
	"""
	已分配的锦歌饭卡资源
	"""
	__slots__ = (
		'type',
		'trade_id',
		'order_id',
		'money'
	)

	def __init__(self, type, order_id, trade_id, money):
		business_model.Resource.__init__(self)
		self.order_id = order_id
		self.trade_id = trade_id
		self.type = type
		self.money = money

	def get_type(self):
		return self.type

#coding: utf8
"""@package business.card.weizoom_card
微众卡的业务模型
"""

from business import model as business_model

class WZCard(business_model.Model):
	"""
	微众卡

	@see WEAPP/market_tools/tools/weizoom_card/models.py
	"""
	__slots__ = (
	)

	@property
	def orders(self):
		"""
		微众卡对应的订单
		"""
		pass

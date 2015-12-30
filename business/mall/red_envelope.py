# -*- coding: utf-8 -*-
"""@package business.mall.red_envelope
促销-红包
"""

#import json
#import itertools

#from core import inner_resource
#from core import auth
#from core.cache import utils as cache_util
#import cache
from wapi.decorators import param_required
from db.mall import models as mall_models
from datetime import datetime
from business import model as business_model

class RedEnvelope(business_model.Model):
	"""
	促销-红包
	"""

	@staticmethod
	def can_show_red_envelope(order, red_envelope):
		"""判断订单是否能显示分享红包
		@params order: 需要判断的订单，需要使用订单商品价格，订单运费等价格信息
		@params red_envelope: 红包规则，注意是从request.webapp_owner_info缓存中获取
			由缓存抓取时判断红包状态、优惠券库存问题

		@return
			True: 订单可以显示分享红包按钮
			False: 订单不可以显示分享红包按钮
		### 注: 此方法不需要查询数据库
		"""
		if order.status <= mall_models.ORDER_STATUS_CANCEL or order.status >= mall_models.ORDER_STATUS_REFUNDING:
			return False

		now = datetime.now()
		if red_envelope and (red_envelope['limit_time'] or red_envelope['end_time'] > now):
			# 缓存里有分享红包规则，并且红包规则未到期，注：红包规则状态在缓存抓取时判断
			if red_envelope['limit_time'] and red_envelope['created_at'] > order.created_at or \
				not red_envelope['limit_time'] and red_envelope['start_time'] > order.created_at:
				return False
			coupon_rule = red_envelope['coupon_rule']
			if coupon_rule and coupon_rule.get('end_date', now) > now:
				# 红包规则对应的优惠券未到期，注：优惠券库存在缓存抓取时判断
				if order.product_price + order.postage >= red_envelope['limit_order_money']:
					# 商品价格+运费应大于等于红包规则订单金额设置
					return True
		return False
	

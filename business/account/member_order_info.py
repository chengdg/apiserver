# -*- coding: utf-8 -*-

"""会员订单信息
"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
from db.mall import promotion_models
from db.member import models as member_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model
import settings
from business.decorator import cached_context_property

class MemberOrderInfo(business_model.Model):
	"""会员订单信息
	"""
	__slots__ = (
		'history_order_count',
		'not_payed_order_count',
		'not_ship_order_count',
		'shiped_order_count',
		'review_count'
	)

	@staticmethod
	@param_required(['webapp_user'])
	def get_for(args):
		order_info = MemberOrderInfo(args['webapp_user'])

		return order_info

	def __init__(self, webapp_user):
		business_model.Model.__init__(self)

		self.context['webapp_user'] = webapp_user
		self.__fill_detail()

	def __get_count_of_unfinished_product_review_picture(self, webapp_user_id):
		'''
		返回webapp_user已完成订单中， 未完成晒图的商品数量
		'''
		count = 0
		# 得到用户所有已完成订单
		orders = mall_models.Order.select().dj_where(webapp_user_id=webapp_user_id, status=mall_models.ORDER_STATUS_SUCCESSED)

		# 得到用户所以已完成订单中的商品order_has_product.id列表
		orderIds = [order.id for order in orders]
		order_has_product_list_ids = []
		for i in mall_models.OrderHasProduct.select().dj_where(order_id__in=orderIds):
			order_has_product_list_ids.append(i.id)

		# 得到用户已晒图的商品order_has_product.id列表
		prp = set()
		for i in mall_models.ProductReviewPicture.select().dj_where(order_has_product_id__in=order_has_product_list_ids):
			prp.add(i.order_has_product_id)

		count = len(order_has_product_list_ids) - len(prp)

		return count

	def __get_order_stats_from_db(self, cache_key, webapp_user_id):
		"""
		从数据获取订单统计数据
		"""
		def inner_func():
			#try:
			# TODO2: 需要优化：一次SQL，获取全部数据
			stats = {
				"total_count": mall_models.Order.select().dj_where(webapp_user_id=webapp_user_id).count(),
				"not_paid": mall_models.Order.select().dj_where(webapp_user_id=webapp_user_id, status=mall_models.ORDER_STATUS_NOT).count(),
				"not_ship_count": mall_models.Order.select().dj_where(webapp_user_id=webapp_user_id, status=mall_models.ORDER_STATUS_PAYED_NOT_SHIP).count(),
				"shiped_count": mall_models.Order.select().dj_where(webapp_user_id=webapp_user_id, status=mall_models.ORDER_STATUS_PAYED_SHIPED).count(),
				"review_count": self.__get_count_of_unfinished_product_review_picture(webapp_user_id),
			}
			ret = {
				'keys': [cache_key],
				'value': stats
			}
			return ret
			#except:
			#return None
		return inner_func

	def __fill_detail(self):
		"""
		获取会员订单信息的详情
		"""
		webapp_user = self.context['webapp_user']
		key = "webapp_order_stats_{wu:%d}" % (webapp_user.id)
		stats = cache_util.get_from_cache(key, self.__get_order_stats_from_db(key, webapp_user.id))

		self.history_order_count = stats['total_count']
		self.not_payed_order_count = stats['not_paid']
		self.not_ship_order_count = stats["not_ship_count"]
		self.shiped_order_count = stats["shiped_count"]
		self.review_count = stats["review_count"]




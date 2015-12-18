# -*- coding: utf-8 -*-
"""@package business.mall.order_review
订单评论

原Weapp评论调用的接口是`POST '/webapp/api/project_api/call/'`，其中`target_api`为`product_review/create`。
实际源码在`webapp/modules/mall/request_api_util.py`中的`create_product_review()`。
"""

from business import model as business_model
from business.mall.order import Order
from business.mall.product_review import ProductReview
from db.mall import models as mall_models
from core.watchdog.utils import watchdog_info
from wapi.decorators import param_required
import logging

class ReviewedOrder(business_model.Model):
	__slots__ = (
		'id',
		'owner_id',
		'order_id',
		'member_id',
		'serve_score',
		'deliver_score',
		'process_score'
	)

	@staticmethod
	@param_required(['model'])
	def from_model(args):
		"""
		工厂对象，根据ReviewedOrder model获取Member业务对象

		@param[in] webapp_owner
		@param[in] model: ReviewedOrder model

		@return Member业务对象
		"""
		model = args['model']

		reviewed_order = ReviewedOrder(model)
		return reviewed_order

	@staticmethod
	@param_required(['webapp_user', 'webapp_owner', 'order_id'])
	def get_from_order_id(args):
		"""
		工厂对象，根据ReviewedOrder model获取Member业务对象

		@param[in] order_id
		@param[in] webapp_owner
		@param[in] webapp_user

		@return ReviewedOrder业务对象
		"""
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']
		order_id = args['order_id']

		try:
			model = mall_models.OrderReview.get(owner_id=webapp_owner.id, order_id=order_id, member_id=webapp_user.member.id)
			return ReviewedOrder.from_model({
				'model': model
				})
		except:
			return None

	def __init__(self, model):
		business_model.Model.__init__(self)

		if model:
			self._init_slot_from_model(model)



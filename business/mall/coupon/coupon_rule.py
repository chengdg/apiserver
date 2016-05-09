# -*- coding: utf-8 -*-
"""@package business.mall.coupon_rule
优惠券规则
"""
# -*- coding: utf-8 -*-
"""@package business.mall.coupon
优惠券
"""
from datetime import datetime
from business import model as business_model
from db.mall import promotion_models
from eaglet.decorator import param_required


class CouponRule(business_model.Model):
	"""
	优惠券
	"""

	__slots__ = (
		'owner',
		'name',
		'valid_days',
		'is_active',
		'start_date'
		'end_date' ,

		'valid_restrictions',
		'money',
		'count',
		'remained_count',
		'limit_counts',
		'limit_product',
		'limit_product_id',
		'remark',
		'get_person_count',
		'get_count',
		'use_count'
	)

	def __init__(self, model):
		business_model.Model.__init__(self)

		self.context['db_model'] = model

	@staticmethod
	@param_required(['id'])
	def from_id(args):
		id = args['id']
		try:
			coupon_rule_db_model = promotion_models.CouponRule.get(id=id)
			return CouponRule.from_model({'db_model': coupon_rule_db_model})
		except:
			return None

	@staticmethod
	@param_required(['db_model'])
	def from_model(args):
		model = args['db_model']
		coupon_rule = CouponRule(model)
		coupon_rule._init_slot_from_model(model)
		return coupon_rule



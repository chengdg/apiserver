# -*- coding: utf-8 -*-
"""@package business.mall.coupon
优惠券
"""
from datetime import datetime
from business import model as business_model
from business.decorator import cached_context_property
from business.mall.coupon.coupon_rule import CouponRule
from business.mall.forbidden_coupon_product_ids import ForbiddenCouponProductIds
from db.mall import promotion_models
from wapi.decorators import param_required


class Coupon(business_model.Model):
	"""
	优惠券
	"""

	__slots__ = (
		'id',
		'owner',
		'coupon_rule',
		'member_id',
		'coupon_record_id',
		'status',
		'coupon_id',
		'provided_time',
		'start_time',
		'expired_time',
		'money',
		'is_manual_generated',
		'webapp_user'
	)

	def __init__(self, model):
		business_model.Model.__init__(self)

		self.context['db_model'] = model

	@staticmethod
	@param_required(['coupon_id'])
	def from_coupon_id(args):
		coupon_id = args['coupon_id']
		try:
			coupon_db_model = promotion_models.Coupon.get(coupon_id=coupon_id)
			return Coupon.from_model({'db_model': coupon_db_model})
		except:
			return None

	@staticmethod
	@param_required(['db_model'])
	def from_model(args):
		model = args['db_model']
		coupon = Coupon(model)
		coupon._init_slot_from_model(model)
		return coupon

	def __check_coupon_status(self, member_id):
		"""
		检查优惠券状态
		"""
		msg = ''
		today = datetime.today()
		if self.start_time > today:
			msg = '该优惠券活动尚未开始'
		elif self.expired_time < today or self.status == promotion_models.COUPON_STATUS_EXPIRED:
			msg = '该优惠券已过期'
		elif self.status == promotion_models.COUPON_STATUS_Expired:
			msg = '该优惠券已失效'
		elif self.status == promotion_models.COUPON_STATUS_DISCARD:
			msg = '该优惠券已作废'
		elif self.status == promotion_models.COUPON_STATUS_USED:
			msg = '该优惠券已使用'
		elif self.member_id > 0 and self.member_id != member_id:
			msg = '该优惠券已被他人领取不能使用'
		return msg


	@property
	def is_single_coupon(self):
		if self.coupon_rule.limit_product:
			return True

	def check_single_coupon_in_order(self, order, purchase_info, member_id):
		msg = self.__check_coupon_status(member_id)
		if msg:
			return False, msg

		if self.coupon_rule.limit_product_id not in[product.id for product in order.products]:
			return False, '该优惠券不能购买订单中的商品'

		for p in order.products:
			if p.id == self.coupon_rule.limit_product_id:
				# todo 确认此处取到的价格是原价
				price = p.price * p.purchase_count
				break

		if self.coupon_rule.valid_restrictions > price:
			# 单品券限制购物金额
				return '该优惠券指定商品金额不满足使用条件', None
		else:
			return True, ''

	def check_common_coupon_in_order(self, order, purchase_info, member_id):
		"""
		检查通用券在订单中是否可用
		"""
		msg = self.__check_coupon_status(member_id)

		if msg:
			return False, msg
		product_ids = [product.id for product in order.products if product.can_use_coupon]

		# 订单使用通用券且只有禁用通用券商品
		if len(product_ids) == 0:
			msg = '该优惠券不能购买订单中的商品'

		# 判断通用券是否满足金额限制
		else:
			products_sum_price = sum([product.price * product.purchase_count for product in order.products if product.can_use_coupon])

			if self.coupon_rule.valid_restrictions > products_sum_price and self.coupon_rule.valid_restrictions != -1:
				msg = '该优惠券不满足使用金额限制'

		if msg:
			return False, msg
		else:
			return True, msg

	# @staticmethod
	# def check_coupon_type(coupon_id):
	# 	coupon = Coupon.from_coupon_id({'coupon_id': coupon_id})
	# 	if not coupon:
	# 		coupon_type = 'invalid'
	# 	else:
	# 		coupon_type = 'product' if coupon.is_product_coupon else 'order'
	# 	return coupon_type

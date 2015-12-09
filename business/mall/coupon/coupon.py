# -*- coding: utf-8 -*-
"""@package business.mall.coupon
优惠券
"""
from datetime import datetime
from business import model as business_model
from business.mall.coupon.coupon_rule import CouponRule
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

	def check_common_coupon_in_order(self, order, purchase_info, member_id):
		"""
		检查通用券在订单中是否可用
		"""

		coupon_rule = CouponRule.from_id({"id": self.coupon_rule.id})

		msg = self.__check_coupon_status(member_id)

		if msg:
			return False, msg
		# todo 处理禁用优惠券

		# 判断通用券是否满足金额限制
		order_price =  sum([product.price * product.purchase_count for product in order.products])
		if coupon_rule.valid_restrictions > order_price and coupon_rule.valid_restrictions != -1:
			msg = '该优惠券不满足使用金额限制'

		if msg:
			return False, msg
		else:
			return True, msg

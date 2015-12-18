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
		'display_status',
		'coupon_id',
		'limit_product_id',
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

	def __check_coupon_status(self, member_id=0):
		"""
		检查优惠券状态
		"""
		msg = ''
		today = datetime.today()
		if self.start_time > today:
			msg = '该优惠券活动尚未开始'
			#兼容历史数据
			if coupon.status == promotion_models.COUPON_STATUS_USED:
				coupon.display_status = 'used'
			else:
				coupon.display_status = 'disable'
		elif self.expired_time < today or self.status == promotion_models.COUPON_STATUS_EXPIRED:
			msg = '该优惠券已过期'
			self.display_status = 'overdue'
		elif self.status == promotion_models.COUPON_STATUS_Expired:
			msg = '该优惠券已失效'
			self.display_status = 'overdue'
		elif self.status == promotion_models.COUPON_STATUS_DISCARD:
			msg = '该优惠券已作废'
			coupon.display_status = 'disable'
		elif self.status == promotion_models.COUPON_STATUS_USED:
			msg = '该优惠券已使用'
			self.display_status = 'used'
		elif self.member_id > 0 and self.member_id != member_id:
			msg = '该优惠券已被他人领取不能使用'
			self.display_status = 'used'
		return msg

	def is_can_use_by_webapp_user(self, webapp_user):
		"""
		判断webapp_user是否可以使用优惠券
		"""
		member_id = webapp_user.member.id if webapp_user.member else 0
		msg = self.check_coupon_status(member_id)
		if msg:
			return False

		return True

	@cached_context_property
	def is_single_coupon(self):
		if self.coupon_rule.limit_product:
			return True

	def check_coupon_in_order(self, order, purchase_info, member_id):
			msg = self.__check_coupon_status(member_id)
			if msg:
				return False, msg

			# 处理单品券
			if self.is_single_coupon:
				if self.coupon_rule.limit_product_id not in[product.id for product in order.products]:
					msg ='该优惠券不能购买订单中的商品'
				else:
					price = 0
					for p in order.products:
						if p.id == self.coupon_rule.limit_product_id:
							price += p.original_price * p.purchase_count

					if self.coupon_rule.valid_restrictions > price:
						# 单品券限制购物金额
							msg = '该优惠券指定商品金额不满足使用条件'

			# 处理通用券
			else:
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

	@staticmethod
	@param_required(['webapp_user'])
	def get_coupons_by_webapp_user(args):
		"""
		获取我所有的优惠券
		过滤掉 已经作废的优惠券
		"""
		webapp_user = args['webapp_user']
		#过滤已经作废的优惠券
		coupons = list(promotion_models.Coupon.select().dj_where(member_id=webapp_user.member.id, status__lt=promotion_models.COUPON_STATUS_DISCARD).order_by(promotion_models.Coupon.provided_time.desc()))
		coupon_rule_ids = [c.coupon_rule_id for c in coupons]
		coupon_rules = promotion_models.CouponRule.select().dj_where(id__in=coupon_rule_ids)
		id2coupon_rule = dict([(c.id, c) for c in coupon_rules])
		# coupon_ids = []
		today = datetime.today()
		coupon_ids_need_expire = []
		for coupon in coupons:
			#添加优惠券使用限制
			coupon.valid_restrictions = id2coupon_rule[coupon.coupon_rule_id].valid_restrictions
			coupon.limit_product_id = id2coupon_rule[coupon.coupon_rule_id].limit_product_id
			coupon.name = id2coupon_rule[coupon.coupon_rule_id].name
			coupon.start_date = id2coupon_rule[coupon.coupon_rule_id].start_date
			# 优惠券倒计时
			if coupon.expired_time > today:
				valid_days = (coupon.expired_time - today).days
				if valid_days > 0:
					coupon.valid_time = '%d天' % valid_days
				else:
					#过期时间精确到分钟
					valid_seconds = (coupon.expired_time - today).seconds
					if valid_seconds > 3600:
						coupon.valid_time = '%d小时' % int(valid_seconds / 3600)
					else:
						coupon.valid_time = '%d分钟' % int(valid_seconds / 60)
				coupon.valid_days = valid_days
			else:
				# 记录过期并且是未使用的优惠券id
				if coupon.status == promotion_models.COUPON_STATUS_UNUSED:
					coupon_ids_need_expire.append(coupon.id)
					coupon.status = promotion_models.COUPON_STATUS_EXPIRED

		if len(coupon_ids_need_expire) > 0:
			promotion_models.Coupon.update(status=promotion_models.COUPON_STATUS_EXPIRED).dj_where(id__in=coupon_ids_need_expire).execute()

		coupons = [Coupon.from_model({"db_model": coupon}) for coupon in coupons]
		return coupons
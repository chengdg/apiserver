# -*- coding: utf-8 -*-
"""@package business.mall.coupon
优惠券
"""
from datetime import datetime

from business import model as business_model
from db.mall import promotion_models
from eaglet.decorator import param_required


class Coupon(business_model.Model):
	"""
	优惠券
	"""

	__slots__ = (
		'id',
		'coupon_rule',
		'member_id',
		'coupon_record_id',
		'status',
		'display_status',
		'coupon_id',
		'limit_product_id',  # 多商品券的限制商品id列表
		'provided_time',
		'start_time',
		'expired_time',
		'money',
		'is_manual_generated',
		'webapp_user',

		'valid_restrictions',
		'name',
		'valid_days',
		'valid_time',
		'invalid_reason',
	)

	def __init__(self, model):
		business_model.Model.__init__(self)

		self.context['db_model'] = model
		if model:
			self._init_slot_from_model(model)
			self.__check_coupon_status()


	@staticmethod
	@param_required(['id'])
	def from_id(args):
		try:
			coupon_db_model = promotion_models.Coupon.get(id=args['id'])
			coupons = Coupon.__create_coupons([coupon_db_model])
			return coupons[0]
		except:
			return None


	@staticmethod
	@param_required(['coupon_id', 'webapp_owner_id'])
	def from_coupon_id(args):
		coupon_id = args['coupon_id']
		webapp_owner_id = args['webapp_owner_id']
		try:
			coupon_db_model = promotion_models.Coupon.get(coupon_id=coupon_id, owner=webapp_owner_id)
			coupons = Coupon.__create_coupons([coupon_db_model])
			return coupons[0]
		except:
			return None

	@staticmethod
	@param_required(['webapp_user'])
	def get_coupons_by_webapp_user(args):
		"""
		获取我所有的有效优惠券，过滤掉已经作废的优惠券
		"""
		webapp_user = args['webapp_user']
		#过滤已经作废的优惠券
		coupon_db_models = list(promotion_models.Coupon.select().dj_where(member_id=webapp_user.member.id, status__lt=promotion_models.COUPON_STATUS_DISCARD).order_by(promotion_models.Coupon.provided_time.desc()))
		return Coupon.__create_coupons(coupon_db_models)

	@staticmethod
	@param_required(['webapp_user'])
	def get_all_coupons_by_webapp_user(args):
		"""
		获取我所有的优惠券
		"""
		webapp_user = args['webapp_user']

		coupon_db_models = list(promotion_models.Coupon.select().dj_where(member_id=webapp_user.member.id).order_by(promotion_models.Coupon.provided_time.desc()))
		return Coupon.__create_coupons(coupon_db_models)

	@staticmethod
	@param_required(['db_model'])
	def from_model(args):
		model = args['db_model']
		coupon = Coupon(model)
		return coupon

	@staticmethod
	def __create_coupons(coupon_db_models):
		"""
		基于coupon db model创建Coupon业务对象
		"""
		coupon_rule_ids = [c.coupon_rule_id for c in coupon_db_models]
		coupon_rules = promotion_models.CouponRule.select().dj_where(id__in=coupon_rule_ids)
		id2coupon_rule = dict([(c.id, c) for c in coupon_rules])
		# coupon_ids = []
		today = datetime.today()
		coupon_ids_need_expire = []
		coupons = []
		for coupon_db_model in coupon_db_models:
			coupon = Coupon.from_model({"db_model": coupon_db_model})

			#填充与coupon rule相关数据
			coupon_rule = id2coupon_rule[coupon_db_model.coupon_rule_id]
			coupon.coupon_rule = coupon_rule
			coupon.valid_restrictions = coupon_rule.valid_restrictions
			coupon.limit_product_id = map(lambda x: int(x), coupon_rule.limit_product_id.split(',')) if coupon_rule.limit_product_id != '0' else 0
			coupon.name = coupon_rule.name

			#填充优惠券倒计时信息
			if coupon_db_model.expired_time > today:
				valid_days = (coupon_db_model.expired_time - today).days
				if valid_days > 0:
					coupon.valid_time = '%d天' % valid_days
				else:
					#过期时间精确到分钟
					valid_seconds = (coupon_db_model.expired_time - today).seconds
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

			coupons.append(coupon)

		if len(coupon_ids_need_expire) > 0:
			promotion_models.Coupon.update(status=promotion_models.COUPON_STATUS_EXPIRED).dj_where(id__in=coupon_ids_need_expire).execute()

		return coupons

	def __check_coupon_status(self, member_id=0):
		"""
		检查优惠券状态
		"""
		msg = ''
		today = datetime.today()
		if self.status == promotion_models.COUPON_STATUS_USED:
			msg = u'该优惠券已使用'
			self.display_status = 'used'
		elif self.start_time > today:
			msg = u'该优惠券活动尚未开始'
			#兼容历史数据
			if self.status == promotion_models.COUPON_STATUS_USED:
				self.display_status = 'used'
			else:
				self.display_status = 'disable'
		elif self.expired_time < today or self.status == promotion_models.COUPON_STATUS_EXPIRED:
			msg = u'该优惠券已过期'
			self.display_status = 'overdue'
		elif self.status == promotion_models.COUPON_STATUS_Expired:
			msg = u'该优惠券已失效'
			self.display_status = 'overdue'
		elif self.status == promotion_models.COUPON_STATUS_DISCARD:
			msg = u'该优惠券已作废'
			self.display_status = 'disable'
		elif self.status == promotion_models.COUPON_STATUS_USED:
			msg = u'该优惠券已使用'
			self.display_status = 'used'
		elif self.member_id > 0 and self.member_id != member_id:
			msg = u'该优惠券已被他人领取不能使用'
			self.display_status = 'used'

		self.invalid_reason = msg
		return msg

	def is_can_use_by_webapp_user(self, webapp_user):
		"""
		判断webapp_user是否可以使用优惠券
		"""
		member_id = webapp_user.member.id if webapp_user.member else 0
		msg = self.__check_coupon_status(member_id)
		if msg and msg != u'该优惠券活动尚未开始':
			return False
		else:
			return True

	def is_expired(self):
		"""
		判断优惠券是否过期

		Returns
			如果过期，返回True；否则，返回False
		"""
		return self.display_status == 'overdue'

	def is_specific_product_coupon(self):
		if self.coupon_rule.limit_product:
			return True
		else:
			return False

	def disable(self):
		"""
		禁用优惠券
		"""
		self.display_status = 'disable'

	def is_can_use_for_products(self, webapp_user, reserved_products):
		member_id = webapp_user.member.id if webapp_user.member else 0
		msg = self.__check_coupon_status(member_id)
		if msg:
			return False, msg

		# 处理单品券
		if self.is_specific_product_coupon():
			if not bool(set(self.limit_product_id) & set([product.id for product in reserved_products])):
				msg = u'该优惠券不能购买订单中的商品'
			else:
				price = 0
				for product in reserved_products:
					if product.id in self.limit_product_id:
						price += product.original_price * product.purchase_count

				if self.valid_restrictions > price:
					# 单品券限制购物金额
						msg = u'该优惠券指定商品金额不满足使用条件'
		# 处理通用券
		else:
			product_ids = [product.id for product in reserved_products if product.can_use_coupon]

			# 订单使用通用券且只有禁用通用券商品
			if len(product_ids) == 0:
				msg = u'该优惠券不能购买订单中的商品'

			# 判断通用券是否满足金额限制
			else:
				products_sum_price = sum([product.price * product.purchase_count for product in reserved_products if product.can_use_coupon])

				if self.valid_restrictions > products_sum_price and self.valid_restrictions != -1:
					msg = u'该优惠券不满足使用金额限制'

		if msg and msg != u'该优惠券活动尚未开始':
			self.disable()
			return False, msg
		else:
			return True, msg

	def check_coupon_in_order(self, order, webapp_user):
		reserved_products = order.products
		return self.is_can_use_for_products(webapp_user, reserved_products)

	def to_dict(self,*extras):
		result = super(Coupon, self).to_dict()
		if extras:
			for extra in extras:
				if extra == 'coupon_rule_id':
					result[extra] = result['coupon_rule'].id
		del result['coupon_rule']
		result['start_time'] = result['start_time'].strftime('%Y/%m/%d %H:%M:%S')
		result['expired_time'] = result['expired_time'].strftime('%Y/%m/%d %H:%M:%S')

		return result
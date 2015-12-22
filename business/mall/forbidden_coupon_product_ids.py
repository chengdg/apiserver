# -*- coding: utf-8 -*-
"""@package business.mall.forbidden_coupon_product_ids
禁用优惠券的商品id集合，从redis缓存中获取相应数据
"""

from datetime import datetime
from core.cache import utils as cache_util
from db.mall import promotion_models
from wapi.decorators import param_required
from business import model as business_model


class ForbiddenCouponProductIds(business_model.Model):
	"""
	携带基础商品信息的商品集合
	"""
	__slots__ = (
		'ids',
	)

	@staticmethod
	@param_required(['webapp_owner'])
	def get_for_webapp_owner(args):
		"""
		factory方法
		"""
		webapp_owner = args['webapp_owner']
		
		ids = ForbiddenCouponProductIds(webapp_owner)
		return ids

	def __init__(self, webapp_owner):
		business_model.Model.__init__(self)

		self.ids = self.__get_forbidden_coupon_product_ids(webapp_owner.id)

	def __get_forbidden_coupon_product_ids_for_cache(self, webapp_owner_id):
		"""
		webapp_cache:get_forbidden_coupon_product_ids_for_cache
		"""
		def inner_func():
			forbidden_coupon_products = []

			for forbidden_coupon_product in promotion_models.ForbiddenCouponProduct.select().dj_where(
				owner_id=webapp_owner_id,
				status__in=(promotion_models.FORBIDDEN_STATUS_NOT_START, promotion_models.FORBIDDEN_STATUS_STARTED)
			):
				forbidden_coupon_products.append(forbidden_coupon_product.to_dict())
			return {
					'keys': [
						'forbidden_coupon_products_%s' % (webapp_owner_id)
					],
					'value': forbidden_coupon_products
				}
		return inner_func

	def __get_forbidden_coupon_product_ids(self, webapp_owner_id):
		"""
		webapp_cache:get_forbidden_coupon_product_ids
		获取商家的禁用全场优惠券的商品id列表 duhao
		"""
		key = 'forbidden_coupon_products_%s' % (webapp_owner_id)

		dict_forbidden_coupon_products = cache_util.get_from_cache(key, self.__get_forbidden_coupon_product_ids_for_cache(webapp_owner_id))
		forbidden_coupon_products = []

		for dict_forbidden_coupon_product in dict_forbidden_coupon_products:
			forbidden_coupon_products.append(promotion_models.ForbiddenCouponProduct.from_dict(dict_forbidden_coupon_product))

		product_ids = set()
		for product in forbidden_coupon_products:
			if ForbiddenCouponProductIds.check_is_active(product):
				product_ids.add(product.product_id)

		return product_ids

	@staticmethod
	def check_is_active(forbidden_coupon_product):
		if forbidden_coupon_product.is_permanant_active and forbidden_coupon_product.status != promotion_models.FORBIDDEN_STATUS_FINISHED:
			return True

		if forbidden_coupon_product.status == promotion_models.FORBIDDEN_STATUS_FINISHED:
			return False

		ForbiddenCouponProductIds.update_status_if_necessary(forbidden_coupon_product)

		if forbidden_coupon_product.status == promotion_models.FORBIDDEN_STATUS_NOT_START or forbidden_coupon_product.status == promotion_models.FORBIDDEN_STATUS_FINISHED:
			return False

		return True

	@staticmethod
	def update_status_if_necessary(forbidden_coupon_product):
		if forbidden_coupon_product.is_permanant_active:
			if forbidden_coupon_product.status != promotion_models.FORBIDDEN_STATUS_STARTED:
				forbidden_coupon_product.status = promotion_models.FORBIDDEN_STATUS_STARTED
				forbidden_coupon_product.save()
			return
		now = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

		if type(forbidden_coupon_product.end_date) == datetime:
			end_date = forbidden_coupon_product.end_date.strftime('%Y-%m-%d %H:%M:%S')
		else:
			end_date = forbidden_coupon_product.end_date

		if type(forbidden_coupon_product.start_date) == datetime:
			start_date = forbidden_coupon_product.start_date.strftime('%Y-%m-%d %H:%M:%S')
		else:
			start_date = forbidden_coupon_product.start_date

		if start_date <= now and end_date > now and forbidden_coupon_product.status == promotion_models.FORBIDDEN_STATUS_NOT_START:
			# 未开始状态,但是时间已经再开始,由于定时任务尚未执行
			forbidden_coupon_product.status = promotion_models.FORBIDDEN_STATUS_STARTED
			forbidden_coupon_product.save()
		elif end_date <= now and (
				forbidden_coupon_product.status == promotion_models.FORBIDDEN_STATUS_NOT_START or
				forbidden_coupon_product.status == promotion_models.FORBIDDEN_STATUS_STARTED):
			# 未开始,进行中状态,但是时间到期了,由于定时任务尚未执行
			forbidden_coupon_product.status = promotion_models.FORBIDDEN_STATUS_FINISHED
			forbidden_coupon_product.save()

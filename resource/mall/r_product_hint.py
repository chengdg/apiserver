# -*- coding: utf-8 -*-

from core import resource
from wapi.decorators import param_required
from cache import utils as cache_util
from wapi.mall import promotion_models


class ProductHint(resource.Resource):
	"""
	商品提示
	"""
	app = 'mall'
	resource = 'product_hint'

	@staticmethod
	def get_forbidden_coupon_product_ids_for_cache(webapp_owner_id):
		"""
		webapp_cache:get_forbidden_coupon_product_ids_for_cache
		"""
		def inner_func():
			forbidden_coupon_products = list(promotion_models.ForbiddenCouponProduct.select().dj_where(
				owner_id=webapp_owner_id, 
				status__in=(promotion_models.FORBIDDEN_STATUS_NOT_START, promotion_models.FORBIDDEN_STATUS_STARTED)
			))

			return {
					'keys': [
						'forbidden_coupon_products_%s' % (webapp_owner_id)
					],
					'value': forbidden_coupon_products
				}
		return inner_func

	@staticmethod
	def get_forbidden_coupon_product_ids(webapp_owner_id):
		"""
		webapp_cache:get_forbidden_coupon_product_ids
		获取商家的禁用全场优惠券的商品id列表 duhao
		"""
		key = 'forbidden_coupon_products_%s' % (webapp_owner_id)

		forbidden_coupon_products = cache_util.get_from_cache(key, ProductHint.get_forbidden_coupon_product_ids_for_cache(webapp_owner_id))
		product_ids = []
		for product in forbidden_coupon_products:
			if product.is_active:
				product_ids.append(product.product_id)
		return product_ids

	@staticmethod
	def is_forbidden_coupon(owner_id, product_id):
		"""
		判断商品是否被禁止使用全场优惠券
		"""
		forbidden_coupon_product_ids = ProductHint.get_forbidden_coupon_product_ids(owner_id)
		product_id = int(product_id)
		return product_id in forbidden_coupon_product_ids

	@param_required(['woid', 'product_id'])
	def get(args):
		"""
		获取显示在商品详情页的商品相关的提示信息

		@note duhao与2015-09-08增加 `__get_product_hint(owner_id, product_id)`
		"""
		hint = ''
		webapp_owner_id = args['woid']
		product_id = args['product_id']
		if ProductHint.is_forbidden_coupon(webapp_owner_id, product_id):
			hint = u'该商品不参与全场优惠券使用！'
		return {"woid": webapp_owner_id, "hint": hint}

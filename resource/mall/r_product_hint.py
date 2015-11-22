# -*- coding: utf-8 -*-

from core import inner_resource
from wapi.decorators import param_required
from core.cache import utils as cache_util
from db.mall import promotion_models
import resource


class ProductHint(inner_resource.Resource):
	"""
	商品提示
	"""
	app = 'mall'
	resource = 'product_hint'

	@staticmethod
	def is_forbidden_coupon(owner_id, product_id):
		"""
		判断商品是否被禁止使用全场优惠券
		"""
		forbidden_coupon_product_ids = resource.get('mall', 'forbidden_coupon_product_ids', {
			'woid': owner_id
		})
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



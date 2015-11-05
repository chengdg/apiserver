# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required
#from wapi.wapi_utils import create_json_response
from wapi.mall import models as mall_models
from utils import dateutil as utils_dateutil


class ShoppingCartItem(api_resource.ApiResource):
	"""
	购物车项目
	"""
	app = 'mall'
	resource = 'shopping_cart_item'

	@staticmethod
	def add_product_to_shopping_cart(webapp_user_id, product_id, product_model_name, count):
		try:
			shopping_cart_item = mall_models.ShoppingCart.get(
				mall_models.ShoppingCart.webapp_user_id == webapp_user_id,
				mall_models.ShoppingCart.product == product_id,
				mall_models.ShoppingCart.product_model_name == product_model_name
			)
			shopping_cart_item.count = shopping_cart_item.count + count
			shopping_cart_item.save()
		except:
			shopping_cart_item = mall_models.ShoppingCart.create(
				webapp_user_id = webapp_user_id,
				product = product_id,
				product_model_name = product_model_name,
				count = count
			)

	@staticmethod
	def get_shopping_cart_product_nums(webapp_user_id):
		"""
		获得购物车中商品数量
		"""
		return mall_models.ShoppingCart.select().dj_where(webapp_user_id=webapp_user_id).count()

	@param_required(['id'])
	def get(args):
		"""
		获取购物车项目

		@param id 商品ID
		"""
		product_id = args['id']
		#print("in product(), product_id={}".format(product_id))
		#return {"name": u"商品%s" % product_id}
		product = mall_models.Product.get(id=product_id)
		return Product.to_dict(product)

	@param_required(['product_id', 'count', 'wuid'])
	def put(args):
		"""
		创建购物车项目
		"""
		product_id = args['product_id']
		product_model_name = args.get('product_model_name', 'standard')
		webapp_user_id = args['wuid']
		count = int(args.get('count', 0))
		ShoppingCartItem.add_product_to_shopping_cart(webapp_user_id, product_id, product_model_name, count)

		new_count = ShoppingCartItem.get_shopping_cart_product_nums(webapp_user_id)

		return {
			"shopping_cart_product_nums": new_count
		}

	@param_required(['id'])
	def post(args):
		"""
		修改购物车项目
		"""
		return {
			"id": args['id'],
			"action": "post"
		}

	@param_required(['id'])
	def delete(args):
		"""
		删除购物车项目
		"""
		return {
			"id": args['id'],
			"action": "delete"
		}

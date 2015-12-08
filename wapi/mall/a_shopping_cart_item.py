# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required
#from wapi.wapi_utils import create_json_response
from db.mall import models as mall_models
from utils import dateutil as utils_dateutil
from business.mall.shopping_cart import ShoppingCart


class AShoppingCartItem(api_resource.ApiResource):
	"""
	购物车项目
	"""
	app = 'mall'
	resource = 'shopping_cart_item'
	
	@param_required(['product_id', 'count', 'product_model_name'])
	def put(args):
		"""
		创建购物车项目
		"""
		product_id = args['product_id']
		product_model_name = args.get('product_model_name', 'standard')
		count = int(args.get('count', 0))

		shopping_cart = ShoppingCart.get_for_webapp_user({
			'webapp_user': args['webapp_user'],
			'webapp_owner': args['webapp_owner'],
		})
		shopping_cart.add_product(product_id, product_model_name, count)

		return {
			"shopping_cart_product_nums": shopping_cart.product_count
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
		shopping_cart = ShoppingCart.get_for_webapp_user({
			'webapp_user': args['webapp_user'],
			'webapp_owner': args['webapp_owner'],
		})

		shopping_cart_item_id = args['id']
		shopping_cart.delete_items(shopping_cart_item_id)

		return {
			'success': True,
			'count': 1
		}


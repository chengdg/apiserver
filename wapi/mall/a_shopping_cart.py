# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required
#from wapi.wapi_utils import create_json_response
from db.mall import models as mall_models
from utils import dateutil as utils_dateutil
from business.mall.shopping_cart import ShoppingCart


class AShoppingCart(api_resource.ApiResource):
	"""
	购物车
	"""
	app = 'mall'
	resource = 'shopping_cart'
	
	@param_required([])
	def get(args):
		"""
		创建购物车项目
		"""
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']

		#获取promotion_product_group集合
		shopping_cart = ShoppingCart.get_for_webapp_user({
			'webapp_owner': webapp_owner,
			'webapp_user': webapp_user
		})
		product_groups = shopping_cart.product_groups
		invalid_products = shopping_cart.invalid_products

		#获取会员信息
		member = webapp_user.member
		_, member_discount = member.discount
		member_data = {
			'grade_id': member.grade_id,
			'discount': member_discount
		}

		data = {
			'member': member_data,
			'product_groups': product_groups,
			'invalid_products': [product.to_dict() for product in invalid_products]
		}

		return data

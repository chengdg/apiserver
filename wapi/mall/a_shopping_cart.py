# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required
#from wapi.wapi_utils import create_json_response
from db.mall import models as mall_models
from utils import dateutil as utils_dateutil
from business.mall.shopping_cart_products import ShoppingCartProducts
from business.mall.product_grouper import ProductGrouper


class AShoppingCart(api_resource.ApiResource):
	"""
	购物车
	"""
	app = 'mall'
	resource = 'shopping_cart'
	
	@param_required(['woid'])
	def get(args):
		"""
		创建购物车项目
		"""
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']

		#获取promotion_product_group集合
		shopping_cart_products = ShoppingCartProducts.get_for_webapp_user({
			'webapp_owner': webapp_owner,
			'webapp_user': webapp_user
		})
		product_grouper = ProductGrouper()
		promotion_product_groups = product_grouper.group_product_by_promotion(webapp_user.member, shopping_cart_products.products)
		product_group_datas = [group.to_dict(with_price_factor=True) for group in promotion_product_groups]

		#获取会员信息
		member = webapp_user.member
		_, member_discount = member.discount
		member_data = {
			'grade_id': member.grade_id,
			'discount': member_discount
		}

		data = {
			'member': member_data,
			'product_groups': product_group_datas
		}

		return data

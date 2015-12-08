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

		#获取购物车商品信息
		shopping_cart = webapp_user.shopping_cart
		product_groups = shopping_cart.product_groups
		invalid_products = shopping_cart.invalid_products

		#对shopping cart item进行排序，要求：
		#1. 限时抢购排在最前面，多个促销按加入购物车时间顺序排列
		#2. 买赠排在促销后，多个买赠按加入购物车时间顺序排列
		#3. 其他按加入购物车时间顺序
		flash_sales = []
		premium_sales = []
		other_promotions = []
		others = []
		for product_group in product_groups:
			if product_group['promotion'] and product_group['can_use_promotion']:
				promotion = product_group['promotion']
				if promotion['type_name'] == 'flash_sale':
					flash_sales.append(product_group)
				elif promotion['type_name'] == 'premium_sale':
					premium_sales.append(product_group)
				else:
					other_promotions.append(product_group)
			else:
				others.append(product_group)

		sort_strategy = lambda x,y: cmp(x['products'][0]['shopping_cart_id'], y['products'][0]['shopping_cart_id'])
		flash_sales.sort(sort_strategy)
		premium_sales.sort(sort_strategy)
		other_promotions.sort(sort_strategy)
		others.sort(sort_strategy)

		product_groups = []
		product_groups.extend(flash_sales)
		product_groups.extend(premium_sales)
		product_groups.extend(other_promotions)
		product_groups.extend(others)

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

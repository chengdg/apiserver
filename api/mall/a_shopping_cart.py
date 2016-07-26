# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required
#from api.wapi_utils import create_json_response
from db.mall import models as mall_models
from util import dateutil as utils_dateutil
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

		if webapp_owner.user_profile.webapp_type:
			#如果是自营账号，需要按添加到购物车的先后顺序排列商品，相同店铺的商品集中排列
			temp_groups = []
			supplier_user_id2product_datas = {}
			supplier_user_id2max_shopping_cart_id = {}  #每个供应商最后加进购物车的id，用户排序

			group_for_weizoom(supplier_user_id2product_datas, supplier_user_id2max_shopping_cart_id, flash_sales, 'flash_sales')
			group_for_weizoom(supplier_user_id2product_datas, supplier_user_id2max_shopping_cart_id, premium_sales, 'premium_sales')
			group_for_weizoom(supplier_user_id2product_datas, supplier_user_id2max_shopping_cart_id, other_promotions, 'other_promotions')
			group_for_weizoom(supplier_user_id2product_datas, supplier_user_id2max_shopping_cart_id, others, '')

			#按supplier_user_id2max_shopping_cart_id从大到小排序
			sorted_items = sorted(supplier_user_id2max_shopping_cart_id.iteritems(), key=lambda d:d[0])
			product_groups = []
			for item in sorted_items:
				product_groups.append(supplier_user_id2product_datas[item[0]])

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
			'invalid_products': [product.to_dict() for product in invalid_products],
			'is_weizoom': webapp_owner.user_profile.webapp_type
		}

		return data


def group_for_weizoom(supplier_user_id2product_datas, supplier_user_id2max_shopping_cart_id, groups, key):
	for product_group in groups:
		products = product_group['products']
		for product in products:
			group_by = '%d-%d' % (product['supplier'], product['supplier_user_id'])
			product_data = {
				'promotion': key,
				'product': product
			}
			product_datas = supplier_user_id2product_datas.get(group_by, [])
			product_datas.append(product_data)
			supplier_user_id2product_datas[group_by] = product_datas
			shopping_cart_id = supplier_user_id2max_shopping_cart_id.get(group_by, 0)
			if product['shopping_cart_id'] > shopping_cart_id:
				supplier_user_id2max_shopping_cart_id[group_by] = product['shopping_cart_id']

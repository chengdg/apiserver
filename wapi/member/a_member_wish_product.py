# -*- coding: utf-8 -*-
import json

from core import api_resource
from wapi.decorators import param_required
from db.mall import models as mall_models
from utils import dateutil as utils_dateutil
import resource
from business.mall.product import Product


class AMemberWishProduct(api_resource.ApiResource):
	"""
	会员收藏商品
	"""
	app = 'member'
	resource = 'wish_product'


	# @param_required(['webapp_user', 'product_id'])
	# def get(args):
	# 	"""
	# 	获取会员单个收藏的单个商品

	# 	@param webapp_user 会员帐号信息
	# 	@param product_id_id 商品ID

	# 	"""

	# 	"""
	# 	显示“商品详情”页面

	# 	"""
	# 	product_id = args['product_id']
	# 	webapp_owner = args['webapp_owner']
	# 	# jz 2015-11-26
	# 	# webapp_user = args['webapp_user']
	# 	# member = args.get('member', None)
	# 	# member_grade_id = member.grade_id if member else None
		
	# 	# 检查置顶评论是否过期
	# 	# TODO: 是否每次都需要去进行检查？还是交给service每天凌晨进行更新
	# 	# resource.post('mall', 'top_product_review', {
	# 	# 	"product_id": product_id
	# 	# })

	# 	product = Product.from_id({
	# 		'webapp_owner': webapp_owner,
	# 		# 'member': member,
	# 		'product_id': args['product_id']
	# 	})

	# 	return product.to_dict(extras=['hint'])

	@param_required(['webapp_user', 'product_id'])
	def put(args):
		webapp_user = args['webapp_user']
		product_id = args['product_id']
		member = webapp_user.member
		print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>..member_id:', webapp_user.social_account.openid
		member.collect_product(product_id)
		return {}

	@param_required(['webapp_user', 'product_id', 'wished'])
	def post(args):
		webapp_user = args['webapp_user']
		product_id = args['product_id']
		wished = args['wished']
		member = webapp_user.member
		if str(wished) == '1':
			member.collect_product(product_id)
		else:
			member.cancel_collect_product(product_id)

		return {}




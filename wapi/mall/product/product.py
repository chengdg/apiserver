# -*- coding: utf-8 -*-
import json

from core import api_resource
from wapi.decorators import param_required
from wapi.mall import models as mall_models
from utils import dateutil as utils_dateutil
import resource


class Product(api_resource.ApiResource):
	"""
	商品
	"""
	app = 'mall'
	resource = 'product'


	@param_required(['woid', 'product_id'])
	def get(args):
		"""
		获取商品详情

		@param id 商品ID

		@note 从Weapp中迁移过来
		@see  mall_api.get_product_detail(webapp_owner_id, product_id, webapp_user, member_grade_id)
		"""

		"""
		显示“商品详情”页面

		"""
		product_id = args['product_id']
		webapp_owner_id = args['woid']
		webapp_user = args['webapp_user']

		member = args.get('member', None)
		member_grade_id = member.grade_id if member else None
		
		# 检查置顶评论是否过期
		# TODO: 是否每次都需要去进行检查？还是交给service每天凌晨进行更新
		resource.post('mall', 'top_product_review', {
			"product_id": product_id
		})

		product = resource.get('mall', 'product_detail', {
			'woid': webapp_owner_id, 
			'product_id': product_id, 
			'member_grade_id': member_grade_id, 
			'wuid': webapp_user.id
		}) # 获取商品详细信息
		product['swipe_images_json'] = json.dumps(product['swipe_images'])
		
		hint = resource.get('mall', 'product_hint', {
			'woid': webapp_owner_id, 
			'product_id': product_id
		}).get('hint', '')

		if product['is_deleted']:
			raise Exception(u"商品不存在")

		jsons = [{
			"name": "models",
			"content": product.get('all_models')
		}, {
			'name': 'priceInfo',
			'content': product.get('price_info')
		}, {
			'name': 'promotion',
			'content': product.get('promotion')
		}]

		non_member_followurl = None
		'''
		if request.user.is_weizoom_mall:
			# TODO: is_can_buy_by_product做什么？To be deprecated.
			#product0.is_can_buy_by_product(request)
			# TODO: API化
			otherProfile = UserProfile.objects.get(user_id=product['owner_id'])
			otherSettings = OperationSettings.objects.get(owner=otherProfile.user)
			if otherSettings.weshop_followurl.startswith('http://mp.weixin.qq.com'):
				non_member_followurl = otherSettings.weshop_followurl

				# liupeiyu 记录点击关注信息
				non_member_followurl = './?woid={}&module=mall&model=concern_shop_url&action=show&product_id={}&other_owner_id={}'.format(request.webapp_owner_id, product['id'], product['owner_id'])
		'''

		is_non_member = not member
		return product
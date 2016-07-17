# -*- coding: utf-8 -*-
import json
import settings
from business.mall.allocator.order_group_buy_resource_allocator import GroupBuyOPENAPI
from eaglet.core import api_resource
from eaglet.decorator import param_required
from db.mall import models as mall_models
from util import dateutil as utils_dateutil
#import resource
from business.mall.product import Product
from business.mall.review.product_reviews import ProductReviews

from eaglet.utils.resource_client import Resource
from eaglet.core import watchdog
from eaglet.utils.resource_client import Resource


class AProduct(api_resource.ApiResource):
	"""
	商品
	"""
	app = 'mall'
	resource = 'product'


	@param_required(['product_id'])
	def get(args):
		"""
		获取商品详情

		@param product_id 商品ID

		@note 从Weapp中迁移过来
		@see  mall_api.get_product_detail(webapp_owner_id, product_id, webapp_user, member_grade_id)
		"""

		product_id = args['product_id']
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']

		param_data = {'pid': product_id, 'woid': webapp_owner.id, 'member_id': webapp_user.member.id}


		resp = Resource.use('marketapp_apiserver').get({
			'resource':GroupBuyOPENAPI['group_buy_product'],
			'data':param_data
		})


		if resp and resp['code'] == 200:
			data = resp['data']

			if data['is_in_group_buy']:
				return {
					'is_in_group_buy': True,
					'activity_url': 'http://' + settings.WEAPP_DOMAIN + data['activity_url']
				}

		product = Product.from_id({
			'webapp_owner': webapp_owner,
			# 'member': member,
			'product_id': args['product_id']
		})
		if product.is_deleted:
			return {'is_deleted': True}
		else:
			product.apply_discount(args['webapp_user'])

			if product.promotion:
				#检查促销是否能使用
				if not product.promotion.can_use_for(webapp_user):
					product.promotion = None
					product.promotion_title = product.product_promotion_title


			param_data = {'woid':webapp_owner.id, 'product_id':product_id}
			reviews = []
			resp = Resource.use('marketapp_apiserver').get({
				'resource': 'evaluate.get_product_evaluates',
				'data': param_data
			})

			if resp:
				code = resp["code"]
				if code == 200:

					reviews = resp["data"]['product_reviews']

			result = product.to_dict(extras=['hint'])

			result['webapp_owner_integral_setting'] = {
				'integarl_per_yuan': webapp_owner.integral_strategy_settings.integral_each_yuan
			}
			result['product_reviews'] = reviews
		result['is_in_group_buy'] = False
		result['activity_url'] = ''
		print ">>2"*18
		import uuid
		message = {
			"_log_type": "test",
			"_uuid": "view_product",
			"_type_0": "product",
			"woid": webapp_owner.id,
			"webapp_user_id": webapp_user.id,
			"r": str(uuid.uuid4()),
			"product_id": product_id,
			"review_count": len(reviews),
			"is_in_group_buy": result['is_in_group_buy']
		}

		watchdog.info(json.dumps(message))



		return result

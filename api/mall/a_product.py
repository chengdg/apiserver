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
from business.mall.review.review_openapi import REVIEWOPENAPI
from util.microservice_consumer import microservice_consume
from eaglet.core import watchdog
from eaglet.utils.api_resource import APIResourceClient


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

		resource = APIResourceClient(settings.WEAPP_DOMAIN, GroupBuyOPENAPI['group_buy_product'])
		is_success, code, group_buy_product = resource.get(param_data)
		if is_success and code == 200:
			if group_buy_product['is_in_group_buy']:
				return {
					'is_in_group_buy': True,
					'activity_url': 'http://' + settings.WEAPP_DOMAIN + group_buy_product['activity_url']
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

			# product_reviews = ProductReviews.get_from_product_id({
			# 	'webapp_owner': webapp_owner,
			# 	'product_id': product_id,
			# })
			url = REVIEWOPENAPI['evaluates_from_product_id']
			param_data = {'woid':webapp_owner.id, 'product_id':product_id}
			is_success, reviews_data = microservice_consume(url=url, data=param_data)
			reviews = []
			if is_success:
				reviews = reviews_data['product_reviews']


			# if product_reviews:
			# 	reviews = product_reviews.products
			# 	reviews = reviews[:2]
			# else:
			# 	reviews = []
			# #假数据
			# reviews =  [
	  #                   {
	  #                     "status": "2",
	  #                     "member_icon": "",
	  #                     "created_at": "2016-06-06 10:32:10",
	  #                     "member_id": 1,
	  #                     "review_detail": "123asdfa",
	  #                     "member_name": "bill",
	  #                   },
	  #                   {
	  #                     "status": "1",
	  #                     "member_icon": "",
	  #                     "created_at": "2016-06-06 11:53:12",
	  #                     "member_id": 1,
	  #                     "review_detail": "fgsfsfdgsfdgsfg",
	  #                     "member_name": "bill",
	  #                   }
	  #                 ]
	  #       #假数据

			result = product.to_dict(extras=['hint'])

			result['webapp_owner_integral_setting'] = {
				'integarl_per_yuan': webapp_owner.integral_strategy_settings.integral_each_yuan
			}
			result['product_reviews'] = reviews
		result['is_in_group_buy'] = False
		result['activity_url'] = ''

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

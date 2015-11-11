# -*- coding: utf-8 -*-

"""订单商品

"""

import json
from bs4 import BeautifulSoup
import math
import itertools

from wapi.decorators import param_required
from wapi import wapi_utils
from cache import utils as cache_util
from wapi.mall import models as mall_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.product import Product
import settings


class OrderProduct(business_model.Model):
	"""订单商品
	"""
	__slots__ = (
		'member_discount',
		'purchase_count',
		'used_promotion_id',
		'total_price',
	)

	@staticmethod
	@param_required(['webapp_owner_info', 'webapp_user', 'product_id', 'product_model_name'])
	def create(args):
		"""工厂方法，创建OrderProduct对象

		@return OrderProduct对象
		"""
		order_product = OrderProduct(args['webapp_owner_info'], args['webapp_user'], args['product_id'], args['product_model_name'])

		return order_product

	def __init__(self, webapp_owner_info, webapp_user, product_id, product_model_name, webapp_user):
		business_model.Model.__init__(self)

		self.__fill_detail(product_id, product_model_name, webapp_user)

	def __fill_detail(self, product_id, product_model_name, webapp_user):
		"""
		mall_api:get_product_details_with_model
		获得指定规格的商品详情
		"""
		product = Product.from_id(product_id)
		products = []
		invalid_products = []
		id2info = dict([('%s_%s' % (info['id'], info['model_name']), info) for info in product_infos])
		for product_info in product_infos:
			product = resource.get('mall', 'product_detail', {
				"woid": webapp_owner_id,
				"product_id": product_info['id'],
				"return_model": True
			})
			#product = webapp_cache.get_webapp_product_detail(webapp_owner_id, product_info['id'])
			#product = copy.copy(product)
			product.flash_data = {
				"product_model_id": '%s_%s' % (product_info['id'], product_info['model_name'])
			}
			products.append(product)

		for product in products:
			product_info = id2info[product.flash_data['product_model_id']]
			product.fill_specific_model(product_info['model_name'])
			if webapp_owner_id != product.owner_id and product.weshop_sync == 2:
				product.price = round(product.price * 1.1, 2)

		return products

	@staticmethod
	def get_product_member_discount(discount, product):
	    """
	    get_product_member_discount
	    判断商品是否参加会员折扣，返回对应折扣(0.000~1.000), 1.000 表示伟打折.


	    Return:
	      fload: 如果商品参加会员折扣， 返回对应的折扣 否则返回1.000
	    """
	    # 商品是否参加会员折扣
	    if product.is_member_product:
	        return discount
	    return 1.000

	def get_products(self, webapp_owner_id, webapp_owner_info, webapp_user, purchase_info):
	    '''获取商品集合
	    '''
	    member = webapp_user.member
	    member_grade_id, member_discount = resource.get('member', 'member_discount', {
	    	'member': member,
	    	'webapp_owner_info': webapp_owner_info
	    })

	    product_ids = purchase_info['product_ids']
	    promotion_ids = purchase_info['promotion_ids']
	    product_counts = purchase_info['product_counts']
	    product_model_names = purchase_info['product_model_names']
	    products = []
	    product_infos = []
	    product2count = {}
	    product2promotion = {}

	    for i in range(len(product_ids)):
	        product_id = int(product_ids[i])
	        product_model_name = product_model_names[i]
	        product_infos.append({"id": product_id, "model_name": product_model_name})
	        product_model_id = '%s_%s' % (product_id, product_model_name)
	        product2count[product_model_id] = int(product_counts[i])
	        product2promotion[product_model_id] = promotion_ids[i] if promotion_ids[i] else 0

	    postage_configs = webapp_owner_info.mall_data['postage_configs']
	    system_postage_config = filter(lambda c: c.is_used, postage_configs)[0]
	    products = ROrderProducts.get_product_details_with_model(webapp_owner_id, webapp_user, product_infos)
	    for product in products:
	        product_model_id = '%s_%s' % (product.id, product.model['name'])
	        product.member_discount = ROrderProducts.get_product_member_discount(member_discount, product)
	        product.purchase_count = product2count[product_model_id]
	        product.used_promotion_id = int(product2promotion[product_model_id])
	        product.total_price = float(product.price)*product.purchase_count

	        # 确定商品的运费策略
	        if product.postage_type == mall_models.POSTAGE_TYPE_UNIFIED:
	            #使用统一运费
	            product.postage_config = {
	                "id": -1,
	                "money": product.unified_postage_money,
	                "factor": None
	            }
	        else:
	            if isinstance(system_postage_config.created_at, datetime):
	                system_postage_config.created_at = system_postage_config.created_at.strftime('%Y-%m-%d %H:%M:%S')
	            if isinstance(system_postage_config.update_time, datetime):
	                system_postage_config.update_time = system_postage_config.update_time.strftime('%Y-%m-%d %H:%M:%S')
	            product.postage_config = system_postage_config.to_dict('factor')
	    return products
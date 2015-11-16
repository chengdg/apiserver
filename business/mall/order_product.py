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
from business.decorator import cached_context_property


class OrderProduct(business_model.Model):
	"""订单商品
	"""
	__slots__ = (
		'id',
		'type',
		'member_discount',
		'purchase_count',
		'used_promotion_id',
		'total_price',
		'product_model_id',
		'_postage_config',

		'price',
		'weight',
		'stock_type',
		'stocks',
		'min_limit',
		'model_name',
		'model',
		'is_model_deleted',
		'market_price',
		'custom_model_properties',
		'total_price',
	)

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'product_info'])
	def get(args):
		"""工厂方法，创建OrderProduct对象

		@return OrderProduct对象
		"""
		order_product = OrderProduct(args['webapp_owner'], args['webapp_user'], args['product_info'])

		return order_product

	def __init__(self, webapp_owner, webapp_user, product_info):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.__fill_detail(webapp_user, product_info)

	def __fill_detail(self, webapp_user, product_info):
		"""
		mall_api:get_product_details_with_model
		获得指定规格的商品详情
		"""
		product = Product.from_id(product_info['id'])
		self.context['product'] = product

		model = product.get_specific_model(product_info['model_name'])
		self.type = product.type,
		self.id = product.id,
		self.price = model['price']
		self.weight = model['weight']
		self.stock_type = model['stock_type']
		if not hasattr(product, 'min_limit'):
			self.min_limit = model['stocks']
		self.stocks = model['stocks']
		self.model_name = product_info['model_name']
		self.model = model
		self.is_model_deleted = False
		self.market_price = model.get('market_price', 0.0)
		self.product_model_id = '%s_%s' % (product_info['id'], product_info['model_name'])
		self.purchase_count = product_info['count']
		self.used_promotion_id = product_info['promotion_id']
		self.total_price = float(self.price) * int(self.purchase_count)

		if product.is_member_product:
			self.member_discount = webapp_user.member.discount
		else:
			self.member_discount = 1.00
		#TODO2: 为微众商城增加1.1的价格因子

	@cached_context_property
	def postage_config(self):
		"""
		[property] 订单商品的运费策略
		"""
		product = self.context['product']
		webapp_owner = self.context['webapp_owner']

        if product.postage_type == mall_models.POSTAGE_TYPE_UNIFIED:
            #使用统一运费
            product.postage_config = {
                "id": -1,
                "money": product.unified_postage_money,
                "factor": None
            }
        else:
        	system_postage_config = webapp_owner.system_postage_config
            if isinstance(system_postage_config.created_at, datetime):
                system_postage_config.created_at = system_postage_config.created_at.strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(system_postage_config.update_time, datetime):
                system_postage_config.update_time = system_postage_config.update_time.strftime('%Y-%m-%d %H:%M:%S')
            product.postage_config = system_postage_config.to_dict('factor')

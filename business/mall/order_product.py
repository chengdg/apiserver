# -*- coding: utf-8 -*-
"""@package business.mall.order_product
订单商品

一个订单商品是在商品业务对象的基础上，加上订单的相关信息，比如订单中商品的数量等，形成的新的业务对象。

与订单相关的业务流程，比如下单，获取订单详情等等，都不直接使用Product，而是使用OrderProduct

"""

#import json
#from bs4 import BeautifulSoup
#import math
#import itertools
#from datetime import datetime

from eaglet.decorator import param_required
##from wapi import wapi_utils
#from eaglet.core.cache import utils as cache_util
from db.mall import models as mall_models
#import resource
from eaglet.core import watchdog
#from eaglet.core import watchdog
from business import model as business_model 
from business.mall.product import Product
#import settings
from business.decorator import cached_context_property


class OrderProduct(business_model.Model):
	"""订单商品
	"""
	__slots__ = (
		'id',
		'name',
		'type',
		'thumbnails_url',
		'pic_url',
		'is_discounted',
		'purchase_count',
		'used_promotion_id',
		'product_model_id',
		'_postage_config',

		'price',
		'original_price',
		'weight',
		'stock_type',
		'stocks',
		'min_limit',
		'model_name',
		'model',
		'custom_model_properties',
		'total_price',
		'is_member_product',
		'promotion',
		'shelve_type',
		'promotion_money',
		'active_integral_sale_rule',
		'integral_sale_model',
		'discount_money',
		'supplier',
		'supplier_name',
		'supplier_user_id',
		'is_use_integral_sale',

		#review add by bert
		'has_reviewed', #old has_review 
		'has_reviewed_picture', #old  product_review_picture > order_is_reviewed
		'rid', # order_has_product_id
	)	

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'product_info'])
	def get(args):
		"""工厂方法，创建OrderProduct对象

		@param[in] product_info 商品信息
			{
				id: 商品id,
				model_name: 商品规格名,
				promotion_id: 商品促销id,
				count: 商品数量
			}

		@return OrderProduct对象
		"""
		order_product = OrderProduct(args['webapp_owner'], args['webapp_user'], args['product_info'])

		return order_product

	def __init__(self, webapp_owner, webapp_user, product_info=None):
		business_model.Model.__init__(self)

		self.context['webapp_user'] = webapp_user
		self.context['webapp_owner'] = webapp_owner
		if product_info:
			self.__fill_detail(webapp_user, product_info)


	def __fill_detail(self, webapp_user, product_info):
		"""
		根据商品信息填充相应的商品详情
		"""
		product = Product.from_id({
			"webapp_owner": self.context['webapp_owner'],
			"member": webapp_user.member,
			"product_id": product_info['id']
		})
		self.context['product'] = product

		self.price = product_info['price']
		self.total_price = product_info['total_price']
		self.discount_money = product_info['discount_money']
		self.promotion_money = product_info['promotion_money']
		self.purchase_count = product_info['count']
		self.model_name = product_info['model_name']
		self.product_model_id = '%s_%s' % (product_info['id'], product_info['model_name'])
		self.purchase_count = product_info['count']
		self.used_promotion_id = product_info['promotion_id']
		self.is_discounted = (self.discount_money != 0)
		self.is_use_integral_sale = product_info['integral_sale_id'] > 0
		self.rid = product_info['rid']

		if product_info['promotion_result']:
			#self.promotion = {PromotionRepository.get_promotion_from_dict_data(product_info['promotion_result'])}
			promotion_result = product_info['promotion_result']
			self.promotion = {
				'type_name': promotion_result['type'],
				'promotioned_product_price': promotion_result.get('promotion_price', -1),
			}

		self.id = product.id
		self.type = product.type
		self.name = product.name
		self.thumbnails_url = product.thumbnails_url
		self.pic_url = product.pic_url
		self.shelve_type = product.shelve_type
		self.supplier = product.supplier
		self.supplier_name = product.supplier_name
		self.supplier_user_id = product.supplier_user_id

		model = product.get_specific_model(product_info['model_name'])
		if model:
			self.original_price = model.price
			self.weight = model.weight
			self.stock_type = model.stock_type
			if not hasattr(product, 'min_limit'):
				self.min_limit = model.stocks
			self.stocks = model.stocks
		else:
			watchdog.error("none model product id {},model_name:{},woid:{}".format(product, product_info['model_name'], self.context['webapp_owner'].id))
			self.original_price = product.price
			self.weight = product.weight
			self.stock_type = product.stock_type
			if not hasattr(product, 'min_limit'):
				self.min_limit = 1
			self.stocks = 0
		self.model = model


	def has_premium_sale(self):
		"""
		订单商品是否使用了买赠促销
		"""
		
	@cached_context_property
	def postage_config(self):
		"""
		[property] 订单商品的运费策略
		"""
		product = self.context['product']
		webapp_owner = self.context['webapp_owner']

		if product.postage_type == mall_models.POSTAGE_TYPE_UNIFIED:
			#使用统一运费
			return {
				"id": -1,
				"money": product.unified_postage_money,
				"factor": None
			}
		else:
			return webapp_owner.system_postage_config

	def to_dict(self):
		data = business_model.Model.to_dict(self)
		data['postage_config'] = data['_postage_config']
		data['model'] = self.model.to_dict() if self.model else None
		return data




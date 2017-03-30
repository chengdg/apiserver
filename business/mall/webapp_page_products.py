# -*- coding: utf-8 -*-
"""@package business.mall.simple_products
携带基础商品信息的商品集合，用于商品列表页面的展示
"""

import json
from bs4 import BeautifulSoup
import math
import itertools
from operator import attrgetter
import pickle

from eaglet.decorator import param_required
#from wapi import wapi_utils
from bdem import msgutil
from eaglet.core.cache import utils as cache_util
from db.mall import models as mall_models
from eaglet.core import watchdog
from eaglet.core import paginator
from business import model as business_model 
import settings
from business.mall.product import Product
from util import redis_util
from business.mall.simple_product import CachedSimpleProduct


class WebAppPageProducts(business_model.Model):
	"""
	携带基础商品信息的商品集合
	"""

	def __init__(self, webapp_owner, webapp_user):
		business_model.Model.__init__(self)
		self.webapp_owner = webapp_owner
		self.webapp_user = webapp_user
		
	def get_by_product_ids(self, product_ids=None):
		# CachedSimpleProduct商品规格已经经过改价的处理,business_product.price_info中的就是展示的(包括改价后的平台)
		# products = [CachedSimpleProduct._get_from_db(product_id, self.webapp_owner) for product_id in product_ids]
		db_products = mall_models.Product.select().dj_where(id__in=product_ids)
		products = []
		for db_product in db_products:
			product = Product.from_model({"webapp_owner": self.webapp_owner,
									 	  'model': db_product,
									 	  "fill_options": {'with_price': True,
														   "with_product_promotion": True},
										  })
			products.append({
				'id': db_product.id,
				'name': db_product.name,
				'is_deleted': db_product.is_deleted,
				'thumbnails_url': db_product.thumbnails_url,
				# 商品的规格已经处理过改价
				'display_price': product.price_info['display_price'],
				'is_member_product': product.is_member_product,
				'supplier': product.supplier,
				'promotion_js': product.promotion.to_dict() if product.promotion else None,
				'integral_sale': product.integral_sale.to_dict() if product.integral_sale else None,
			})
		
		return products
	
	def get_by_category(self, category_id=None, count_per_page=None):
		product_ids = self.get_product_ids_from_category(category_id, count_per_page)
		return self.get_by_product_ids(product_ids)
	
	def get_product_ids_from_category(self, category_id, count_per_page):
		temp_key = '{wo:%s}_{co:%s}_pids' % (self.webapp_user.id, category_id)
		if cache_util.exists_key(temp_key):
			return redis_util.smemebers(temp_key)[:count_per_page]
		else:
			# mall_models.ProductPool.select().dj_where(product_id__in=product_ids,
			# 										  status=mall_models.PP_STATUS_ON,
			# 										  woid=corp_id)
			
			# 普通分组
			if category_id:
				product_relations = mall_models.CategoryHasProduct.select().dj_where(category_id=category_id)\
					.order_by(mall_models.CategoryHasProduct.display_index,
							  mall_models.CategoryHasProduct.created_at.desc())
	
				return [relation.product_id for relation in product_relations][:count_per_page]
			else:
				# 如果是自营
				if self.webapp_owner.user_profile.webapp_type:
					product_pools = mall_models.ProductPool.select().dj_where(woid=self.webapp_user.id,
																			  status=mall_models.PP_STATUS_ON)\
						.order_by(mall_models.ProductPool.display_index, mall_models.ProductPool.sync_at.desc)
					return [pool.product_id for pool in product_pools][:count_per_page]
				else:
					products = mall_models.Product.select().dj_where(owner_id=self.webapp_user.id,
																	 shelve_type=mall_models.PRODUCT_SHELVE_TYPE_ON)
					return [product.id for product in products][:count_per_page]

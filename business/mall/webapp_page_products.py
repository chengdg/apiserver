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
		results = []
		for product_id in product_ids:
			temp_key = 'product_simple_detail_{pid:%s}' % product_id
			cache_simple_product = cache_util.get_cache(temp_key)
			if cache_simple_product:
				# 如果是缓存中获取的,需要判断一下是否有改价
				price = cache_util.get_cache('customized_price_{wo:%s}_{pid:%s}'% (self.webapp_user.id, product_id))
				if price:
					cache_simple_product['display_price'] = price
				results.append(cache_simple_product)
			else:
				db_product = mall_models.Product.select().dj_where(id=product_id).first()
				product = Product.from_model({"webapp_owner": self.webapp_owner,
											  'model': db_product,
											  "fill_options": {'with_price': True,
															   "with_product_promotion": True},
											  })
				cache_product = {
					'id': product.id,
					'name': product.name,
					'is_deleted': product.is_deleted,
					'thumbnails_url': product.thumbnails_url,
					# 商品的规格已经处理过改价
					'display_price': product.price_info['display_price'],
					'is_member_product': product.is_member_product,
					'supplier': product.supplier,
					'categories': [],
					'promotion_js': product.promotion.to_dict() if product.promotion else None,
					'integral_sale': product.integral_sale.to_dict() if product.integral_sale else None,
				}
				temp_key = 'product_simple_detail_{pid:%s}' % product_id
				cache_util.set_cache(temp_key, cache_product)
				results.append(cache_product)
		return results
	
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
					if product_pools.count() > 0:
						
						return [pool.product_id for pool in product_pools][:count_per_page]
					else:
						return []
				else:
					products = mall_models.Product.select().dj_where(owner_id=self.webapp_user.id,
																	 shelve_type=mall_models.PRODUCT_SHELVE_TYPE_ON)
					return [product.id for product in products][:count_per_page]

# -*- coding: utf-8 -*-
"""@package business.mall.product
商品

Product是商品业务对象的实现，内部使用CachedProduct对象进行redis的读写操作。
OrderProduct，ShoppingCartProduct等更特定的商品业务对象都在内部使用Product业务对象实现。
"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from business.mall.realtime_stock import RealtimeStock
from business.mall.supplier import Supplier
from core.exceptionutil import unicode_full_stack
from eaglet.decorator import param_required
#from wapi import wapi_utils
from eaglet.core.cache import utils as cache_util
from db.mall import models as mall_models
from db.mall import promotion_models
from eaglet.core import watchdog
from business import model as business_model
import db.account.models as account_model
import settings
from business.mall.forbidden_coupon_product_ids import ForbiddenCouponProductIds
from business.mall.product_model_generator import ProductModelGenerator
from business.mall.product_model import ProductModel
from business.mall.promotion.promotion_repository import PromotionRepository
from business.decorator import cached_context_property


class CachedSimpleProduct(object):
	"""
	缓存的Product
	"""
	
	@staticmethod
	def get(product_id, webapp_owner):
		CachedSimpleProduct.webapp_owner = webapp_owner
		return CachedSimpleProduct.__get_from_cache(product_id)
	
	@staticmethod
	def __get_from_cache(product_id):
		key = 'product_simple_detail_{pid:%s}_{wo:%s}' % (product_id, CachedSimpleProduct.webapp_owner.id)
		# 此方法都经过pickle处理过
		product = cache_util.get_cache(key)
		if not product:
			return CachedSimpleProduct.__get_from_db(product_id)
		return product
	
	@staticmethod
	def __get_from_db(product_id):
		# TODO 修改成符合代码规范
		db_product = mall_models.Product.select().dj_where(id=product_id).first()
		if not db_product:
			return None
		db_images = mall_models.ProductSwipeImage.select().dj_where(product_id=product_id)
		is_deleted = CachedSimpleProduct.product_is_deleted(db_product)
		data = {
			'id': db_product.id,
			'name': db_product.name,
			'is_deleted': is_deleted,
			'swipe_images': [{
						'id': img.id,
						'url': '%s%s' % (settings.IMAGE_HOST, img.url) if img.url.find('http') == -1 else img.url,
						'linkUrl': img.link_url,
						'width': img.width,
						'height': img.height
						} for img in db_images],
		}
		# TODO 发消息
		key = 'product_simple_detail_{pid:%s}_{wo:%s}' % (product_id, CachedSimpleProduct.webapp_owner.id)
		cache_util.set_cache(key, data)
		return data
		
	@staticmethod
	def product_is_deleted(product):
	
		if mall_models.ProductPool.select().dj_where(product_id=product.id) > 0:
			#  同步商品
			if mall_models.ProductPool.select().dj_where(product_id=product.id,
													  woid=CachedSimpleProduct.webapp_owner.id,
													  status=mall_models.PP_STATUS_ON) > 0:
				return False
			return True
		else:
			if product.is_deleted:
				return True
			return False
		
	
class SimpleProduct(business_model.Model):
	"""
	商品
	"""
	__slots__ = (
		'id',
		'is_deleted',
		'name',
		'swipe_images',
	)
	# TODO 代码规范

	def from_id(args, webapp_owner, product_id):
		return CachedSimpleProduct.get(product_id, webapp_owner)

	def __init__(self, model=None):
		business_model.Model.__init__(self)

		if model:
			self._init_slot_from_model(model)
			
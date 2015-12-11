# -*- coding: utf-8 -*-
"""@package business.mall.allocator.OrderProductResourceAllocator
请求订单商品库存资源

"""
import logging
import json
import copy
from bs4 import BeautifulSoup
import math
import itertools
from datetime import datetime

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.product import Product
import settings
from business.decorator import cached_context_property
from business.resource.product_resource import ProductResource
from business.mall.allocator.product_resource_allocator import ProductResourceAllocator

class OrderProductResourceAllocator(business_model.Service):
	"""请求订单商品库存资源
	"""
	__slots__ = (
		'order'
		)

	def __init__(self, webapp_owner, webapp_user):
		business_model.Service.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

		self.context['product_resource_allocator'] = []


	def release(self, resources):
		if not resources:
			return 
		ProductResourceAllocator.release(resources)

	def __check_promotion(self, product):
		if product.has_expected_promotion() and not product.is_expected_promotion_active():
			return False, {
				"is_success": False,
				"type": 'promotion:expired',
				"msg": u"该活动已经过期",
				"short_msg": u"已经过期"
			}

		if not product.promotion:
			return True, {
				"is_success": True
			}

		is_can_use, check_result = product.promotion.check_usablity(self.context['webapp_user'], product)
		if not is_can_use:
			check_result['is_success'] = False
			return False, check_result

		return True, {
			"is_success": True
		}

	def __supply_product_info_into_fail_reason(self, product, result):
		result['id'] = product.id
		result['name'] = product.name
		result['stocks'] = product.stocks
		result['model_name'] = product.model_name
		result['pic_url'] = product.thumbnails_url

	def __merge_different_model_product(self, products):
		"""
		将同一商品的不同规格的商品进行合并，主要合并: purchase_count

		Parameters
			[in] products: ReservedProduct对象集合

		Returns
			合并后的ReservedProduct对象副本的集合
		"""
		id2product = {}
		for product in products:
			merged_product = id2product.get(product.id, None)
			if not merged_product:
				merged_product = copy.copy(product)
				id2product[product.id] = merged_product
			else:
				merged_product.purchase_count += product.purchase_count

		return id2product.values()

	def allocate_resource(self, order, purchase_info):
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		products = order.products

		#检查订单中商品的促销是否可用
		merged_products = self.__merge_different_model_product(products)
		for merged_product in merged_products:
			is_success, reason = self.__check_promotion(merged_product)
			if not is_success:
				self.__supply_product_info_into_fail_reason(merged_product, reason)
				return False, reason, None

		successed = False
		resources = []
		for product in products:
		 	product_resource_allocator = ProductResourceAllocator.get()
		 	successed, reason, resource = product_resource_allocator.allocate_resource(product)

		 	if not successed:
		 		self.release(resources)
		 		break
		 	else:
		 		resources.append(resource)

		if not successed:
			return False, reason, resources
		else:
		 	return True, reason, resources

		
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
from business.resource.products_resource import ProductsResource
from business.mall.allocator.product_resource_allocator import ProductResourceAllocator
from business.mall.merged_reserved_product import MergedReservedProduct

class OrderProductsResourceAllocator(business_model.Service):
	"""请求订单商品库存资源
	"""
	__slots__ = (
		'order'
		)

	def __init__(self, webapp_owner, webapp_user):
		business_model.Service.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

		self.context['resource2allocator'] = {}


	def release(self, resources):
		if not resources:
			return 

		release_resources = []
		for resource in resources:
			if resource.get_type() == business_model.RESOURCE_TYPE_PRODUCT:
				release_resources.append(resource)

		for release_resource in release_resources:
			resources = release_resource.resources

			for resource in resources:
				allocator = self.context['resource2allocator'].get(resource.model_id, None)
				if allocator:
					allocator.release()

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

		is_can_use, check_result = product.promotion.check_usability(self.context['webapp_user'], product)
		if not is_can_use:
			check_result['is_success'] = False
			return False, check_result

		return True, {
			"is_success": True
		}

	def __supply_product_info_into_fail_reason(self, product, result):
		if not 'id' in result:
			#如果失败原因中没有商品信息，则填充商品信息
			result['id'] = product.id
			result['name'] = product.name
			result['stocks'] = product.stocks
			result['model_name'] = product.model_name
			result['pic_url'] = product.thumbnails_url

	def __merge_different_model_product(self, products):
		"""
		将同一商品的不同规格的商品进行合并，主要合并

		Parameters
			[in] products: ReservedProduct对象集合

		Returns
			MergedReservedProduct对象集合
		"""
		id2product = {}
		for product in products:
			merged_reserved_product = id2product.get(product.id, None)
			if not merged_reserved_product:
				merged_reserved_product = MergedReservedProduct()
				merged_reserved_product.add_product(product)
				id2product[product.id] = merged_reserved_product
			else:
				merged_reserved_product.add_product(product)

		return id2product.values()

	def allocate_resource(self, order, purchase_info):
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		products = order.products

		#检查订单中商品的促销是否可用
		merged_reserved_products = self.__merge_different_model_product(products)
		for merged_reserved_product in merged_reserved_products:
			is_success, reason = self.__check_promotion(merged_reserved_product)
			if not is_success:
				self.__supply_product_info_into_fail_reason(merged_reserved_product, reason)
				return False, reason, None

		successed = False
		resources = []
		for product in products:
		 	product_resource_allocator = ProductResourceAllocator.get()
		 	successed, reason, resource = product_resource_allocator.allocate_resource(product)

		 	if not successed:
		 		self.__supply_product_info_into_fail_reason(product, reason)
		 		self.release(resources)
		 		break
		 	else:
		 		resources.append(resource)
		 		self.context['resource2allocator'][resource.model_id] = product_resource_allocator

		if not successed:
			return False, reason, None
		else:
			resource = ProductsResource(resources)
		 	return True, reason, resource

		
# -*- coding: utf-8 -*-
"""@package business.mall.allocator.OrderProductResourceAllocator
请求订单商品库存资源

"""
import logging
import json
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
			return {
				"is_success": False,
				"type": 'promotion:expired',
				"msg": u"该活动已经过期",
				"short_msg": u"已经过期"
			}

		return {
			"is_success": True
		}

	def __supply_product_info_into_fail_result(self, product, result):
		result['id'] = product.id
		result['name'] = product.name
		result['stocks'] = product.stocks
		result['model_name'] = product.model_name
		result['pic_url'] = product.thumbnails_url

	def allocate_resource(self, order, purchase_info):
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		products = order.products
		successed = False
		resources = []
		for product in products:
			#检查ReservedProduct的期望促销是否可用
			result = self.__check_promotion(product)
			if not result["is_success"]:
				self.__supply_product_info_into_fail_result(product, result)
				return False, result, None

		 	product_resource_allocator = ProductResourceAllocator.get()
		 	successed, reason, resource = product_resource_allocator.allocate_resource(product)
		 	if not successed:
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

		
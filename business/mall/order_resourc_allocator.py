# -*- coding: utf-8 -*-
"""@package business.mall.order_resource_allocator
订单资源分配器

"""

import json
from bs4 import BeautifulSoup
import math

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
from business.mall.integral_allocator import IntegralAllocator


class OrderResourceAllocator(business_model.Model):

	"""
	OrderResourceAllocator
	"""
	__slots__ = ('factory_order',)

	def __init__(self, webapp_owner, webapp_user, factory_order):
		business_model.Model.__init__(self)

		self.context['resources'] = [
			self.__integral_allocator
		]

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user
		self.factory_order = factory_order
		#self.roll_back_resources = []
		self.context['roll_back_resources'] = []

	def __integral_allocator(self):
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']
		integral_allocator = IntegralAllocator(webapp_owner, webapp_user, self.factory_order)
		self.context['roll_back_resources'].append(integral_allocator)
		result = integral_allocator.result

		if result['success']:
			self.factory_order.order.integral = result['data']['total_integral']
			self.factory_order.order.integral_money = result['data']['integral_money']

		return result


	def roll_back(self):
		for resource in self.context['roll_back_resources']:
			resource.roll_back()


	def allocated_resources(self):
		"""
		为订单分配资源

		@return
			is_valid: 是否有效
			reason: 当is_valid为False时，失效的理由
		"""
		failed_results = []
		for resource in self.context['resources']:
			result = resource()
			if not result['success']:
				failed_results.append(result)
				break

		if len(failed_results) > 0:
			#资源不够回滚数据
			self.roll_back()
			return {
				'is_valid': False,
				'reason': {
					'detail': self.__create_failed_reason(failed_results)
				}
			}
		else:
			return {'is_valid': True, 'order': self.factory_order.order}

	def __create_failed_reason(self, failed_results):
		details = []
		real_details = []
		for failed_result in failed_results:
			if failed_result['data'].has_key('detail'):
				for detail in failed_result['data']['detail']:
					details.append(detail)

		products_ids = [detail['id'] for detail in details]
		for id in products_ids:
			flag, index = self.__check_pro_id_in_detail_list(details,id)
			if flag:
				real_details.append(details[index])
				continue
			else:
				for detail in details:
					if detail['id'] == id:
						real_details.append(detail)
		
		return real_details
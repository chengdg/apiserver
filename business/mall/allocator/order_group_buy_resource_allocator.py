# -*- coding: utf-8 -*-
import json

import settings
from business import model as business_model
from business.mall.allocator.coupon_resource_allocator import CouponResourceAllocator
from business.mall.coupon.coupon import Coupon
from business.resource.coupon_resource import CouponResource

import requests

from business.resource.group_buy_resource import GroupBuyResource


class OrderGroupBuyAllocator(business_model.Service):
	__slots__ = ()


	def __init__(self, webapp_owner, webapp_user):
		business_model.Service.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

	def allocate_resource(self, order, purchase_info):
		if not purchase_info.group_id:
			return self.__return_empty_resource()

		# 检测purchase_info互斥


		group_buy_product_id = order.products[0].id

		# 检测活动可行性

		# 申请资源

		import requests
		url = 'http://' + settings.WEAPP_DOMAIN + '/m/apps/group/api/check_group_buy'
		param_data = {
			'member_id': self.context['webapp_user'].member.id,
			'group_id': purchase_info.group_id,
			'pid': group_buy_product_id,
			'woid': self.context['webapp_owner'].id
		}
		r = requests.get(url=url,params=param_data)
		print '*******************************************************'
		print(r.text)
		print '*******************************************************'
		group_buy_product_info = json.loads(r.text)['data']


		# mock_group_buy_product_info = {
		# 	'is_success': True,
		# 	'group_buy_price': 200,
		# 	'reason': 'asdasdasdasda',
		# }

		# group_buy_price = group_buy_info['group_buy_price']
		# reversed_product.price = group_buy_price

		# group_buy_product_info = mock_group_buy_product_info



		if not group_buy_product_info['is_success']:
			# 申请资源失败
			reason_dict = {
				"is_success": False,
				"msg": group_buy_product_info['reason'],
				"type": "group_buy"
			}
			return False, [reason_dict], None



		group_buy_resource = GroupBuyResource.get({
			'type': self.resource_type,
		})

		group_buy_resource.pid = group_buy_product_id
		group_buy_resource.group_buy_price = group_buy_product_info['group_buy_price']

		return True, '', group_buy_resource




	def release(self, resource):
		if resource.get_type() == self.resource_type:
			# 通知团购服务
			pass

	@property
	def resource_type(self):
		return business_model.RESOURCE_TYPE_GROUP_BUY

	def __return_empty_resource(self):
		print('-----x')
		empty_coupon_resource = GroupBuyResource.get({
			'type': self.resource_type,
		})
		return True, '',empty_coupon_resource

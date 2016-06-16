# -*- coding: utf-8 -*-
import json

import settings
from business import model as business_model
from business.resource.group_buy_resource import GroupBuyResource
from db.mall import models as mall_models


# 团购服务api接口
from util.microservice_consumer import microservice_consume

GroupBuyOPENAPI = {
	# 'group_buy_product': 'http://' + settings.WEAPP_DOMAIN + '/m/apps/group/api/group_buy_product',
	# 'group_buy_products': 'http://' + settings.WEAPP_DOMAIN + '/m/apps/group/api/group_buy_products',
	# 'order_action': 'http://' + settings.WEAPP_DOMAIN + '/m/apps/group/api/order_action',
	# 'check_group_buy': 'http://' + settings.WEAPP_DOMAIN + '/m/apps/group/api/check_group_buy',
	# 'group_buy_info': 'http://' + settings.WEAPP_DOMAIN + '/m/apps/group/api/group_buy_info',
	# 'get_group_url': 'http://' + settings.WEAPP_DOMAIN + '/m/apps/group/api/get_group_url',
	'group_buy_product': 'http://' + settings.WEAPP_DOMAIN + '/apps/group/api/group_buy_product',
	'group_buy_products': 'http://' + settings.WEAPP_DOMAIN + '/apps/group/api/group_buy_products',
	'order_action': 'http://' + settings.WEAPP_DOMAIN + '/apps/group/api/order_action',
	'check_group_buy': 'http://' + settings.WEAPP_DOMAIN + '/apps/group/api/check_group_buy',
	'group_buy_info': 'http://' + settings.WEAPP_DOMAIN + '/apps/group/api/group_buy_info',
	'get_group_url': 'http://' + settings.WEAPP_DOMAIN + '/apps/group/api/get_group_url',
}




class OrderGroupBuyAllocator(business_model.Service):
	__slots__ = ()


	def __init__(self, webapp_owner, webapp_user):
		business_model.Service.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

	def allocate_resource(self, order, purchase_info):
		webapp_user = self.context['webapp_user']
		# 检测是否团购订单
		if not purchase_info.group_id:
			return self.__return_empty_resource()

		# 检测purchase_info互斥
		is_success, reason = self.__check_purchase_info(purchase_info)

		# 检测是否重复下单
		# todo 寻觅peewe join的正确打开方式

		import business.mall.order as bussines_models
		orders = bussines_models.Order.get_orders_for_webapp_user({
			'webapp_owner': self.context['webapp_owner'],
			'webapp_user': webapp_user
		})

		# 过滤已取消的团购订单
		order_ids = [order.order_id for order in filter(lambda x: not(x.is_group_buy and x.status == mall_models.ORDER_STATUS_CANCEL), orders)]
		order_has_group_order_ids = [osg.order_id for osg in mall_models.OrderHasGroup.select().dj_where(group_id=purchase_info.group_id, webapp_user_id=webapp_user.id)]
		is_first_order = len(set(order_ids).intersection(order_has_group_order_ids)) == 0

		if not is_first_order:
			is_success = False
			reason = u'不可在一个团购中重复下单'


		pid = purchase_info.product_ids[0]

		if is_success:
			# 申请资源
			url = GroupBuyOPENAPI['check_group_buy']
			param_data = {
				'member_id': self.context['webapp_user'].member.id,
				'group_id': purchase_info.group_id,
				'pid': pid,
				'woid': self.context['webapp_owner'].id
			}
			is_success, group_buy_product_info = microservice_consume(url=url, data=param_data)
			if is_success:
				is_success = group_buy_product_info['is_success']
				reason = group_buy_product_info['reason']
			else:
				reason = '团购下单失败'
		if is_success:
			group_buy_resource = GroupBuyResource.get({
				'type': self.resource_type,
			})

			group_buy_resource.pid = pid
			group_buy_resource.group_buy_price = group_buy_product_info['group_buy_price']

			return True, '', group_buy_resource
		else:
			# 申请资源失败
			reason_dict = {
				"is_success": False,
				"msg": reason,
				"type": "group_buy"
			}
			return False, [reason_dict], None

	def release(self, resource):
		if resource.get_type() == self.resource_type:
			# 无资源需要释放
			pass

	@property
	def resource_type(self):
		return business_model.RESOURCE_TYPE_GROUP_BUY

	def __return_empty_resource(self):
		empty_coupon_resource = GroupBuyResource.get({
			'type': self.resource_type,
		})
		return True, '', empty_coupon_resource

	def __check_purchase_info(self, purchase_info):
		# 团购订单不能使用积分、优惠券
		if purchase_info.order_integral_info or purchase_info.group2integralinfo or purchase_info.coupon_id:
			return False, u'团购订单不能使用积分、优惠券'
		else:
			return True, u''

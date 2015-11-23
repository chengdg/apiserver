# -*- coding: utf-8 -*-
"""@package business.mall.order
订单，代表数据库中已经创建完成后的一个订单

"""

import json
from bs4 import BeautifulSoup
import math
import itertools
import uuid
import time
import random
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

class Order(business_model.Model):
	"""订单
	"""
	__slots__ = (
		'id',
		'order_id',
		'pay_interface_type',
		'final_price',
		'edit_money',

		'postage',
		'integral',
		'coupon_id',
		'status',
		'origin_order_id',
		'express_number',
		'created_at'
	)

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'order_id'])
	def from_id(args):
		"""工厂方法，根据订单id创建Order对象

		@return Order对象
		"""
		order = Order(args['webapp_owner'], args['webapp_user'], args['order_id'])
		return order

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user'])
	def get_orders_for_webapp_user(args):
		"""工厂方法，获取webapp_user对应的Order对象集合

		@return Order对象列表
		"""
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']
		order_models = list(mall_models.Order.select().dj_where(webapp_user_id=webapp_user.id))
		order_models.sort(lambda x,y: cmp(y.id, x.id))

		orders = []
		for order_model in order_models:
			order = Order(webapp_owner, webapp_user, None)
			order.context['order'] = order_model
			order._init_slot_from_model(order_model)
			order.context['is_valid'] = True
			orders.append(order)

		return orders

	@staticmethod
	def empty_order():
		"""工厂方法，创建空的Order对象

		@return Order对象
		"""
		order = Order(None, None, None)
		return order

	def __init__(self, webapp_owner, webapp_user, order_id):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

		if order_id:
			try:
				order_db_model = mall_models.Order.get(order_id=order_id)
				self.context['order'] = order_db_model
				self._init_slot_from_model(order_db_model)
				self.context['is_valid'] = True
			except:
				webapp_owner_id = webapp_owner.id
				error_msg = u"获得order_id('{}')对应的Order model失败, cause:\n{}"\
						.format(webapp_owner_id, unicode_full_stack())
				watchdog_error(error_msg, user_id=webapp_owner_id, noraise=True)
				self.context['is_valid'] = False

	@cached_context_property
	def product_outlines(self):
		"""订单中的商品概况，只包含最基本的商品信息

		TODO2：这里返回的依然是存储层的Product对象，需要返回业务层的Product业务对象
		"""
		product_ids = [r.product_id for r in mall_models.OrderHasProduct.select().dj_where(order=self.id)]
		products = list(mall_models.Product.select().dj_where(id__in=product_ids))

		return products

	@property
	def has_sub_order(self):
		"""
		[property] 该订单是否有子订单
		"""
		return self.origin_order_id == -1 and self.status > mall_models.ORDER_STATUS_NOT #未支付的订单按未拆单显示

	@property
	def pay_interface_name(self):
		"""
		[property] 订单使用的支付接口名
		"""
		return mall_models.PAYTYPE2NAME[self.pay_interface_type]

	def is_valid(self):
		"""
		判断订单是否有效

		@return True: 有效订单; False: 无效订单
		"""
		return self.context['is_valid']

	def pay(self, pay_interface_type):
		"""对订单进行支付

		@param[in] pay_interface_type: 支付所使用的支付接口的type
		"""
		pay_result = False

		if self.status == mall_models.ORDER_STATUS_NOT:
			#改变订单的支付状态
			pay_result = True

			now = datetime.now()
			if self.origin_order_id < 0:
				mall_models.Order.update(status=mall_models.ORDER_STATUS_PAYED_NOT_SHIP, pay_interface_type=pay_interface_type, payment_time=now).dj_where(origin_order_id=order.id)

			mall_models.Order.update(status=mall_models.ORDER_STATUS_PAYED_NOT_SHIP, pay_interface_type=pay_interface_type, payment_time=now).dj_where(order_id=self.order_id).execute()
			self.status = mall_models.ORDER_STATUS_PAYED_NOT_SHIP
			self.pay_interface_type = pay_interface_type

			#记录日志
			#record_operation_log(order_id, u'客户', u'支付')
			#record_status_log(order_id, u'客户', ORDER_STATUS_NOT, ORDER_STATUS_PAYED_NOT_SHIP)

			self.__send_notify_mail()

		return pay_result

	def __send_notify_mail(self):
		"""发送通知邮件
		"""
		print '[TODO2]: send order notify mail...'
		return
		order_has_products = OrderHasProduct.objects.filter(order=order)
		buy_count = ''
		product_name = ''
		product_pic_list = []
		for order_has_product in order_has_products:
			buy_count = buy_count+str(order_has_product.number)+','
			product_name = product_name+order_has_product.product.name+','
			product_pic_list.append(order_has_product.product.thumbnails_url)
		buy_count = buy_count[:-1]
		product_name = product_name[:-1]

		user = UserProfile.objects.get(webapp_id=order.webapp_id).user

		if order.coupon_id == 0:
			coupon = ''
		else:
			coupon = str(Coupon.objects.get(id=int(order.coupon_id)).coupon_id)+u',￥'+str(order.coupon_money)

		try:
			area = get_str_value_by_string_ids(order.area)
		except:
			area = order.area
		else:
			area = u''

		buyer_address = area+u" "+order.ship_address

		if order.status == 0:
			status = 0
			order_status = u"待支付"
		elif order.status == 3:
			status = 1
			order_status = u"待发货"
		elif order.status == 4:
			status = 2
			order_status = u"已发货"
		elif order.status == 5:
			status = 3
			order_status = u"已完成"
		elif order.status == 1:
			status = 4
			order_status = u"已取消"
		elif order.status == 6:
			status = 5
			order_status = u"退款中"
		elif order.status == 7:
			status = 6
			order_status = u"退款完成"
		else:
			status = -1
			order_status = ''

		try:
			member= WebAppUser.get_member_by_webapp_user_id(order.webapp_user_id)
			if member is not None:
				member_id = member.id
			else:
				member_id = -1
		except :
			member_id = -1

		if order.express_company_name:
			from tools.express.util import  get_name_by_value
			express_company_name = get_name_by_value(order.express_company_name)
		else:
			express_company_name = ""
		if order.express_number:
			express_number = order.express_number
		else:
			express_number = ''

		notify_order(
				user=user,
				member_id=member_id,
				status=status,
				order_id=order.order_id,
				buyed_time=time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time())),
				order_status=order_status,
				buy_count=buy_count,
				total_price=order.final_price,
				bill=order.bill,
				coupon=coupon,
				product_name=product_name,
				integral=order.integral,
				buyer_name=order.ship_name,
				buyer_address=buyer_address,
				buyer_tel=order.ship_tel,
				remark=order.customer_message,
				product_pic_list=product_pic_list,
				postage=order.postage,
				express_company_name=express_company_name,
				express_number=express_number
				)

	#===============================================================================
	# notify_order : 发送邮件
	#===============================================================================
	def notify_order(user, member_id, status, order_id, buyed_time, order_status, buy_count, total_price, bill, coupon, product_name, integral, buyer_name, buyer_address, buyer_tel, remark, product_pic_list, postage='0', express_company_name=None, express_number=None):
		order_notifys = UserOrderNotifySettings.objects.filter(user=user, status=status, is_active=True)
		if order_notifys.count() > 0 and str(member_id) not in order_notifys[0].black_member_ids.split('|') and order_notifys[0].emails != '':
			order_notify = order_notifys[0]
			content_list = []
			content_described = u'微商城-%s-订单' % order_status
			if order_id:
				if product_name:
					content_list.append(u'商品名称：%s' % product_name)
				if product_pic_list:
					pic_address = ''
					for pic in product_pic_list:
						pic_address = pic_address+"<img src='http://%s%s' width='170px' height='200px'></img>" % (settings.DOMAIN, pic)
					if pic_address != '':
						content_list.append(pic_address)
				content_list.append(u'订单号：%s' % order_id)
				if buyed_time:
					content_list.append(u'下单时间：%s' % buyed_time)
				if order_status:
					content_list.append(u'订单状态：<font color="red">%s</font>' % order_status)
				if express_company_name:
					content_list.append(u'<font color="red">物流公司：%s</font>' % express_company_name)
				if express_number:
					content_list.append(u'<font color="red">物流单号：%s</font>' % express_number)
				if buy_count:
					content_list.append(u'订购数量：%s' % buy_count)
				if total_price:
					content_list.append(u'支付金额：%s' % total_price)
				if integral:
					content_list.append(u'使用积分：%s' % integral)
				if coupon:
					content_list.append(u'优惠券：%s' % coupon)
				if bill:
					content_list.append(u'发票：%s' % bill)
				if postage:
					content_list.append(u'邮费：%s' % postage)
				if buyer_name:
					content_list.append(u'收货人：%s' % buyer_name)
				if buyer_tel:
					content_list.append(u'收货人电话：%s' % buyer_tel)
				if buyer_address:
					content_list.append(u'收货人地址：%s' % buyer_address)
				if remark:
					content_list.append(u'顾客留言：%s' % remark)
				
				# if member_id:
				# 	try:
				# 		member = Member.objects.get(id=member_id)
				# 		content_list.append(u'会员昵称：%s' % member.username_for_html)
				# 	except:
				# 		pass
					
			content = u'<br> '.join(content_list) 
			_send_email(user, order_notify.emails, content_described, content)

	def _send_email(user, emails, content_described, content):
		try:
			for email in emails.split('|'):
				if email.find('@') > -1:
					sendmail(email, content_described, content)
		except:
			notify_message = u"发送邮件失败user_id（{}）, cause:\n{}".format(user.id,unicode_full_stack())
			watchdog_warning(notify_message)

	def to_dict(self):
		return business_model.Model.to_dict(self, 'has_sub_order', 'pay_interface_name')


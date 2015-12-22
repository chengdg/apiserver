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

from core.exceptionutil import unicode_full_stack
from core.watchdog.utils import watchdog_alert, watchdog_warning, watchdog_error

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
#import resource
from business import model as business_model 
from business.mall.product import Product
from business.mall.order_products import OrderProducts
from business.mall.order_log_operator import OrderLogOperator
import settings
from business.decorator import cached_context_property
from utils import regional_util

from core.decorator import deprecated
import logging

class Order(business_model.Model):
	"""订单
	"""
	__slots__ = (
		'id',
		'order_id',
		'type',
		'pay_interface_type',
		'final_price',
		'product_price',
		'edit_money',

		'ship_name',
		'ship_tel',
		'ship_area',
		'ship_address',

		'postage',
		'integral',
		'integral_money',
		'coupon_money',
		
		'coupon_id',
		'status',
		'origin_order_id',
		'express_number',
		'customer_message',
		'promotion_saved_money',

		'created_at',
		'update_at',
		
		'supplier',
		'integral_each_yuan',
		'webapp_id',
		'webapp_user_id',
		'member_grade_id',
		'member_grade_discount',
		'buyer_name',

		'weizoom_card_money',
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
			#TODO2: this is ugly, need moved into __init__
			order.ship_area = regional_util.get_str_value_by_string_ids(order_model.area)
			order.context['is_valid'] = True
			orders.append(order)

		return orders


	@staticmethod
	@param_required(['webapp_owner', 'webapp_user'])
	def get_finished_orders_for_webapp_user(args):
		"""
		获取会员的所有已完成的订单

		@see Weapp源码`mall/models.py`中`Order.by_webapp_user_id`

		@todo 需要与get_orders_for_webapp_user()合并
		"""
		orders = Order.get_orders_for_webapp_user(args)
		# 改写自`Order.by_webapp_user_id(webapp_user_id).filter(status=5)` 
		completed = filter(lambda o: o.status==mall_models.ORDER_STATUS_SUCCESSED, orders)
		return completed


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

		self.coupon_money = 0.0
		self.integral_money = 0.0
		self.postage = 0.0
		self.edit_money = 0.0

		if order_id:
			try:
				order_db_model = mall_models.Order.get(order_id=order_id)
				self.context['order'] = order_db_model
				self._init_slot_from_model(order_db_model)
				self.context['is_valid'] = True
				self.ship_area = regional_util.get_str_value_by_string_ids(order_db_model.area)
			except:
				webapp_owner_id = webapp_owner.id
				error_msg = u"获得order_id('{}')对应的Order model失败, cause:\n{}"\
						.format(webapp_owner_id, unicode_full_stack())
				watchdog_error(error_msg, user_id=webapp_owner_id, noraise=True)
				self.context['is_valid'] = False
		else:
			# 用于创建空的Order model
			self.context['order'] = mall_models.Order()


	@cached_context_property
	def product_outlines(self):
		"""订单中的商品概况，只包含最基本的商品信息

		TODO2：这里返回的依然是存储层的Product对象，需要返回业务层的Product业务对象
		"""
		product_ids = [r.product_id for r in mall_models.OrderHasProduct.select().dj_where(order=self.id)]
		products = list(mall_models.Product.select().dj_where(id__in=product_ids))

		return products

	@property
	def sub_orders(self):
		"""拆单后的子订单信息
		"""
		sub_orders = []
		if self.has_sub_order:
			sub_order_ids = self.get_sub_order_ids()
			for sub_order_id in sub_order_ids:
				sub_order = Order.from_id({
					'webapp_owner': self.context['webapp_owner'],
					'webapp_user': self.context['webapp_user'],
					'order_id': sub_order_id
				})
				for product in self.products:
					#只要属于该子订单的商品
					if product.supplier == sub_order.supplier:
						sub_order.products.append(product.to_dict())
				sub_orders.append(business_model.Model.to_dict(sub_order, 'products'))

		return sub_orders

	def get_sub_order_ids(self):
		if self.has_sub_order:
			orders = mall_models.Order.select().dj_where(origin_order_id=self.id)
			sub_order_ids = [order.order_id for order in orders]
			return sub_order_ids
		else:
			return []

	@property
	def products(self):
		"""
		订单中的商品，包含商品的信息
		"""
		products = self.context.get('products', None)
		if not products:
			try:
				products = OrderProducts.get_for_order({
					'webapp_owner': self.context['webapp_owner'],
					'webapp_user': self.context['webapp_user'],
					'order': self,
				}).products
			except:
				import sys
				a, b, c = sys.exc_info()
				print a
				print b
				import traceback
				traceback.print_tb(c)

			self.context['products'] = products

		return products

	@products.setter
	def products(self, products):
		self.context['products'] = products

	@property
	def product_groups(self):
		return self.context['product_groups']

	@product_groups.setter
	def product_groups(self, product_groups):
		self.context['product_groups'] = product_groups
		
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

	@property
	def status_text(self):
		"""
		[property] 订单状态文本
		"""
		return mall_models.STATUS2TEXT[self.status]

	@cached_context_property
	def latest_express_detail(self):
		"""
		[property] 订单的最新物流详情
		"""
		#TODO2: 实现物流详情
		return None

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
				mall_models.Order.update(status=mall_models.ORDER_STATUS_PAYED_NOT_SHIP, pay_interface_type=pay_interface_type, payment_time=now).dj_where(origin_order_id=self.id).execute()

			mall_models.Order.update(status=mall_models.ORDER_STATUS_PAYED_NOT_SHIP, pay_interface_type=pay_interface_type, payment_time=now).dj_where(order_id=self.order_id).execute()
			self.status = mall_models.ORDER_STATUS_PAYED_NOT_SHIP
			self.pay_interface_type = pay_interface_type

			#记录日志
			OrderLogOperator.record_operation_log(self, u'客户', u'支付')
			OrderLogOperator.record_status_log(self, u'客户', mall_models.ORDER_STATUS_NOT, mall_models.ORDER_STATUS_PAYED_NOT_SHIP)

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


	def notify_order(user, member_id, status, order_id, buyed_time, order_status, buy_count, total_price, bill, coupon, product_name, integral, buyer_name, buyer_address, buyer_tel, remark, product_pic_list, postage='0', express_company_name=None, express_number=None):
		"""
		发送邮件，通知订单消息

		@todo 用模板改造沟通邮件内容的代码
		"""
		order_notifys = UserOrderNotifySettings.objects.filter(user=user, status=status, is_active=True)
		if order_notifys.count() > 0 and str(member_id) not in order_notifys[0].black_member_ids.split('|') and order_notifys[0].emails != '':
			# TODO: 可以用模板改造这段代码
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

	def to_dict(self, *extras):
		properties = ['has_sub_order', 'sub_orders', 'pay_interface_name', 'status_text']
		if extras:
			properties.extend(extras)

		order_status_info = self.status
		if self.has_sub_order:
			for sub_order in self.sub_orders:
				#整单的订单状态显示，如果被拆单，则显示订单里最滞后的子订单状态
				if sub_order['status'] < order_status_info:
					order_status_info = sub_order['status']

				#是否显示确认收货按钮交由前端进行判断 duhao
				# if sub_order['status'] == mall_models.ORDER_STATUS_PAYED_SHIPED and ((datetime.today() - sub_order['update_at']).days >= 3 or not self.express_number):
				# 	#已发货订单：有物流信息订单发货后3天显示确认收货按钮，没有物流的立即显示
				# 	if not hasattr(sub_order, 'session_data'):
				# 		sub_order['session_data'] = dict()
				# 	sub_order['session_data']['has_comfire_button'] = '1'

				# sub_order['has_promotion_saved_money'] = sub_order['promotion_saved_money > 0
				# sub_order['order_status_info'] = mall_models.STATUS2TEXT[sub_order['status']]

		result = business_model.Model.to_dict(self, *properties)
		# result['status_text'] = mall_models.STATUS2TEXT[order_status_info]

		#因为self.products这个property返回的是ReservedProduct或OrderProduct的对象集合，所以需要再次处理
		if 'products' in result:
			result['products'] = [product.to_dict() for product in result['products']]

		return result


	@property
	@deprecated
	def db_model(self):
		"""
		临时暴露order model，为了调试方便
		"""
		return self.context['order']


	def save(self):
		"""
		业务模型序列化
		"""
		db_model = self.context['order']

		# 读取基本信息
		db_model.webapp_id = self.webapp_id
		db_model.webapp_user_id = self.webapp_user_id
		db_model.member_grade_id = self.member_grade_id
		db_model.member_grade_discount = self.member_grade_discount
		db_model.buyer_name = self.buyer_name

		# 读取purchase_info信息
		db_model.ship_name = self.ship_name
		db_model.ship_address = self.ship_address
		db_model.ship_tel = self.ship_tel
		db_model.area = self.ship_area
		db_model.customer_message = self.customer_message
		db_model.type = self.type
		db_model.pay_interface_type = self.pay_interface_type
		db_model.order_id = self.order_id	

		if self.supplier:
			db_model.supplier = self.supplier

		if self.origin_order_id:
			db_model.origin_order_id = self.origin_order_id

		if self.coupon_id:
			db_model.coupon_id = self.coupon_id
			db_model.coupon_money = self.coupon_money

		db_model.integral = self.integral
		db_model.integral_money = self.integral_money
		db_model.integral_each_yuan = self.integral_each_yuan

		db_model.postage = self.postage
		db_model.promotion_saved_money = self.promotion_saved_money
		db_model.product_price = self.product_price
		db_model.final_price = self.final_price

		# 微众卡抵扣金额
		db_model.weizoom_card_money = self.weizoom_card_money
		
		logging.info("Order db_model: {}".format(db_model))

		db_model.save()
		self.id = db_model.id

		return

	@property
	def is_saved(self):
		"""
		是否保存成功

		@todo 待实现
		"""
		return True


	def update_status(self, action):
		"""
		更改订单状态

		已知action:
		'action' : 'pay' 支付
		'action' : 'finish' 完成
		'action' : 'cancel' 取消
		'action' : 'return_pay' 退款
		'action' : 'rship' 发货

		@todo 待完整实现
		"""
		operator_name = u'客户'

		if action == 'cancel':
			mall_models.Order.update(status=mall_models.ORDER_STATUS_CANCEL).dj_where(id=self.id).execute()
			# try:
			# 	# 返回订单使用的积分
			# 	if order.integral:
			# 		from modules.member.models import WebAppUser
			# 		from modules.member.integral import increase_member_integral
			# 		member = WebAppUser.get_member_by_webapp_user_id(order.webapp_user_id)
			# 		increase_member_integral(member, order.integral, u'取消订单 返还积分')
			# 	# 返回订单使用的优惠劵
			# 	if order.coupon_id:
			# 		from market_tools.tools.coupon.util import restore_coupon
			# 		restore_coupon(order.coupon_id)
			# 	# 返回商品的数量
			# 	__restore_product_stock_by_order(order)
			# 	mall_signals.cancel_order.send(sender=Order, order=order)
			# except :
			# 	notify_message = u"取消订单业务处理异常，cause:\n{}".format(unicode_full_stack())
			# 	watchdog_alert(notify_message, "mall")
		elif action == 'finish':
			mall_models.Order.update(status=mall_models.ORDER_STATUS_SUCCESSED).dj_where(id=self.id).execute()
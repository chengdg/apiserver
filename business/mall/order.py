# -*- coding: utf-8 -*-
"""@package business.mall.order
订单，代表数据库中已经创建完成后的一个订单

"""

import json
from bs4 import BeautifulSoup
#import math
#import itertools
#import uuid
import time
#import random
from datetime import datetime
import copy

import settings
from core.exceptionutil import unicode_full_stack
from core.sendmail import sendmail
from core.watchdog.utils import watchdog_alert, watchdog_warning, watchdog_error
import db.account.models as accout_models
from core.wxapi import get_weixin_api
from features.util.bdd_util import set_bdd_mock
from services.record_order_status_log_service.task import record_order_status_log
from services.update_product_sale_service.task import update_product_sale
from utils.regional_util import get_str_value_by_string_ids

#import settings
from wapi.decorators import param_required
from core.cache import utils as cache_util
from db.mall import models as mall_models
from business import model as business_model
from business.mall.product import Product
from business.mall.order_products import OrderProducts
from business.mall.log_operator import LogOperator
from business.mall.red_envelope import RedEnvelope
from business.spread.member_spread import MemberSpread
from business.decorator import cached_context_property
from utils import regional_util
from business.resource.order_resource_extractor import OrderResourceExtractor

from core.decorator import deprecated
import logging
from db.mall import promotion_models
from db.express import models as express_models
from business.mall.express.express_detail import ExpressDetail
from business.mall.express.express_info import ExpressInfo
from services.order_notify_mail_service.task import notify_order_mail
from business.mall.allocator.allocate_order_resource_service import AllocateOrderResourceService
from business.account.integral import Integral
from business.mall.pay_interface import PayInterface
from decimal import Decimal
from business.mall.allocator.allocate_price_related_resource_service import AllocatePriceRelatedResourceService



ORDER_STATUS2NOTIFY_STATUS = {
	mall_models.ORDER_STATUS_NOT: accout_models.PLACE_ORDER,
	mall_models.ORDER_STATUS_PAYED_NOT_SHIP: accout_models.PAY_ORDER,
	mall_models.ORDER_STATUS_PAYED_SHIPED: accout_models.SHIP_ORDER,
	mall_models.ORDER_STATUS_SUCCESSED: accout_models.SUCCESSED_ORDER,
	mall_models.ORDER_STATUS_CANCEL: accout_models.CANCEL_ORDER
}


ORDER_STATUS2SEND_PONINT = {
	mall_models.ORDER_STATUS_PAYED_NOT_SHIP: mall_models.PAY_ORDER_SUCCESS,
}

class Order(business_model.Model):
	"""订单
	"""
	__slots__ = (
		'id',
		'order_id',
		'type',
		'pay_interface_type',
		'payment_time',
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
		'raw_status',
		'status',
		'origin_order_id',
		'express_company_name',
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
	def empty_order(webapp_owner=None, webapp_user=None):
		"""工厂方法，创建空的Order对象

		@return Order对象
		"""
		order = Order(webapp_owner, webapp_user, None)
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

		@TODO：这里返回的依然是存储层的Product对象，需要返回业务层的Product业务对象
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
					#新的数据中已经有supplier字段了，但是为了兼容旧的数据，此处要做此处理
					if not product.supplier:
						_product = Product.from_id({
							'webapp_owner': self.context['webapp_owner'],
							'product_id': product.id
						})
						product.supplier = _product.supplier

					#只要属于该子订单的商品
					if product.supplier == sub_order.supplier:
						sub_order.products.append(product.to_dict())
				sub_orders.append(business_model.Model.to_dict(sub_order, 'products', 'latest_express_detail'))

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
	def is_sub_order(self):
		"""
		[property] 该订单是否是子订单
		"""
		return self.origin_order_id > 0

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

	@property
	def red_envelope(self):
		"""
		[property] 订单是否可领取红包
		"""
		red_envelope = self.context['webapp_owner'].red_envelope
		if RedEnvelope.can_show_red_envelope(self, red_envelope):
			return red_envelope['id']

		return 0

	@property
	def red_envelope_created(self):
		"""
		[property] 领取红包的记录是否已经建立，即是否已经领取过红包
		"""
		if promotion_models.RedEnvelopeToOrder.select().dj_where(order_id=self.id).count() > 0:
			return True

		return False

	@property
	def pay_info(self):
		if self.status == 0:
			pay_interface = PayInterface.from_type({
				"webapp_owner": self.context['webapp_owner'],
				"pay_interface_type": self.pay_interface_type
			})
			return pay_interface.get_pay_url_info_for_order(self)
		else:
			return {}


	@cached_context_property
	def latest_express_detail(self):
		"""
		[property] 订单的最新物流详情
		"""
		details = self.express_details
		if details:
			return details[-1].to_dict()
		return None

	@cached_context_property
	@deprecated
	def readable_express_company_name(self):
		"""
		可读的快递名称(中文)

		order.express_company_name是物流公司的英文名(拼音)，输出时转成中文名

		@todo 将readable_express_company_name, express_details等并到express_info(ExpressInfo对象)中
		弃用后请修改__send_notify_mail()中的调用
		"""
		return ExpressInfo.get_name_by_value(self.express_company_name)


	@property
	def express_details(self):
		"""
		[property] 订单的物流详情列表

		@return ExpressDetail对象list

		@see Weapp的`weapp/mall/models.py`中的`get_express_details()`
		"""
		# 为了兼容有order.id的方式
		db_details = express_models.ExpressDetail.select().dj_where(order_id=self.id).order_by(-express_models.ExpressDetail.display_index)
		if db_details.count() > 0:
			details = [ExpressDetail(detail) for detail in db_details]
			#return list(details)
			return details

		logging.info("express_company_name:{}, express_number:{}".format(self.express_company_name, self.express_number))
		expresses = express_models.ExpressHasOrderPushStatus.select().dj_where(
				express_company_name = self.express_company_name,
				express_number = self.express_number
			)
		if expresses.count() == 0:
			logging.info("No proper ExpressHasOrderPushStatus records.")
			return []

		try:
			express = expresses[0]
			logging.info("express: {}".format(express.id))
			db_details = express_models.ExpressDetail.select().dj_where(express_id=express.id).order_by(-express_models.ExpressDetail.display_index)
			details = [ExpressDetail(detail) for detail in db_details]
		except Exception as e:
			#innerErrMsg = full_stack()
			#watchdog_fatal(u'获取快递详情失败，order_id={}, case:{}'.format(order.id, innerErrMsg), EXPRESS_TYPE)
			logging.error(u'获取快递详情失败，order_id={}, case:{}'.format(self.id, str(e)))
			details = []
		return details


	def is_valid(self):
		"""
		判断订单是否有效

		@return True: 有效订单; False: 无效订单
		"""
		return self.context['is_valid']

	def __send_notify_mail(self):
		"""发送通知邮件

		@note 原来的发邮件用的是`weizoom.com`邮箱，发邮件有被拒收的风险。应该改成商用的发邮件服务，比如**mailgun**。

		"""

		# todo 修改
		order_has_products = mall_models.OrderHasProduct.select().dj_where(order=self.id)
		buy_count = ''
		product_name = ''
		product_pic_list = []
		for order_has_product in order_has_products:
			buy_count = buy_count+str(order_has_product.number)+','
			product_name = product_name+order_has_product.product.name+','
			product_pic_list.append(order_has_product.product.thumbnails_url)
		buy_count = buy_count[:-1]
		product_name = product_name[:-1]
		user = accout_models.UserProfile.get(webapp_id=self.webapp_id).user
		if self.coupon_id:
			coupon = str(promotion_models.Coupon.get(id=int(self.coupon_id)).coupon_id) + u',￥' + str(self.coupon_money)
		else:
			coupon = ''

		try:
			print(self.ship_area)
			area = get_str_value_by_string_ids(self.ship_area)
		except:
			area = self.ship_area

		buyer_address = area + u" " + self.ship_address
		order_status = self.status_text

		email_notify_status = ORDER_STATUS2NOTIFY_STATUS.get(self.status,-1)
		try:
			member = self.context['webapp_user'].member
			if member is not None:
				member_id = member.id
			else:
				member_id = -1
		except:
			member_id = -1

		express_company_name = self.readable_express_company_name

		if self.express_number:
			express_number = self.express_number
		else:
			express_number = ''

		notify_order_mail.delay(
				user_id=user.id,
				member_id=member_id,
				status=email_notify_status,
				order_id=self.order_id,
				buyed_time=time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time())),
				order_status=order_status,
				buy_count=buy_count,
				total_price=self.final_price,
				bill='',
				coupon=coupon,
				product_name=product_name,
				integral=self.integral,
				buyer_name=self.ship_name,
				buyer_address=buyer_address,
				buyer_tel=self.ship_tel,
				remark=self.customer_message,
				product_pic_list=product_pic_list,
				postage=self.postage,
				express_company_name=express_company_name,
				express_number=express_number
				)


	def to_dict(self, *extras):
		properties = ['has_sub_order', 'sub_orders', 'pay_interface_name', 'status_text', 'red_envelope', 'red_envelope_created', 'pay_info']
		if extras:
			properties.extend(extras)

		order_status_info = self.status
		if self.has_sub_order:
			for sub_order in self.sub_orders:
				#整单的订单状态显示，如果被拆单，则显示订单里最滞后的子订单状态
				if sub_order['status'] < order_status_info:
					order_status_info = sub_order['status']

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

		# 处理拆带相关字段
		products = self.products
		supplier_ids = []
		for product in products:
			supplier = product.supplier
			if supplier not in supplier_ids:
				supplier_ids.append(supplier)

		if len(supplier_ids) > 1:
			# 标记有子订单
			db_model.origin_order_id = -1
			self.origin_order_id = -1
		elif supplier_ids[0] != 0:
			self.supplier = supplier_ids[0]
			db_model.supplier = supplier_ids[0]

		db_model.save()
		self.id = db_model.id

		# 建立订单相关数据

		#建立<order, product>的关系
		for product in products:
			mall_models.OrderHasProduct.create(
				order = self.db_model,
				product = product.id,
				product_name = product.name,
				product_model_name = product.model_name,
				number = product.purchase_count,
				total_price = product.total_price,
				price = product.price,
				promotion_id = product.used_promotion_id,
				promotion_money = product.promotion_saved_money,
				grade_discounted_money=product.discount_money,
				integral_sale_id = product.integral_sale.id if product.integral_sale else 0
			)

		if len(supplier_ids) > 1:
			# 进行拆单，生成子订单
			for supplier in supplier_ids:
				new_order = copy.deepcopy(self.db_model)
				new_order.id = None
				new_order.order_id = '%s^%s' % (self.order_id, supplier)
				new_order.origin_order_id = self.id
				new_order.supplier = supplier
				new_order.save()

		product_groups = self.product_groups
		#建立<order, promotion>的关系
		for product_group in product_groups:
			if product_group.promotion:
				promotion = product_group.promotion
				promotion_result = product_group.promotion_result
				integral_money = 0
				integral_count = 0
				if promotion.type_name == 'integral_sale':
					integral_money = promotion_result['integral_money']
					integral_count = promotion_result['use_integral']
				mall_models.OrderHasPromotion.create(
						order=self.db_model,
						webapp_user_id=self.webapp_user_id,
						promotion_id=promotion.id,
						promotion_type=promotion.type_name,
						promotion_result_json=json.dumps(promotion_result.to_dict()),
						integral_money=integral_money,
						integral_count=integral_count,
				)


		self.__after_update_status('buy')

		return

	@property
	def is_saved(self):
		"""
		是否保存成功

		@todo 待实现
		"""
		return True


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
			self.payment_time = now
			self.raw_status = self.status
			self.status = mall_models.ORDER_STATUS_PAYED_NOT_SHIP
			self.pay_interface_type = pay_interface_type

			# 处理销量
			products = self.products

			product_sale_infos = []
			for product in products:
				# 赠品不计销量
				if product.promotion != {'type_name': 'premium_sale:premium_product'}:
					product_sale_infos.append({
						'product_id': product.id,
						'purchase_count': product. purchase_count
					})

			# 异步更新商品销量
			update_product_sale.delay(product_sale_infos)

			#支付后，更新会员支付数据
			webapp_user = self.context['webapp_user']
			webapp_user.update_pay_info(float(self.final_price) + float(self.weizoom_card_money), self.payment_time)

			self.__after_update_status('pay')
			self.__send_template_message()
		return pay_result


	def __release_order_resources(self):
		"""
		取消订单时，释放订单资源

		"""
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']
		order_resource_extractor = OrderResourceExtractor(webapp_owner, webapp_user)
		resources = order_resource_extractor.extract(self)
		
		# 释放价格无关资源
		service = AllocateOrderResourceService(webapp_owner, webapp_user)
		service.release(resources)

		# 释放价格有关资源
		service = AllocatePriceRelatedResourceService(webapp_owner, webapp_user)
		service.release(resources)

		# 需要删除WZCard的log
		# TODO: 待优化，应该在释放微众卡资源时删除wzcard_log
		LogOperator.remove_wzcard_logs_by_order_id(self.order_id)
			
		return


	def cancel(self):
		"""
		取消订单
		"""
		logging.info(u"Order id:{} is to be cancelled. Resources should be released first.".format(self.id))
		self.__release_order_resources()

		# 更新订单状态
		self.raw_status = self.status
		self.status = mall_models.ORDER_STATUS_CANCEL
		mall_models.Order.update(status=mall_models.ORDER_STATUS_CANCEL).dj_where(id=self.id).execute()

		# 更新子订单状态
		if self.origin_order_id == mall_models.ORIGIN_ORDER:
			# 此订单为主订单。更新其子订单也为“取消状态”
			mall_models.Order.update(status=mall_models.ORDER_STATUS_CANCEL).dj_where(origin_order_id=self.id).execute()

		# TODO: 发出cancel_order事件
		self.__after_update_status('cancel')


	def finish(self):
		"""
		完成订单（确认收货）
		"""

		# 更新红包引入消费金额的数据
		if self.coupon_id and promotion_models.RedEnvelopeParticipences.select().dj_where(coupon_id=self.coupon_id, introduced_by__gt=0).count() > 0:
			red_envelope2member = promotion_models.RedEnvelopeParticipences.get(promotion_models.RedEnvelopeParticipences.coupon_id==self.coupon_id)
			promotion_models.RedEnvelopeParticipences.update(introduce_sales_number = promotion_models.RedEnvelopeParticipences.introduce_sales_number + self.final_price + self.postage).dj_where(
				red_envelope_rule_id=red_envelope2member.red_envelope_rule_id,
				red_envelope_relation_id=red_envelope2member.red_envelope_relation_id,
				member_id=red_envelope2member.introduced_by
			).execute()

		# 更新订单状态
		mall_models.Order.update(status=mall_models.ORDER_STATUS_SUCCESSED).dj_where(id=self.id).execute()
		self.raw_status = self.status
		self.status = mall_models.ORDER_STATUS_SUCCESSED
		# 更新子订单状态
		if self.origin_order_id == -1:
			mall_models.Order.update(status=mall_models.ORDER_STATUS_SUCCESSED).dj_where(origin_order_id=self.id).execute()

		# 订单完成后会员积分处理
		Integral.increase_after_order_payed_finsh({
			'webapp_user': self.context['webapp_user'],
			'webapp_owner': self.context['webapp_owner'],
			'order_id': self.id
		})
		# 订单完成后更新会员等级
		self.context['webapp_user'].update_member_grade()
		self.__after_update_status('finish')

		# 通过分享链接来的订单处理
		# TODO-bert  优化celery中处理
		#try:
		MemberSpread.process_order_from_spread({
			'order_id': self.id,
			'webapp_user': self.context['webapp_user']
			})
		# except:
		# 	error_msg = u"MemberSpread.process_order_from_spread失败, cause:\n{}"\
		# 				.format(unicode_full_stack())
		# 	watchdog_error(error_msg)
		# 	print error_msg
		


	def __after_update_status(self, action):
		"""
		# 更改订单状态

		## 合法操作：
		* pay 支付
		* finish 完成
		* cancel 取消订单
		* buy 购买

		## 功能列表：
		### 共同功能
		* 更新订单状态
		* 记录操作日志
		* 设置父、子订单状态
		* 更新会员数据（消费次数、金额、平均客单价、等级、已购买标识）
		* 发邮件


		@warning 在此处加代码请注意子订单问题,此方法不能由子订单使用
		"""
		assert not self.is_sub_order

		#更新与webapp user对应的订单信息缓存数据
		self.context['webapp_user'].cleanup_order_info_cache()

		# 记录日志

		LogOperator.record_operation_log(self, u'客户', mall_models.ACTION2MSG[action])
		if self.raw_status:
			record_order_status_log.delay(self.order_id, u'客户', self.raw_status, self.status)
		self.__send_notify_mail()



	def __send_template_message(self):
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']
		# user_profile = UserProfile.objects.get(webapp_id=webapp_id)
		user_profile = webapp_owner.user_profile
		user = user_profile.user
		send_point = ORDER_STATUS2SEND_PONINT.get(self.status, '')
		template_message = mall_models.MarketToolsTemplateMessageDetail.select().dj_where(owner=user, template_message__send_point=send_point, status=1).first()
		if user_profile and template_message and template_message.template_id:
			mpuser_access_token = webapp_owner.weixin_mp_user_access_token
			if mpuser_access_token:
				try:
					message = self.__get_order_send_message_dict(user_profile, template_message, self, send_point)
					if settings.IS_UNDER_BDD:
						mock = dict()
						mock['touser'] = mpuser_access_token
						for key, value in message['data'].items():
							mock[key] = value['value']
						set_bdd_mock('template_message', mock)
						return False
					weixin_api = get_weixin_api(mpuser_access_token)
					result = weixin_api.send_template_message(message, True)

					#_record_send_template_info(order, template_message.template_id, user)
					# if result.has_key('msg_id'):
					# 	UserSentMassMsgLog.create(user_profile.webapp_id, result['msg_id'], MESSAGE_TYPE_TEXT, content)
					return True
				except:
					notify_message = u"发送模板消息异常, cause:\n{}".format(unicode_full_stack())
					watchdog_warning(notify_message)
					return False
			else:
				return False
		return True


	def __get_order_send_message_dict(self,user_profile, template_message, order, send_point):
		template_data = dict()
		social_account = self.context['webapp_user'].social_account
		if social_account and social_account.openid:
			template_data['touser'] = self.context['webapp_user'].openid
			template_data['template_id'] = template_message.template_id
			template_data['url'] = 'http://%s/mall/order_detail/?woid=%s&order_id=%s' % (settings.H5_DOMAIN, user_profile.user_id, order.order_id)
			template_data['topcolor'] = "#FF0000"
			detail_data = {}
			template_message_detail = template_message.template_message
			detail_data["first"] = {"value" : template_message.first_text, "color" : "#000000"}
			detail_data["remark"] = {"value" : template_message.remark_text, "color" : "#000000"}
			order.express_company_name =  u'%s快递' % self.readable_express_company_name
			if template_message_detail.attribute:
				attribute_data_list = template_message_detail.attribute.split(',')
				for attribute_datas in attribute_data_list:
					attribute_data = attribute_datas.split(':')
					key = attribute_data[0].strip()
					attr = attribute_data[1].strip()
					if attr == 'final_price' and getattr(order, attr):
						value = u'￥%s［实际付款］' % getattr(order, attr)
						detail_data[key] = {"value" : value, "color" : "#173177"}
					elif hasattr(order, attr):
						if attr == 'final_price':
							value = u'￥%s［实际付款］' % getattr(order, attr)
							detail_data[key] = {"value" : value, "color" : "#173177"}
						elif attr == 'payment_time':
							dt = datetime.now()
							payment_time = dt.strftime('%Y-%m-%d %H:%M:%S')
							detail_data[key] = {"value" : payment_time, "color" : "#173177"}
						else:
							detail_data[key] = {"value" : getattr(order, attr), "color" : "#173177"}
					else:
						order_products = OrderProducts.get_for_order({
							'webapp_owner': self.context['webapp_owner'],
							'webapp_user': self.context['webapp_user'],
							'order': order
						})

						if 'number' == attr:
							number = sum([product.count for product in order_products])
							detail_data[key] = {"value" : number, "color" : "#173177"}

						if 'product_name' == attr:
							products = self.products
							product_names =','.join([p.name for p in products])
							detail_data[key] = {"value" : product_names, "color" : "#173177"}
			template_data['data'] = detail_data
		return template_data
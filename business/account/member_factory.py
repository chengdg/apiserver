# -*- coding: utf-8 -*-
"""@package business.member.member_factory
订单生成器

"""

import json
from bs4 import BeautifulSoup
import math
import itertools
import uuid
import time
import random
import string
from hashlib import md5
from datetime import datetime

from wapi.decorators import param_required
from wapi import wapi_utils
# from cache import utils as cache_util
from db.member import models as member_models
import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
import settings
from business.decorator import cached_context_property
from business.account.member import Member


class MemberFactory(business_model.Model):
	"""会员成器
	"""
	__slots__ = (
		'id',
		'created',
	)

	@staticmethod
	@param_required(['webapp_owner', 'openid', 'for_oauth'])
	def create(args):
		"""工厂方法，创建Order对象

		@return Order对象
		"""
		member_factory = MemberFactory(args['webapp_owner'], args['openid'], args['for_oauth'])

		return member_factory

	def __init__(self, webapp_owner, openid, for_oauth):
		print '>>>>>>>>>>>>webapp_owner:', dir(webapp_owner)
		business_model.Model.__init__(self)
		self.context['created'] = True
		self.context['webapp_owner'] = webapp_owner
		self.context['openid'] = openid
		self.context['for_oauth'] = for_oauth

		print dir(webapp_owner)
		member_grades = webapp_owner.member_grades

		default_grade = None
		for grade in member_grades:
			if grade.is_default_grade:
				default_grade = grade
				break
		self.context['default_grade'] = default_grade
		self.context['default_tag'] = webapp_owner.default_member_tag



	def _generate_member_token(self, social_account):
		return "{}{}{}{}".format(
			social_account.webapp_id,
			social_account.platform,
			time.strftime("%Y%m%d"),
			(''.join(random.sample(string.ascii_letters + string.digits, 6))) + str(social_account.id))


	def save(self):
		"""保存订单
		"""
		webapp_owner = self.context['webapp_owner']
		member_grade = self.context['default_grade']
		for_oauth = self.context['for_oauth']
		openid = self.context['openid']

		member_business_object = Member.empty_member()
		webapp_id = webapp_owner.webapp_id

		token = md5('%s_%s' % (webapp_id, openid)).hexdigest()
		self.created = True
		sure_created = False		
		try:
			social_account = member_models.SocialAccount.get(webapp_id = webapp_id, openid = openid)
			print 'get_social_account>>>>>>>>>>>>>>>>>:',social_account
		except:
			social_account, sure_created = member_models.SocialAccount.get_or_create(
				platform = 0,
				webapp_id = webapp_id,
				openid = openid,
				token = token,
				is_for_test = False,
				access_token = '',
				uuid=''
			)
			print 'create_social_account>>>>>>>>>>>>>>>>>:',social_account
		
		if member_models.MemberHasSocialAccount.select().dj_where(webapp_id=webapp_id, account=social_account).count() >  0:
			self.created = False
		else:
		#默认等级
			#member_grade = member_models.MemberGrade.get_default_grade(webapp_id)
			if for_oauth:
				is_subscribed = False
				status = member_models.NOT_SUBSCRIBED
			else:
				is_subscribed = True
				status = member_models.SUBSCRIBED

			#temporary_token = _create_random()
			member_token = self._generate_member_token(social_account)
			member = member_models.Member.create(
				webapp_id = social_account.webapp_id,
				user_icon = '',#social_account_info.head_img if social_account_info else '',
				username_hexstr = '',
				grade = member_grade,
				remarks_name = '',
				token = member_token,
				is_for_test = social_account.is_for_test,
				is_subscribed = is_subscribed,
				status = status
			)
			# if not member:
			# 	return None

			member_models.MemberHasSocialAccount.create(
						member = member,
						account = social_account,
						webapp_id = webapp_id
						)

			member_models.WebAppUser.create(
				token = member.token,
				webapp_id = webapp_id,
				member_id = member.id
				)

			#添加默认分组
			#try:
			default_member_tag = self.context['default_tag']
			member_models.MemberHasTag.add_tag_member_relation(member, [default_member_tag.id])


			print 'TODO: create member info！！！！！！！！！！！！', member.id

			member_models.MemberInfo.create(
				member=member,
				name='',
				weibo_nickname=''
				)
			member_business_object.id = member.id
			member_business_object.created = self.created
			#member_business_object.is_subscribed = member.is_subscribed

			return member_business_object

		# member = webapp_user.member

		# order = mall_models.Order()
		# order_business_object = Order.empty_order()

		# purchase_info = self.purchase_info
		# ship_info = purchase_info.ship_info
		# order.ship_name = ship_info['name']
		# order.ship_address = ship_info['address']
		# order.ship_tel = ship_info['tel']
		# order.area = ship_info['area']

		# order.customer_message = purchase_info.customer_message
		# order.type = purchase_info.order_type
		# order.pay_interface_type = purchase_info.used_pay_interface_type
		# order_business_object.pay_interface_type = order.pay_interface_type

		# order.order_id = self.__create_order_id()
		# order_business_object.order_id = order.order_id
		# order.webapp_id = webapp_owner.webapp_id
		# order.webapp_user_id = webapp_user.id
		# order.member_grade_id = member.grade_id
		# _, order.member_grade_discount = member.discount

		# order.buyer_name = member.username_for_html

		# products = self.products
		# product_groups = self.product_groups

		# #处理订单中的product总价
		# order.product_price = sum([product.price * product.purchase_count for product in products])
		# order.final_price = order.product_price
		# #mall_signals.pre_save_order.send(sender=mall_signals, pre_order=fake_order, order=order, products=products, product_groups=product_groups, owner_id=request.webapp_owner_id)
		# order.final_price = round(order.final_price, 2)
		# if order.final_price < 0:
		# 	order.final_price = 0

		# #处理订单中的促销优惠金额
		# promotion_saved_money = 0.0
		# for product_group in product_groups:
		# 	promotion_result = product_group['promotion_result']
		# 	if promotion_result:
		# 		saved_money = promotion_result.get('promotion_saved_money', 0.0)
		# 		promotion_saved_money += saved_money
		# order.promotion_saved_money = promotion_saved_money

		# """
		# # 订单来自商铺
		# if products[0].owner_id == webapp_owner_id:
		# 	order.webapp_source_id = webapp_id
		# 	order.order_source = ORDER_SOURCE_OWN
		# # 订单来自微众商城
		# else:
		# 	order.webapp_source_id = WebApp.objects.get(owner_id=products[0].owner_id).appid
		# 	order.order_source = ORDER_SOURCE_WEISHOP
		# """
		# order.save()

		# #更新库存
		# for product in products:
		# 	product.consume_stocks()

		# #建立<order, product>的关系
		# supplier_ids = []
		# for product in products:
		# 	supplier = product.supplier
		# 	if not supplier in supplier_ids:
		# 		supplier_ids.append(supplier)

		# 	mall_models.OrderHasProduct.create(
		# 		order = order,
		# 		product = product.id,
		# 		product_name = product.name,
		# 		product_model_name = product.model_name,
		# 		number = product.purchase_count,
		# 		total_price = product.total_price,
		# 		price = product.price,
		# 		promotion_id = product.used_promotion_id,
		# 		promotion_money = product.promotion_money,
		# 		grade_discounted_money=product.discount_money
		# 	)

		# if len(supplier_ids) > 1:
		# 	# 进行拆单，生成子订单
		# 	order.origin_order_id = -1 # 标记有子订单
		# 	for supplier in supplier_ids:
		# 		new_order = copy.copy(order)
		# 		new_order.id = None
		# 		new_order.order_id = '%s^%s' % (order.order_id, supplier)
		# 		new_order.origin_order_id = order.id
		# 		new_order.supplier = supplier
		# 		new_order.save()
		# elif supplier_ids[0] != 0:
		# 	order.supplier = supplier_ids[0]
		# order.save()

		# #建立<order, promotion>的关系
		# for product_group in product_groups:
		# 	promotion_result = product_group.get('promotion_result', None)
		# 	if promotion_result or product_group.get('integral_sale_rule', None):
		# 		try:
		# 			promotion_id = product_group['promotion']['id']
		# 			promotion_type = product_group['promotion_type']
		# 		except:
		# 			promotion_id = 0
		# 			promotion_type = 'integral_sale'
		# 		try:
		# 			if not promotion_result:
		# 				promotion_result = dict()
		# 			promotion_result['integral_product_info'] = product_group['integral_sale_rule']['integral_product_info']
		# 		except:
		# 			pass
		# 		integral_money = 0
		# 		integral_count = 0
		# 		if product_group['integral_sale_rule'] and product_group['integral_sale_rule'].get('result'):
		# 			integral_money = product_group['integral_sale_rule']['result']['final_saved_money']
		# 			integral_count = product_group['integral_sale_rule']['result']['use_integral']
		# 		OrderHasPromotion.objects.create(
		# 			order=order,
		# 			webapp_user_id=webapp_user.id,
		# 			promotion_id=promotion_id,
		# 			promotion_type=promotion_type,
		# 			promotion_result_json=json.dumps(promotion_result),
		# 			integral_money=integral_money,
		# 			integral_count=integral_count,
		# 		)

		# if order.final_price == 0:
		# 	# 优惠券或积分金额直接可支付完成，直接调用pay_order，完成支付
		# 	self.pay_order(order.order_id, True, PAY_INTERFACE_PREFERENCE)
		# 	# 支付后的操作
		# 	#mall_signals.post_pay_order.send(sender=Order, order=order, request=request)

		# order_business_object.final_price = order.final_price
		# order_business_object.id = order.id
		# return order_business_object
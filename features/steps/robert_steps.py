# -*- coding: utf-8 -*-
import json

from behave import *

from features.util import bdd_util
from features.util.helper import WAIT_SHORT_TIME
from db.mall import models as mall_models
from db.mall import promotion_models
from db.member import models as member_models
from .steps_db_util import (
    get_custom_model_id_from_name, get_product_model_keys, get_area_ids
)

# 获取规格ids, 根据名称
def _get_product_model_ids_from_name(webapp_owner_id, model_name):
	if model_name is None or model_name == "standard":
		return "standard"
	return get_custom_model_id_from_name(webapp_owner_id ,model_name)

# 获取规格名称, 根据ids
def _get_product_model_name_from_ids(webapp_owner_id, ids):
	if ids is None or ids == "standard":
		return "standard"
	return get_custom_model_id_from_name(webapp_owner_id ,ids)

PAYNAME2ID = {
    u'全部': -1,
    u'微信支付': 2,
    u'货到付款': 9,
    u'支付宝': 0,
    u'优惠抵扣': 10
}

@when(u"{webapp_user_name}购买{webapp_owner_name}的商品")
def step_impl(context, webapp_user_name, webapp_owner_name):
	"""最近修改: yanzhao
	e.g.:
		{
			"order_id": "" # 订单号
			"ship_area": "",
			"ship_name": "bill",
			"ship_address": "",
			"ship_tel": "",
			"customer_message": "",
			"integral": "10",
			"integral_money": "10",
			"weizoom_card": [{"card_name":"", "card_pass": ""}],
			"coupon": "coupon_1",
			"date": "" # 下单时间
			"products": [
				{
					"count": "",
					"name": "",
					"promotion": {"name": ""},
					integral: ""
				},...
			]
		}
	"""
	if hasattr(context, 'caller_step_purchase_info') and context.caller_step_purchase_info:
		args = context.caller_step_purchase_info
	else:
		args = json.loads(context.text)

	def __get_current_promotion_id_for_product(product, member_grade_id):
		promotion_ids = [r.promotion_id for r in promotion_models.ProductHasPromotion.select().dj_where(product_id=product.id)]
		promotions = list(promotion_models.Promotion.select().dj_where(id__in=promotion_ids, status=promotion_models.PROMOTION_STATUS_STARTED).where(promotion_models.Promotion.type>3))
		if len(promotions) > 0 and (promotions[0].member_grade_id <= 0 or \
				promotions[0].member_grade_id == member_grade_id):
			# 存在促销信息，且促销设置等级对该会员开放
			return promotions[0].id
		return 0

	settings = member_models.IntegralStrategySttings.select().dj_where(webapp_id=context.webapp_id)
	integral_each_yuan = settings[0].integral_each_yuan

	member = bdd_util.get_member_for(webapp_user_name, context.webapp_id)
	group2integralinfo = dict()

	if webapp_owner_name == u'订单中':
		is_order_from_shopping_cart = "true"
		webapp_owner_id = context.webapp_owner_id
		product_ids = []
		product_counts = []
		promotion_ids = []
		product_model_names = []


		products = context.response.context['order'].products
		integral = 0
		integral_group_items = []
		for product in products:
			product_counts.append(str(product.purchase_count))
			product_ids.append(str(product.id))

			if hasattr(product, 'promotion'):
				promotion = Promotion.objects.get(name=product.promotion.name)
				promotion_ids.append(str(promotion.id))
			else:
				promotion_ids.append(str(__get_current_promotion_id_for_product(product_obj, member.grade_id)))
			product_model_names.append(_get_product_model_ids_from_name(webapp_owner_id, product.model_name))

			if hasattr(product, 'integral') and product.integral > 0:
				integral += product.integral
				integral_group_items.append('%s_%s' % (product.id, product.model['name']))
		if integral:
			group2integralinfo['-'.join(integral_group_items)] = {
				"integral": integral,
				"money": round(integral / integral_each_yuan, 2)
			}
	else:
		is_order_from_shopping_cart = "false"
		webapp_owner_id = bdd_util.get_user_id_for(webapp_owner_name)
		product_ids = []
		product_counts = []
		product_model_names = []
		promotion_ids = []
		products = args['products']
		# integral = 0
		# integral_group_items = []
		for product in products:
			product_counts.append(str(product['count']))
			product_name = product['name']
			product_obj = mall_models.Product.get(owner_id=webapp_owner_id, name=product_name)
			product_ids.append(str(product_obj.id))
			if product.has_key('promotion'):
				promotion = promotion_models.Promotion.get(name=product['promotion']['name'])
				promotion_ids.append(str(promotion.id))
			else:
				promotion_ids.append(str(__get_current_promotion_id_for_product(product_obj, member.grade_id)))
			_product_model_name = _get_product_model_ids_from_name(webapp_owner_id, product.get('model', None))
			product_model_names.append(_product_model_name)
			if 'integral' in product and product['integral'] > 0:
				# integral += product['integral']
				# integral_group_items.append('%s_%s' % (product_obj.id, _product_model_name))
				group2integralinfo['%s_%s' % (product_obj.id, _product_model_name)] = {
					"integral": product['integral'],
					"money": round(product['integral'] / integral_each_yuan, 2)
				}
		# if integral:
		# 	group2integralinfo['-'.join(integral_group_items)] = {
		# 		"integral": integral,
		# 		"money": round(integral / integral_each_yuan, 2)
		# 	}

	order_type = args.get('type', 'normal')

	# 处理中文地区转化为id，如果数据库不存在的地区则自动添加该地区
	ship_area = get_area_ids(args.get('ship_area'))

	data = {
		"woid": webapp_owner_id,
		"module": 'mall',
		"is_order_from_shopping_cart": is_order_from_shopping_cart,
		"target_api": "order/save",
		"product_ids": '_'.join(product_ids),
		"promotion_ids": '_'.join(promotion_ids),
		"product_counts": '_'.join(product_counts),
		"product_model_names": '$'.join(product_model_names),
		"ship_name": args.get('ship_name', "未知姓名"),
		"area": ship_area,
		"ship_id": 0,
		"ship_address": args.get('ship_address', "长安大街"),
		"ship_tel": args.get('ship_tel', "11111111111"),
		"is_use_coupon": "false",
		"coupon_id": 0,
		# "coupon_coupon_id": "",
		"message": args.get('customer_message', ''),
		"group2integralinfo": json.JSONEncoder().encode(group2integralinfo),
		"card_name": '',
		"card_pass": '',
		"xa-choseInterfaces": PAYNAME2ID.get(args.get("pay_type",""),-1)
	}
	if 'integral' in args and args['integral'] > 0:
		# 整单积分抵扣
		# orderIntegralInfo:{"integral":20,"money":"10.00"}"
		orderIntegralInfo = dict()
		orderIntegralInfo['integral'] = args['integral']
		if 'integral_money' in args:
			orderIntegralInfo['money'] = args['integral_money']
		else:
			orderIntegralInfo['money'] = round(int(args['integral'])/integral_each_yuan, 2)
		data["orderIntegralInfo"] = json.JSONEncoder().encode(orderIntegralInfo)
	if order_type == u'测试购买':
		data['order_type'] = mall_models.PRODUCT_TEST_TYPE
	if u'weizoom_card' in args:
		for card in args[u'weizoom_card']:
			data['card_name'] += card[u'card_name'] + ','
			data['card_pass'] += card[u'card_pass'] + ','

	#填充商品积分
	# for product_model_id, integral in product_integrals:
	# 	data['is_use_integral_%s' % product_model_id] = 'on'
	# 	data['integral_%s' % product_model_id] = integral

	#填充优惠券信息
	# 根据优惠券规则名称填充优惠券ID
	coupon = args.get('coupon', None)
	if coupon:
		data['is_use_coupon'] = 'true'
		data['coupon_id'] = coupon

	url = '/wapi/mall/order/?_method=put'
	response = context.client.post(url, data)
	context.response = response
	#response结果为: {"errMsg": "", "code": 200, "data": {"msg": null, "order_id": "20140620180559"}}

	# response_json = json.loads(context.response.content)

	# if response_json['code'] == 200:
	# 	# context.created_order_id为订单ID
	# 	context.created_order_id = response_json['data']['order_id']
	# else:
	# 	context.created_order_id = -1
	# 	context.response_json = response_json
	# 	context.server_error_msg = response_json['data']['msg']
	# 	print "buy_error----------------------------",context.server_error_msg,response
	# if context.created_order_id != -1:
	# 	if 'date' in args:
	# 		Order.objects.filter(order_id=context.created_order_id).update(created_at=bdd_util.get_datetime_str(args['date']))
	# 	if 'order_id' in args:
	# 		db_order = Order.objects.get(order_id=context.created_order_id)
	# 		db_order.order_id=args['order_id']
	# 		db_order.save()
	# 		if db_order.origin_order_id <0:
	# 			for order in Order.objects.filter(origin_order_id=db_order.id):
	# 				order.order_id = '%s^%s' % (args['order_id'], order.supplier)
	# 				order.save()
	# 		context.created_order_id = args['order_id']

	context.product_ids = product_ids
	context.product_counts = product_counts
	context.product_model_names = product_model_names
	context.webapp_owner_name = webapp_owner_name
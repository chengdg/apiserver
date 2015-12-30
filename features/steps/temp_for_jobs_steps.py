# -*- coding: utf-8 -*-
import json

from behave import *

from features.util import bdd_util
import steps_db_util
from db.mall import models as mall_models
from db.mall import promotion_models
from business.account.member import Member
from db.wzcard import models as wzcard_models

@then(u"{user}能获取商品'{product_name}'")
def step_impl(context, user, product_name):
	expected = json.loads(context.text)
	actual = __get_product(context, product_name)
	bdd_util.assert_dict(expected, actual)


@then(u"{user}能获得优惠券'{coupon_rule_name}'的码库")
def step_impl(context, user, coupon_rule_name):
	webapp_owner = context.webapp_owner
	db_coupon_rule = promotion_models.CouponRule.get(owner=webapp_owner.id, name=coupon_rule_name)
	db_coupons = promotion_models.Coupon.select().dj_where(coupon_rule_id=db_coupon_rule.id)
	
	actual = {}
	for coupon in db_coupons:
		member = None
		_coupon = {}
		_coupon['target'] = ''
		if coupon.member_id > 0:
			member = Member.from_id({
				'webapp_owner': webapp_owner,
				'member_id': coupon.member_id
			})
			_coupon['target'] = member.username_for_html
		_coupon['consumer'] = ''
		if coupon.status == promotion_models.COUPON_STATUS_USED:
			_coupon['consumer'] = member.username_for_html
		_coupon['status'] = promotion_models.COUPONSTATUS[coupon.status]['name']
		_coupon['money'] = float(coupon.money)
		actual[coupon.coupon_id] = _coupon

	expected_coupons = json.loads(context.text)
	bdd_util.assert_dict(expected_coupons, actual)


# @then(u"{user}能获取微众卡'{weizoom_card_id}'")
# def step_impl(context, user, weizoom_card_id):
# 	weizoom_card = wzcard_models.WeizoomCard.get(owner=context.webapp_owner_id, weizoom_card_id=weizoom_card_id)
# 	status2text = {
# 		0: u'未使用',
# 		1: u'已使用',
# 		2: u'已用完',
# 		3: u'未激活'
# 	}
# 	actual = {
# 		"status": status2text[weizoom_card.status],
# 		"price": 100.00
# 	}

# 	expected = json.loads(context.text)
# 	expected['price'] = float(expected['price'])

# 	bdd_util.assert_dict(expected, actual)


def __get_product(context, product_name):
	"""
	直接从数据库获取并填充商品数据
	"""
	webapp_owner_id = context.webapp_owner_id
	product_obj = mall_models.Product.get(owner=webapp_owner_id, name=product_name)
	response = context.client.get('/wapi/mall/product/', {
		'product_id': product_obj.id
	})

	product = response.body['data']

	actual = {
		"sales": product['sales'] if product['sales'] else 0,
		"name": product['name'],
		"thumbnails_url": product['thumbnails_url'],
		"pic_url": product['pic_url'],
		"detail": product['detail'],
		"status": u'在售' if product['shelve_type'] == mall_models.PRODUCT_SHELVE_TYPE_ON else u'待售',
		'stocks': product['total_stocks'],
		'is_use_custom_model': u'是' if product['is_use_custom_model'] else u'否',
		'model': {'models': {}},
		"is_member_product": 'on' if product['is_member_product'] else 'off',
		"promotion_title": product['promotion_title'],
	}

	models = product['models']
	if len(models) == 1:
		model = product['models'][0]
		model['stock_type'] = u'无限' if model['stock_type'] == mall_models.PRODUCT_STOCK_TYPE_UNLIMIT else u'有限'
		actual['model']['models'] = {
			'standard': model
		}
	else:
		for model in models:
			model['stock_type'] = u'无限' if model['stock_type'] == mall_models.PRODUCT_STOCK_TYPE_UNLIMIT else u'有限'
			actual['model']['models'][model['property2value']['name']] = model

	return actual
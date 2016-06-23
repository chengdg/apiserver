# -*- coding: utf-8 -*-
import json
import time

from behave import *

from db.mall.promotion_models import COUPONSTATUS
from features.util import bdd_util
from features.util.helper import WAIT_SHORT_TIME
from db.mall import models as mall_models
from db.member import models as member_models

from business.account.webapp_user import WebAppUser
from business.account.webapp_owner import WebAppOwner

from eaglet.core.cache import utils as cache_util
import logging

@then(u"{webapp_user_name}在{webapp_owner_name}的webapp中拥有{integral_count}会员积分")
def step_impl(context, webapp_user_name, webapp_owner_name, integral_count):
	#webapp_owner_id = context.webapp_owner_id
	response = context.client.get('/user_center/user_center/', {
	})
	
	##expected = json.loads(context.text)
	actual = response.body['data']['integral']

	expected = int(integral_count)
	context.tc.assertEquals(expected, actual)


@when(u"{webapp_user_name}获得{webapp_owner_name}的{integral_count}会员积分")
def step_impl(context, webapp_user_name, webapp_owner_name, integral_count):
	webapp_owner_id = context.webapp_owner_id
	webapp_id = bdd_util.get_webapp_id_for(webapp_owner_name)
	member = bdd_util.get_member_for(webapp_user_name, webapp_id)
	member_models.Member.update(integral=int(integral_count)).dj_where(id=member.id).execute()

	webapp_owner = WebAppOwner.get({
			'woid': webapp_owner_id
		})

	webapp_user = WebAppUser.from_member_id({
		'webapp_owner': webapp_owner,
		'member_id': member.id
		})
	if webapp_user:
		webapp_user.cleanup_cache()


@then(u'{webapp_user_name}在{webapp_owner_name}的webapp中获得积分日志')
def step_impl(context, webapp_user_name, webapp_owner_name):
	webapp_id = bdd_util.get_webapp_id_for(webapp_owner_name)
	member = bdd_util.get_member_for(webapp_user_name, webapp_id)
	integral_logs = list(member_models.MemberIntegralLog.select().dj_where(member_id=member.id).order_by(-member_models.MemberIntegralLog.id))
	json_data = json.loads(context.text)
	actual_list = []
	for data in integral_logs:
		actual_list.append({"content": data.event_type, "integral": data.integral_count})

	bdd_util.assert_list(actual_list, json_data)


@when(u"{user}访问个人中心")
def step_impl(context, user):
	webapp_owner_id = context.webapp_owner_id
	response = context.client.get('/user_center/user_center/', {
	})
	#response = context.client.get(bdd_util.nginx(url), follow=True)
	
	# member类型是<class 'modules.member.models.Member'>
	member = response.body['data']
	
	#context.user_center_stats = _get_stats_from_user_center_page(response.content)
	context.user_center_stats = {
		u'全部订单': member['history_order_count'],
		u'待支付': member['not_payed_order_count'],
		u'待发货': member['not_ship_order_count'],
		u'待收货': member['shiped_order_count'],
		u'购物车': member['shopping_cart_product_count'],
	}
	# dumping
	for k,v in context.user_center_stats.items():
		print("'%s': %d" % (k,v))


@then(u"'个人中心'中'{key}'数为{expected}")
def step_impl(context, key, expected):
	#print("expected order_count="+order_count)
	user_center_stats = context.user_center_stats
	print("key: %s, expected: %s" % (key, expected))
	for k,v in user_center_stats.items():
		print("'%s': %d" % (k,v))
	if user_center_stats is not None:
		context.tc.assertEquals(int(expected), user_center_stats[key])
	else:
		assert False

@then(u"'个人中心'中市场工具的数量为{expected}")
def step_impl(context, expected):
	pass


@then(u"{webapp_user_name}能获得优惠券列表")
def step_impl(context, webapp_user_name):
	response = context.client.get('/user_center/my_coupon/')
	unused_coupons = response.body['data']['unused_coupons']
	used_coupons = response.body['data']['used_coupons']
	expired_coupons = response.body['data']['expired_coupons']

	for coupon in unused_coupons + used_coupons + expired_coupons:
		coupon['status'] = COUPONSTATUS[coupon['status']]['name']
	unused_coupons = __sort(unused_coupons)
	used_coupons = __sort(used_coupons)
	expired_coupons = __sort(expired_coupons)
	actual = {'unused_coupons': unused_coupons, 'used_coupons': used_coupons, 'expired_coupons': expired_coupons}
	expected = json.loads(context.text)
	bdd_util.assert_dict(expected, actual)


def __sort(dict_array):
	return list(reversed(sorted(dict_array, key=lambda x: x['coupon_id'])))

@then(u"{webapp_user}成功获取个人中心的'待评价'列表")
def step_get_presonal_review_list(context, webapp_user):
	context.client = bdd_util.login(webapp_user)
	expected = json.loads(context.text)
	url = "/member/waiting_review_products"
	response = context.client.get(url, {
	})
	# response = context.client.get(bdd_util.nginx(url), follow=True)
	orders = response.body['data']['orders']
	actual = []
	if orders:
		for order in orders:
			#logging.error(order['order_is_reviewed'])	
			if not order['order_is_reviewed']:
				data = {}
				data['order_no'] = order['order_id']
				data['products'] = []
				for product in order['products']:
					# logging.error('>>>>>>>>>>>.1')
					# logging.error(product)
					# logging.error('>>>>>>>>>>>.2')
					if not product['has_review'] or not product['has_picture']:
						p_data = {}
						p_data['product_name'] = product['name']

					
						if  product['model']['property_values']:
							for mode in product['model']['property_values']:
								p_data['product_model_name'] = mode['name']
						# p_model_name = product['product_model_name']
						# if p_model_name:
						# 	the_model_name = ""
						# 	for model in p_model_name:
						# 		the_model_name += model['property_value']
						# 	p_data['product_model_name'] = the_model_name
						data['products'].append(p_data)
				actual.append(data)
	else:
		actual.append({})
	if not actual:
		actual.append({})

	# logging.error(actual)
	# logging.error(expected)
	bdd_util.assert_list(expected, actual)



# @then(u"订单'{order_no}'中'{product_name}'的评商品评价提示信息'{review_status}'")
# def step_get_user_publish_review(context, order_no, product_name, review_status):
# 	pass
# 	# product_review = bdd_util.get_product_review(order_no, product_name)
# 	# count = len(product_review.review_detail)
# 	# assert count > 200

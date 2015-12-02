# -*- coding: utf-8 -*-
"""@package wapi.mall.a_coupon
优惠券接口

@see Webapp中的`mall/promotion/coupon.py`
@todo 待清理
"""
import os

#from django.template import RequestContext
#from django.shortcuts import render_to_response
#from django.http import HttpResponse
#from excel_response import ExcelResponse
#from django.contrib.auth.decorators import param_required

#from core import resource
#from mall import export
#from mall.models import *
#from modules.member.models import WebAppUser
#from modules.member.module_api import get_member_by_id_list
#from core import paginator
#from models import *
#from core.jsonresponse import create_response, JsonResponse
#from core import search_util
#from mall.promotion.utils import create_coupons

COUNT_PER_PAGE = 20
PROMOTION_TYPE_COUPON = 4
FIRST_NAV_NAME = export.MALL_PROMOTION_AND_APPS_FIRST_NAV




"""
# 筛选数据构造
COUPON_FILTERS = {
	'coupon': [
		{
			'comparator': lambda coupon, filter_value: (filter_value == coupon.coupon_id),
			'query_string_field': 'couponCode'
		}, {
			'comparator': lambda coupon, filter_value: (filter_value == 'all') or (filter_value == str(coupon.status)),
			'query_string_field': 'useStatus'
		}
	],
	'member': [
		{
			'comparator': lambda member, filter_value: (filter_value in member.username_for_html),
			'query_string_field': 'memberName'
		}
	]
}


def _filter_reviews(args, coupons):
	has_filter = search_util.init_filters(args, COUPON_FILTERS)
	if not has_filter:
		# 没有filter，直接返回
		return coupons

	coupons = search_util.filter_objects(coupons, COUPON_FILTERS['coupon'])

	# 处理领取人
	member_name = args.GET.get('memberName', '')
	filter_coupons = coupons
	if member_name:
		member_ids = [c.member_id for c in coupons]
		members = get_member_by_id_list(member_ids)
		members = search_util.filter_objects(members, COUPON_FILTERS['member'])
		member_ids = [member.id for member in members]
		filter_coupons = []
		for coupon in coupons:
			if coupon.member_id in member_ids:
				filter_coupons.append(coupon)
	return filter_coupons
"""
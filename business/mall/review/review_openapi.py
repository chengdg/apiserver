# -*- coding: utf-8 -*-

import settings

#评论api接口
REVIEWOPENAPI = {
	'evaluates_from_product_id': 'http://' + settings.WEAPP_DOMAIN + '/apps/evaluate/api/get_product_evaluates/',
	# 'reviewed_count': 'http://' + settings.WEAPP_DOMAIN + '/m/apps/evaluate/review_count/',
	'reviewed_count': 'http://' + settings.WEAPP_DOMAIN + '/apps/evaluate/api/get_unreviewd_count/',
	'evaluates_from_member_id': 'http://' + settings.WEAPP_DOMAIN + '/apps/evaluate/api/get_product_evaluates_status/',
	'order_evaluates_from_member_id': 'http://' + settings.WEAPP_DOMAIN + '/apps/evaluate/api/get_order_evaluates/',
	
}
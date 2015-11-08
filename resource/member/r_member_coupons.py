# -*- coding: utf-8 -*-

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from core import resource
from wapi.decorators import param_required
from wapi import wapi_utils
from cache import utils as cache_util
from wapi.mall import models as mall_models
from wapi.mall import promotion_models
import settings
import resource
from core import inner_resource
from core.watchdog.utils import watchdog_alert


class RMemberCoupons(inner_resource.Resource):
	"""
	会员优惠券
	"""
	app = 'member'
	resource = 'member_coupons'

	@staticmethod
	def get_my_coupons(member_id):
		"""
		获取我所有的优惠券
		过滤掉 已经作废的优惠券
		"""
		#过滤已经作废的优惠券
		coupons = list(promotion_models.Coupon.select().dj_where(member_id=member_id, status__lt=promotion_models.COUPON_STATUS_DISCARD).order_by(-promotion_models.Coupon.provided_time))
		coupon_rule_ids = [c.coupon_rule_id for c in coupons]
		coupon_rules = promotion_models.CouponRule.select().dj_where(id__in=coupon_rule_ids)
		id2coupon_rule = dict([(c.id, c) for c in coupon_rules])
		# coupon_ids = []
		today = datetime.today()
		coupon_ids_need_expire = []
		for coupon in coupons:
			#添加优惠券使用限制
			coupon.valid_restrictions = id2coupon_rule[coupon.coupon_rule_id].valid_restrictions
			coupon.limit_product_id = id2coupon_rule[coupon.coupon_rule_id].limit_product_id
			coupon.name = id2coupon_rule[coupon.coupon_rule_id].name
			coupon.start_date = id2coupon_rule[coupon.coupon_rule_id].start_date
			# 优惠券倒计时
			if coupon.expired_time > today:
				valid_days = (coupon.expired_time - today).days
				if valid_days > 0:
					coupon.valid_time = '%d天' % valid_days
				else:
					#过期时间精确到分钟
					valid_seconds = (coupon.expired_time - today).seconds
					if valid_seconds > 3600:
						coupon.valid_time = '%d小时' % int(valid_seconds / 3600)
					else:
						coupon.valid_time = '%d分钟' % int(valid_seconds / 60)
				coupon.valid_days = valid_days
			else:
				# 记录过期并且是未使用的优惠券id
				if coupon.status == promotion_models.COUPON_STATUS_UNUSED:
					coupon_ids_need_expire.append(coupon.id)
					coupon.status = promotion_models.COUPON_STATUS_EXPIRED

		if len(coupon_ids_need_expire) > 0:
			promotion_models.Coupon.objects.filter(id__in=coupon_ids_need_expire).update(status=promotion_models.COUPON_STATUS_EXPIRED)

		return coupons


	@param_required(['member'])
	def get(args):
		member = args['member']
		coupons = RMemberCoupons.get_my_coupons(member.id)
		if 'return_model':
			return coupons
		else:
			coupons = [coupon.to_dict() for coupon in coupons]
			return coupons

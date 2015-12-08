# -*- coding: utf-8 -*-
"""@package wapi.mall.a_coupon_info
优惠券列表接口

@see Webapp中的`mall/promotion/coupon.py`

"""
import os

from core import api_resource
from wapi.decorators import param_required

#from excel_response import ExcelResponse

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


class ACouponInfo(api_resource.Resource):
	"""
	"""
	app = "mall2"
	resource = "coupon"

	@param_required
	def get(request):
		"""
		添加库存页面
		"""
		rule_id = request.GET.get('rule_id', '0')
		rules = CouponRule.objects.filter(id=rule_id)

		c = RequestContext(request, {
			'first_nav_name': FIRST_NAV_NAME,
			'second_navs': export.get_promotion_and_apps_second_navs(request),
			'second_nav_name': export.MALL_PROMOTION_SECOND_NAV,
			'third_nav_name': export.MALL_PROMOTION_COUPON_NAV,
			'rule': rules[0]
		})
		return render_to_response('mall/editor/promotion/create_coupon.html', c)

	@param_required
	def api_post(request):
		"""
		增加库存
		"""
		rule_id = request.POST.get('rule_id', '0')
		rules = CouponRule.objects.filter(id=rule_id)
		if len(rules) != 1:
			return create_response(500, '优惠券不存在')
		if rules[0].is_active == 0 or rules[0].end_date < datetime.now():
			return create_response(500, '优惠券已失效或者已过期')
		count = int(request.POST.get('count', '0'))
		create_coupons(rules[0], count)

		if rules[0].remained_count <= 0:
			rules.update(remained_count=0)    
		rules.update(
			count=(rules[0].count + count),
			remained_count=(rules[0].remained_count + count)
		)
		return create_response(200).get_response()

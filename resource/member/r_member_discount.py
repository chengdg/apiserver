# -*- coding: utf-8 -*-

import json

from bs4 import BeautifulSoup

from core import inner_resource
from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from wapi.mall import models as mall_models
import settings

class RMemberDiscount(inner_resource.Resource):
	"""
	商品详情
	"""
	app = 'member'
	resource = 'member_discount'

	@param_required(['member', 'webapp_owner_info'])
	def get(args):
		member = args['member']
		webapp_owner_info = args['webapp_owner_info']
		if not member:
			return -1, 100

		member_grade_id = member.grade_id
		member_grade = args['webapp_owner_info'].member2grade.get(member_grade_id, '')
		if member_grade:
			return member_grade_id, member_grade.shop_discount
		else:
			return member_grade_id, 100

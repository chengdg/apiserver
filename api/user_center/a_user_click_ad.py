# -*- coding: utf-8 -*-

import json
from datetime import datetime

from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.account.ad_clicked import AdClicked


class AUserClickAd(api_resource.ApiResource):
	"""
	点击萌版纪录
	"""
	app = 'user_center'
	resource = 'ad_click'

	@param_required([])
	def put(args):
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']
		member_id = webapp_user.member.id

		AdClicked.add_ad_clicked({
			"member_id": member_id
			})

		return {}

	# @param_required([])
	# def post(args):
	# 	webapp_user = args['webapp_user']
	# 	webapp_owner = args['webapp_owner']
	# 	member_id = webapp_user.member.id

	# 	AdClicked.add_ad_clicked({
	# 		"member_id": member_id
	# 		})

	# 	return {}
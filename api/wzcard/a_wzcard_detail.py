# -*- coding: utf-8 -*-
"""
微众卡详情
"""

# import copy
# from datetime import datetime

from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.wzcard.wzcard import WZCard

class ACardDetail(api_resource.ApiResource):
	"""
	微众卡详情
	"""
	app = 'wzcard'
	resource = 'detail'
	

	@param_required(['card_id'])
	def get(args):
		"""
		获取虚拟卡列表
		"""
		# webapp_owner = args['webapp_owner']
		# webapp_user = args['webapp_user']
		# card_id = args['card_id']
		card_detail = WZCard.from_member_card_id(args)


		return {
		"weizoom_card":card_detail,

		}

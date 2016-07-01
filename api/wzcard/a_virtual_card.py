# -*- coding: utf-8 -*-
"""
虚拟卡列表
"""

# import copy
# from datetime import datetime

from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.mall.virtual_product_has_code import VirtualProductHasCode

class AVirtualCard(api_resource.ApiResource):
	"""
	虚拟卡列表
	"""
	app = 'wzcard'
	resource = 'virtual_wzcard'


	@param_required([])
	def get(args):
		"""
		获取虚拟卡列表
		"""
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']

		cards, has_expired_cards = VirtualProductHasCode.handle_from_webapp_user({"webapp_owner":webapp_owner, "webapp_user":webapp_user})

		virtual_wzcard_data = {
		"cards":cards,
		"has_expired_cards":has_expired_cards
		}
		return virtual_wzcard_data

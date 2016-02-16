# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required

#import resource

class WebAppOwnerInfo(api_resource.ApiResource):
	"""
	商品
	"""
	app = 'user'
	resource = 'webapp_owner_info'

	@param_required(['woid'])
	def get(args):
		"""
		创建商品
		"""
		webapp_owner = args['webapp_owner']

		data = {}
		data['qrcode_img'] = webapp_owner.qrcode_img
		data['mp_head_img'] = webapp_owner.mp_head_img
		data['mp_nick_name'] = webapp_owner.mp_nick_name
		return data
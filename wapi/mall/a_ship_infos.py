# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required


class AShipInfos(api_resource.ApiResource):
	"""
	商品
	"""
	app = 'mall'
	resource = 'ship_infos'

	@param_required([])
	def get(args):
		"""
		获取收货地址列表

		"""
		webapp_user = args['webapp_user']
		ship_infos = webapp_user.ship_infos
		data = {
			'ship_infos': ship_infos
		}
		return data

	@param_required(['ship_id'])
	def post(args):
		"""
		选择默认收货地址
		Returns:ship_id

		"""
		webapp_user = args['webapp_user']
		result = webapp_user.select_default_ship(args['ship_id'])
		if result:
			return {
				'result': result,
			}
		else:
			return 500

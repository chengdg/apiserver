# -*- coding: utf-8 -*-
from core import api_resource
from wapi.decorators import param_required
from business.mall.regional import Regional

class ARegional(api_resource.ApiResource):
	"""
	收货地址调用的地区信息
	"""
	app = 'mall'
	resource = 'regional'

	@param_required(['type', 'id'])
	def get(args):
		"""
		@param type
		@param id
		@return
		{
			'regional_info': regional_info
		}
		"""
		regional = Regional()
		regional_type = args['type']
		regional_id = args['id']

		if regional_type == 'provinces':
			regional_info = regional.get_all_provinces()
		elif regional_type == 'cities':
			regional_info = regional.get_cities_for_province(regional_id)
		elif regional_type == 'districts':
			regional_info = regional.get_districts_for_city(regional_id)
		else:
			# Todo watchdog
			return 500
		return{
			'regional_info': regional_info
		}


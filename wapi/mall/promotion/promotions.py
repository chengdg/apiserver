# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required
#from wapi.wapi_utils import create_json_response


class Promotions(api_resource.ApiResource):
	"""
	商品促销信息

	"""
	app = 'mall'
	resource = 'promotions'

	@param_required([])
	def get(args):
		"""
		获取商品详情

		@param id 商品ID
		"""
		print("in promotions()")
		return {"name":"promotions"}

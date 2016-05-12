# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required
from business.mall.product_search import ProductSearch


class AProductSearch(api_resource.ApiResource):
	"""
	获取商品的评论列表
	"""
	app = 'mall'
	resource = 'product_search_records'

	@param_required([])
	def get(args):
		webapp_user = args['webapp_user']
		records = ProductSearch.get_records_by_webapp_user({"webapp_user_id": webapp_user.id})
		return {
			'records': records
		}

	@param_required([])
	def delete(args):
		webapp_user = args['webapp_user']
		ProductSearch.delete_record_by_webapp_user({"webapp_user_id": webapp_user.id})
		return {}

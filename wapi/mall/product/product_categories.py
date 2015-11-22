# -*- coding: utf-8 -*-
"""
商品分类相关
"""

from core import api_resource
from wapi.decorators import param_required
from utils import dateutil as utils_dateutil
from db.mall import models as mall_models
from db.account import models as auth_models

class ProductCategories(api_resource.ApiResource):
	"""
	获取WebAPP ID
	"""
	app = 'mall'
	resource = 'product_categories'

	@staticmethod
	def category_to_dict(category):
		return {
			"id": category.id,
			"oid": category.owner_id,
			"name": category.name,
			"product_count": category.product_count,
			"created_at": utils_dateutil.datetime2string(category.created_at)
		}

	@param_required(['woid'])
	def get(args):
		"""
		获得分类集合

		@param oid 分类所属user的id
		"""
		categories = mall_models.ProductCategory.select().where(mall_models.ProductCategory.owner == args['woid'])
		data = []
		for category in categories:
			data.append(ProductCategories.category_to_dict(category))

		return data



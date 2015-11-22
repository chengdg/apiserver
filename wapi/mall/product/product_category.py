# -*- coding: utf-8 -*-
"""
商品分类相关
"""

from core import api_resource
from wapi.decorators import param_required
from utils import dateutil as utils_dateutil
from db.mall import models as mall_models
from db.account import models as auth_models

class ProductCategory(api_resource.ApiResource):
	"""
	获取WebAPP ID
	"""
	app = 'mall'
	resource = 'product_category'

	@staticmethod
	def category_to_dict(category):
		return {
			"id": category.id,
			"oid": category.owner_id,
			"name": category.name,
			"product_count": category.product_count,
			"created_at": utils_dateutil.datetime2string(category.created_at)
		}


	@param_required(['id'])
	def get(args):
		"""
		获得分类详情

		@param id 分类ID
		"""
		category = mall_models.ProductCategory.get(mall_models.ProductCategory.id == args['id'])
		return ProductCategory.category_to_dict(category)


	@param_required(['id', 'name'])
	def post(args):
		"""
		修改Category的名字
		"""
		category = mall_models.ProductCategory.get(mall_models.ProductCategory.id == args['id'])
		category.name = args['name']
		category.save()
		return ProductCategory.category_to_dict(category)


	@param_required(['oid', 'name'])
	def put(args):
		"""
		创建分类
		"""
		owner = auth_models.User.get(auth_models.User.id == args['oid'])
		category = mall_models.ProductCategory.create(
			owner=owner,
			name=args.get('name', '').strip()
		)
		category.save()
		return ProductCategory.category_to_dict(category)



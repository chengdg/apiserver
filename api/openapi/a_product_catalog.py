# -*- coding: utf-8 -*-
"""@package api.product.a_product_catalog
订单API

"""

import copy
from datetime import datetime
from eaglet.core import api_resource
from core.exceptionutil import unicode_full_stack
from eaglet.decorator import param_required
from business.mall.product_catalog import ProductCatalog
from eaglet.core import watchdog


class AProductCatalog(api_resource.ApiResource):
	"""
	商品分类信息
	"""
	app = 'product'
	resource = 'product_catalogs'

	@staticmethod
	def catalog_to_dict(catalog):
		return {
			"id": catalog.id,
			"name": catalog.name,
			"level": catalog.level,
			"father_id": catalog.father_id
		}

	def get(args):
		"""
		openapi 获取商品分类信息操作
		"""

		product_catalogs = ProductCatalog.get_product_catalogs()
		data = []
		if product_catalogs:
			for catalog in product_catalogs:
				data.append(AProductCatalog.catalog_to_dict(catalog)) 
			return data
		else:
			return False

# -*- coding: utf-8 -*-
"""@package api.product.a_product_classification
订单API

"""

import copy
from datetime import datetime
from eaglet.core import api_resource
from core.exceptionutil import unicode_full_stack
from eaglet.decorator import param_required
from business.mall.product_classification import ProductClassification
from eaglet.core import watchdog


class AProductClassification(api_resource.ApiResource):
	"""
	商品分类信息
	"""
	app = 'product'
	resource = 'product_classifications'

	@staticmethod
	def classification_to_dict(classification):
		return {
			"id": classification.id,
			"name": classification.name,
			"level": classification.level,
			"father_id": classification.father_id
		}

	def get(args):
		"""
		openapi 获取商品分类信息操作
		"""

		product_classifications = ProductClassification.get_product_classifications()
		data = []
		if product_classifications:
			for classification in product_classifications:
				data.append(AProductClassification.classification_to_dict(classification)) 
			return {'data':data}
		else:
			return {'data':''}

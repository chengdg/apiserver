#coding: utf8
"""@package business.mall.resource.order_resource_extractor.OrderResourceExtractor
资源抽取器


"""

from business import model as business_model 
from business.mall.integral.integral_resource_extractor import IntegralResourceExtractor

import logging

class OrderResourceExtractor(business_model.Model):
	"""
	资源抽取器

	负责从purchase_info中抽取各种resource并合并同类resource
	"""
	__slots__ = (
		'__extractors',
	)

	def __init__(self):
		self.__extractors = []
		self.register_extractor(IntegralResourceExtractor())
		return

	def register_extractor(self, extractor):
		self.__extractors.append(extractor)
		return

	def extract(self, purchase_info):
		"""
		抽取并合并资源

		@param purchase_info 购买信息
		@return 各种Resource的list
		"""
		return []

	def _merge(self, resources):
		"""
		合并同类资源

		@param Resource list
		@return 合并后的Resource list
		"""
		return resources

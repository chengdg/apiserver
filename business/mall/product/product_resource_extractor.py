#coding: utf8
"""
商品资源抽取器
"""
from business import model as business_model 

class ProductResourceExtractor(business_model.Model):
	"""
	商品资源抽取器
	"""

	def extract(self, order, purchase_info):
		"""
		根据purchase_info抽取resource

		@return Resource对象
		"""
		# 抽取商品资源信息

		return []


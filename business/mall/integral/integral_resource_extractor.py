#coding: utf8
from business import model as business_model 

class IntegralResourceExtractor(business_model.Model):
	"""
	积分资源抽取器
	"""

	def extract(self, purchase_info):
		"""
		根据purchase_info抽取resource

		@return Resource对象
		"""
		return []

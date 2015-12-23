#coding: utf8
"""@package business.mall.resource.order_resource_extractor.OrderResourceExtractor
资源抽取器


"""

class OrderResourceExtractor(object):
	"""
	资源抽取器

	负责从purchase_info中抽取各种resource并合并同类resource
	"""

	def __init__(self):
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

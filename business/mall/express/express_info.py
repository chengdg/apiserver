#coding: utf8
"""
订单中的物流信息
"""

from business import model as business_model 
from core.decorator import deprecated
import json

class ExpressInfo(business_model.Model):
	__slots__ = (
	)

	def __init__(self):
		business_model.Model.__init__(self)

	@staticmethod
	@deprecated
	def __get_express_company_json():
		"""
		获得快递公司信息, 读取json文件
		
		@see 原Weapp的`weapp/tools/express/util.py`
		@todo 待优化（比如数据存入数据库）	
		"""
		file = open("data/express_company.json", 'rb')
		data_json = json.load(file)
		return data_json

	@staticmethod
	@deprecated
	def get_name_by_value(value):
		"""
		根据快递公司value(英文名)，获取快递公司名称

		@see 原Weapp的`weapp/tools/express/util.py`
		"""
		if not value:
			return ''

		data_json = ExpressInfo.__get_express_company_json()
		for item in data_json:
			if item['value'] == value:
				return item['name']
		return value


	@property
	def express_number(self):
		return
#coding: utf8
"""@package wapi.mall.a_express_detail
快递详情
"""

from core import api_resource
from wapi.decorators import param_required
from business.mall.order import Order

class AExpressDetails(api_resource.ApiResource):
	"""
	物流详情
	"""
	app = 'mall'
	resource = 'express_details'

	@staticmethod
	def to_dict(express_detail):
		return express_detail.to_dict()

	@param_required(['woid', 'order_id'])
	def get(args):
		"""
		获取物流详情

		结果示例：
		```
		{
		  "code": 200,
		  "data": {
		    "express_details": [
		      {
		        "status": "2",
		        "express_id": 13241234,
		        "created_at": "2015-12-22 17:04:54",
		        "display_index": 2,
		        "ftime": "2015-12-22",
		        "context": "哈哈1",
		        "time": "2015-12-22 17:04:39",
		        "id": 2
		      },
		      {
		        "status": "1",
		        "express_id": 147258368,
		        "created_at": "2015-12-22 16:22:39",
		        "display_index": 1,
		        "ftime": "2015-12-22",
		        "context": "嘻嘻2",
		        "time": "2015-12-22 16:22:15",
		        "id": 1
		      }
		    ]
		  },
		  "errMsg": "",
		  "innerErrMsg": ""
		}
		```
		"""
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']

		order = Order.from_id({
			'webapp_owner': webapp_owner,
			'webapp_user': webapp_user,
			'order_id': args['order_id']
			})
		express_details = order.express_details
		for detail in express_details:
			print(detail.id, detail.content, detail.status)

		data = [AExpressDetails.to_dict(detail) for detail in express_details]
		
		return {
			"express_company_name": order.readable_express_company_name,
			"express_number": order.express_number,
			"express_details": data
		}

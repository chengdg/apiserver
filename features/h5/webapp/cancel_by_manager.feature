# __author__ : "刘海鹏"
#editor 新新 2015.10.20

Feature: 后台取消订单,后台可获取订单状态,取消原因
"""

		bill可以获取订单状态为'已取消'
"""

Background:
	Given jobs登录系统
	And jobs已添加商品
		"""
		[{
			"name": "商品1",
			"model": {
				"models": {
					"standard": {
						"price": 9.9,
						"stock_type": "有限",
						"stocks": 3
					}
				}
			}

		}]
		"""
	And bill关注jobs的公众号

@mall2 @mall.manager_cancel_status
Scenario:1 取消订单后,手机端订单状态为'已取消'
	1.jobs取消订单,bill可以获取订单状态为'已取消'
	2.bill可获取'取消原因'

	Given jobs登录系统

	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"products": [{
				"name": "商品1",
				"count": 2
			}],
			"customer_message": "bill的订单备注1"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 19.8,
			"products": [{
				"name": "商品1",
				"count": 2
			}]
		}
		"""
	Given jobs登录系统
	Then jobs可以获得最新订单详情
		"""
		{
			"status": "待支付",
			"actions": ["取消订单", "支付", "修改价格"],
			"total_price": 19.8,
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"customer_message": "bill的订单备注1",
			"products": [{
				"name": "商品1",
				"count": 2,
				"total_price": 19.80
			}]
		}
		"""
	When jobs'取消'最新订单
	Then jobs可以获得最新订单详情
		"""
		{
			"status": "已取消",
			"actions": []
		}
		"""

	When bill访问jobs的webapp
	Then bill成功创建订单
		"""
		{
			"status": "已取消",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 19.8,
			"products": [{
				"name": "商品1",
				"count": 2
			}]
		}
		"""



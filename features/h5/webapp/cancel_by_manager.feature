# watcher: wangxinrui@weizoom.com,benchi@weizoom.com
#editor 新新 2015.10.20
#editor 新新 2015.11.26


Feature: 后台取消订单,后台可获取订单状态,取消原因
"""

		bill可以获取订单状态为'已取消'
"""

Background:
	Given 重置'weapp'的bdd环境
	Given jobs登录系统::weapp
	And jobs已添加商品::weapp
		"""
		[{
			"name": "商品1",
			"model": {
				"models": {
					"standard": {
						"price": 9.90,
						"stock_type": "有限",
						"stocks": 3
					}
				}
			}

		}]
		"""
	And jobs已添加支付方式::weapp
	"""
	[{
		"type": "货到付款"
	}, {
		"type": "微信支付"
	}]
	"""
	And bill关注jobs的公众号

@mall3 @mall.manager_cancel_status
Scenario:1 取消订单后,手机端订单状态为'已取消'
	1.jobs取消订单,bill可以获取订单状态为'已取消'
	2.bill可获取'取消原因'

	Given jobs登录系统::weapp

	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
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
			"final_price": 19.80,
			"products": [{
				"name": "商品1",
				"count": 2
			}]
		}
		"""
	Given jobs登录系统::weapp
	Then jobs可以获得最新订单详情::weapp
		"""
		{
			"status": "待支付",
			"actions": ["取消订单", "支付", "修改价格"],
			"final_price": 19.80,
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
	When jobs'取消'最新订单::weapp
	Then jobs可以获得最新订单详情::weapp
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
			"final_price": 19.80,
			"products": [{
				"name": "商品1",
				"count": 2
			}]
		}
		"""



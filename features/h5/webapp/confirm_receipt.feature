#author: 王丽 2016-01-05

Feature: 会员确认、支付、取消非本会员的订单

Background:
	Given 重置weapp的bdd环境
	When jobs已添加商品:weapp
		"""
		[{
			"name": "商品1",
			"postage":10,
			"price":100
		}, {
			"name": "商品2",
			"postage":15,
			"price":100
		}]
		"""
	And jobs已添加支付方式:weapp
		"""
		[{
			"type": "货到付款",
			"is_active": "启用"
		},{
			"type": "微信支付",
			"is_active": "启用"
		},{
			"type": "支付宝",
			"is_active": "启用"
		}]
		"""

	Given bill关注jobs的公众号
	Given tom关注jobs的公众号

@mall.webapp
Scenario:1 会员"取消"非本会员的订单
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"order_id": "001",
			"products": [{
				"name": "商品1",
				"count": 1
			}],
			"pay_type": "微信支付"
		}
		"""

	When tom访问jobs的webapp
	Then tom不能'取消'订单'001'

	When bill访问jobs的webapp
	And bill取消订单'001'
	Then bill手机端获取订单'001'
		"""
		{
			"order_no": "001",
			"status": "已取消"
		}
		"""

@mall.webapp
Scenario:2 会员"支付"非本会员的订单
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"order_id": "002",
			"products": [{
				"name": "商品1",
				"count": 1
			}],
			"pay_type": "微信支付"
		}
		"""

	When tom访问jobs的webapp
	Then tom不能使用支付方式'微信支付'进行支付订单'002'

	When bill访问jobs的webapp
	Then bill使用支付方式'微信支付'进行支付订单'002'
	Then bill手机端获取订单'002'
		"""
		{
			"order_no": "002",
			"status": "已支付"
		}
		"""

@mall.webapp
Scenario:3 会员"确认收货"非本会员的订单
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"order_id": "003",
			"products": [{
				"name": "商品1",
				"count": 1
			}],
			"pay_type": "微信支付"
		}
		"""
	And bill使用支付方式'微信支付'进行支付
	Given jobs登录系统:weapp
	When jobs对订单进行发货:weapp
		"""
		{
			"order_no": "003",
			"logistics": "off",
			"shipper": ""
		}
		"""

	When tom访问jobs的webapp
	And tom不能'确认收货'订单'003'

	When bill访问jobs的webapp
	And bill确认收货订单'003'
	Then bill手机端获取订单'003'
		"""
		{
			"order_no": "003",
			"status": "已完成"
		}
		"""

# __author__ : "冯雪静"

Feature: 禁止修改链接串账号
	"""
	1.修改本商户商品链接的商品ID，可以访问进行购买，成功下单
	2.把本商户的商品链接的商品ID修改成他商户的商品ID，访问链接提示'404页面'
	"""

Background:
	Given jobs登录系统
	And jobs已添加支付方式
		"""
		[{
			"type": "货到付款"
		}]
		"""
	And jobs已添加商品
		"""
		[{
			"name": "商品1",
			"price": 100.00
		},{
			"name": "商品2",
			"price": 90.00
		}]
		"""
	And bill关注jobs的公众号
	Given tom登录系统
	And jobs已添加支付方式
		"""
		[{
			"type": "货到付款"
		}]
		"""
	And tom已添加商品
		"""
		[{
			"name": "商品3",
			"price": 9.99
		}]
		"""
	And bill关注tom的公众号


@mall2
Scenario: 1 修改本商户商品ID，进行访问
	1. bill在webapp把jobs的商品1链接的商品ID修改成商品2的商品ID
	2. bill访问修改后的链接
	3. 进行购买，成功下单

	When bill访问jobs的webapp
	When bill把jobs的'商品1'链接的商品ID修改成'商品2'的商品ID
	When bill访问修改后的链接
	Then webapp页面标题为'商品2'
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品2",
				"count": 1
				}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 90.00,
			"products": [{
				"name": "商品2",
				"price": 90.00,
				"count": 1
			}]
		}
		"""
	Given jobs登录系统
	Then jobs可以获得最新订单详情
		"""
		{
			"status": "待支付",
			"actions": ["修改价格", "取消订单", "支付"],
			"final_price": 90.00,
			"products": [{
				"name": "商品2",
				"price": 90.00,
				"count": 1
			}]
		}
		"""


@mall2
Scenario: 2 修改其他商户商品ID，进行访问
	1. bill在webapp把jobs的商品1链接的商品ID修改成商品2的商品ID
	2. bill访问修改后的链接，获得错误提示信息'404页面'

	When bill访问jobs的webapp
	When bill把jobs的'商品1'链接的商品ID修改成tom的'商品3'的商品ID
	When bill访问修改后的链接
	Then bill获得错误提示'404页面'



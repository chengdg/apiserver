#_author_:王丽 2015-12-30

Feature:对有效订单进行统计
"""
	1 统计整个系统中的订单
	2 统计单个会员的数据
"""

Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp

	And jobs已添加支付方式:weapp
		"""
		[{
			"type": "微众卡支付"
		}, {
			"type": "货到付款"
		}, {
			"type": "微信支付"
		}]
		"""
	And jobs已添加商品:weapp
		"""
		[{
			"name": "商品1",
			"price": 100
		}, {
			"name": "商品2",
			"price": 200
		}]
		"""
	And bill关注jobs的公众号
	And tom关注jobs的公众号
	And nokia关注jobs的公众号
	And marry关注jobs的公众号

	#bill购买jobs的数据
	#待支付订单 001 100 
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"order_id": "001",
			"pay_type":"微信支付",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	#已取消订单 002 200
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"order_id": "002",
			"pay_type":"微信支付",
			"products": [{
				"name": "商品2",
				"count": 1
			}]
		}
		"""
	And bill取消订单'002'

	#待发货订单 003 100  ***
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"order_id": "003",
			"pay_type":"货到付款",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""

	#已发货订单 004 200  ***
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"order_id": "004",
			"pay_type":"货到付款",
			"products": [{
				"name": "商品2",
				"count": 1
			}]
		}
		"""
	And jobs对订单进行发货:weapp
		"""
		{
			"order_no":"004",
			"logistics":"顺丰速运",
			"number":"123456789"
		}
		"""

	#已完成订单 005 100  ***
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"order_id": "005",
			"pay_type":"货到付款",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	And jobs对订单进行发货:weapp
		"""
		{
			"order_no":"004",
			"logistics":"顺丰速运",
			"number":"123456789"
		}
		"""
	#And bill对订单'005'进行确认收货

	#tom购买待发货订单 006 200 ***
	When tom访问jobs的webapp
	And tom购买jobs的商品
		"""
		{
			"order_id": "006",
			"pay_type":"货到付款",
			"products": [{
				"name": "商品2",
				"count": 1
			}]
		}
		"""

	#nokia购买已发货订单 007 100  ***
	When nokia访问jobs的webapp
	And nokia购买jobs的商品
		"""
		{
			"order_id": "007",
			"pay_type":"货到付款",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	And jobs对订单进行发货:weapp
		"""
		{
			"order_no":"007",
			"logistics":"顺丰速运",
			"number":"123456789"
		}
		"""

	#marry购买已完成订单 008 200 ***
	When marry访问jobs的webapp
	And marry购买jobs的商品
		"""
		{
			"order_id": "008",
			"pay_type":"货到付款",
			"products": [{
				"name": "商品2",
				"count": 1
			}]
		}
		"""
	And jobs对订单进行发货:weapp
		"""
		{
			"order_no":"008",
			"logistics":"顺丰速运",
			"number":"123456789"
		}
		"""
	#And marry对订单'008'进行确认收货

@order @allOrder
Scenario:1 统计整个系统有订单的：消费金额、订单数、客单价
	When Given jobs登录系统:weapp

	Then jobs获得有效订单统计
		"""
		{
			"purchase_amount":900.00,
			"purchase_number":6,
			"customer_price":150.00
		}
		"""

@order @allOrder
Scenario:2 统计单个会员有订单的：消费金额、订单数、客单价
	When bill访问jobs的webapp

	Then bill获得有效订单统计
		"""
		{
			"purchase_amount":400.00,
			"purchase_number":3,
			"customer_price":133.33
		}
		"""


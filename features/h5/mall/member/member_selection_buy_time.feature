#_author_:王丽 2015-12-31

Feature:会员列表查询会员的最后购买时间weapp
"""
	【最后购买时间】：会员最后一个提交有效订单（订单状态为：待发货、已发货、已完成）的【付款时间】
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
			"pay_type":"微信支付",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	And bill使用支付方式'微信支付'进行支付于'2015-10-10 10:30:00'

	#已发货订单 004 200  ***
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"order_id": "004",
			"pay_type":"微信支付",
			"products": [{
				"name": "商品2",
				"count": 1
			}]
		}
		"""
	And bill使用支付方式'微信支付'进行支付于'2015-10-11 10:30:00'
	Given jobs登录系统:weapp
	When jobs对订单进行发货:weapp
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
	And bill使用支付方式'微信支付'进行支付于'2015-10-12 10:30:00'
	Given jobs登录系统:weapp
	When jobs对订单进行发货:weapp
		"""
		{
			"order_no":"004",
			"logistics":"顺丰速运",
			"number":"123456789"
		}
		"""
	And bill确认收货订单'005'

	#tom购买待发货订单 006 200 ***
	When tom访问jobs的webapp
	And tom购买jobs的商品
		"""
		{
			"order_id": "006",
			"pay_type":"支付宝",
			"products": [{
				"name": "商品2",
				"count": 1
			}]
		}
		"""
	And tom使用支付方式'支付宝'进行支付于'2015-10-10 10:30:00'

	#nokia购买已发货订单 007 100  ***
	When nokia访问jobs的webapp
	And nokia购买jobs的商品
		"""
		{
			"order_id": "007",
			"pay_type":"支付宝",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	And nokia使用支付方式'支付宝'进行支付于'2015-10-09 10:30:00'
	Given jobs登录系统:weapp
	When jobs对订单进行发货:weapp
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
			"pay_type":"支付宝",
			"products": [{
				"name": "商品2",
				"count": 1
			}]
		}
		"""
	And bill使用支付方式'支付宝'进行支付于'2015-10-08 10:30:00'
	Given jobs登录系统:weapp
	When jobs对订单进行发货:weapp
		"""
		{
			"order_no":"008",
			"logistics":"顺丰速运",
			"number":"123456789"
		}
		"""
	And marry确认收货订单'008'

@member @memberList
Scenario:1 按照会员的"最后购买时间"进行查询
	Given jobs登录系统:weapp

	#区间时间边界值查询，包含结束时间
		When jobs设置会员查询条件:weapp
			"""
			[{
				"status":"全部",
				"last_buy_start_time":"2015-10-09 10:30:00",
				"last_buy_end_time":"2015-10-10 10:30:00"
			}]
			"""
		Then jobs获得刷选结果人数:weapp
			"""
			[{
				"result_quantity":2
			}]
			"""
		Then jobs可以获得会员列表:weapp
			| name  | pay_money | unit_price | pay_times |
			| tom   |   200.00  |   200.00   |     1     |
			| nokia |   100.00  |   100.00   |     1     |

	#区间时间边界值查询，开始时间等于结束时间
		When jobs设置会员查询条件:weapp
			"""
			[{
				"status":"全部",
				"last_buy_start_time":"2015-10-12 10:30:00",
				"last_buy_end_time":"2015-10-12 10:30:00"
			}]
			"""
		Then jobs获得刷选结果人数:weapp
			"""
			[{
				"result_quantity":3
			}]
			"""
		Then jobs可以获得会员列表:weapp
			| name  | pay_money | unit_price | pay_times |
			| bill  |   400.00  |   133.33   |     3     |

	#无查询结果
		When jobs设置会员查询条件:weapp
			"""
			[{
				"status":"全部",
				"last_buy_start_time":"今天",
				"last_buy_end_time":"今天"
			}]
			"""
		Then jobs获得刷选结果人数:weapp
			"""
			[{
				"result_quantity":0
			}]
			"""
		Then jobs可以获得会员列表:weapp
			"""
			[]
			"""

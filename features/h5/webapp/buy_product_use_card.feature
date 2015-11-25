#editor: benchi
#editor: 师帅 2015.10.20

Feature:使用微众卡购买商品
	用户能通过webapp使用微众卡购买jobs的商品
	feathure里要加一个  "weizoom_card_money":50.00,的字段

Background:
	Given jobs登录系统
	And jobs已有微众卡支付权限
	And jobs已添加支付方式
		"""
		[{
			"type":"货到付款"
		},{
			"type":"微信支付"
		},{
			"type":"支付宝"
		},{
			"type":"微众卡支付"
		}]
		"""
	And jobs已添加商品
		"""
		[{
			"name": "商品1",
			"price": 50
		}]
		"""
	And jobs已创建微众卡
		"""
		{
			"cards":[{
				"id":"0000001",
				"password":"1234567",
				"status":"未使用",
				"price":100.00
			},{
				"id":"0000002",
				"password":"1234567",
				"status":"已使用",
				"price":50.00
			},{
				"id":"0000003",
				"password":"1231231",
				"status":"未使用",
				"price":30.00
			},{
				"id":"0000004",
				"password":"1231231",
				"status":"已用完",
				"price":0.00
			},{
				"id":"0000005",
				"password":"1231231",
				"status":"未激活",
				"price":30.00
			},{
				"id":"0000006",
				"password":"1231231",
				"status":"已过期",
				"price":30.00
			}]
		}
		"""
	And bill关注jobs的公众号

@mall2 @mall.pay_weizoom_card
Scenario:1 微众卡金额大于订单金额时进行支付
	bill用微众卡购买jobs的商品时,微众卡金额大于订单金额
	1.自动扣除微众卡金额
	2.创建订单成功，订单状态为“等待发货”，支付方式为“微众卡支付”
	3.微众卡金额减少,状态为“已使用”

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products":[{
				"name":"商品1",
				"price":50,
				"count":1
			}],
			"weizoom_card":[{
				"card_name":"0000001",
				"card_pass":"1234567"
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待发货",
			"final_price": 0.0,
			"product_price": 50.0,
			"weizoom_card_money":50.00,
			"products":[{
				"name":"商品1",
				"price":50.00,
				"count":1
			}]
		}
		"""
	Given jobs登录系统
	Then jobs能获取微众卡'0000001'
		"""
		{
			"status":"已使用",
			"price":50.00
		}
		"""

@mall2 @mall.pay_weizoom_card
Scenario:2 微众卡金额等于订单金额时进行支付
	bill用微众卡购买jobs的商品时,微众卡金额等于订单金额
	1.自动扣除微众卡金额
	2.创建订单成功，订单状态为“等待发货”，支付方式为“微众卡支付”
	3.微众卡金额减少,状态为“已用完”

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products":[{
				"name":"商品1",
				"price":50,
				"count":1
			}],
			"weizoom_card":[{
				"card_name":"0000002",
				"card_pass":"1234567"
			}]
		}
		"""

	Then bill成功创建订单
		"""
		{
			"status": "待发货",
			"final_price": 0.0,
			"product_price": 50.0,
			"weizoom_card_money":50.00,
			"products":[{
				"name":"商品1",
				"price":50.00,
				"count":1
			}]
		}
		"""
	Given jobs登录系统
	Then jobs能获取微众卡'0000002'
		"""
		{
			"status":"已用完",
			"price":0.00
		}
		"""

@mall2 @mall.pay_weizoom_card
Scenario:3 微众卡金额小于订单金额时进行支付
	bill用微众卡购买jobs的商品时,微众卡金额小于订单金额
	1.创建订单成功，订单状态为“等待支付”
	2.微众卡金额不变,状态为“未使用”

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products":[{
				"name":"商品1",
				"price":50,
				"count":1
			}],
			"weizoom_card":[{
				"card_name":"0000003",
				"card_pass":"1231231"
			}]
		}
		"""

	#bill获得创建订单失败的信息'您的微众卡余额不足！'
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 20.0,
			"product_price": 50.0,
			"weizoom_card_money":30.00,
			"products":[{
				"name":"商品1",
				"price":50.00,
				"count":1
			}]
		}
		"""
	Given jobs登录系统
	Then jobs能获取微众卡'0000003'
		"""
		{
			"status":"已用完",
			"price":0.00
		}
		"""

@mall2 @mall.pay_weizoom_card
Scenario:4 用微众卡购买商品时，输入错误的卡号密码
	bill用微众卡购买jobs的商品时,输入错误的卡号密码
	1.创建订单成功，订单状态为“等待支付”
	2.微众卡金额不变,状态为“未使用”

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products":[{
				"name":"商品1",
				"price":50,
				"count":1
			}],
			"weizoom_card":[{
				"card_name":"0000001",
				"card_pass":"1231231"
			}]
		}
		"""

	Then bill获得创建订单失败的信息'卡号或密码错误'

	When bill购买jobs的商品
		"""
		{
			"products":[{
				"name":"商品1",
				"price":50,
				"count":1
			}]
		}
		"""

	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 50.0,
			"product_price": 50.0,
			"products":[{
				"name":"商品1",
				"price":50.00,
				"count":1
			}]
		}
		"""
	Given jobs登录系统
	Then jobs能获取微众卡'0000001'
		"""
		{
			"status":"未使用",
			"price":100.00
		}
		"""

@mall2 @mall.pay_weizoom_card
Scenario:5 用已用完的微众卡购买商品时
	bill用已用完的微众卡购买jobs的商品时
	1.创建订单成功，订单状态为“等待支付”
	2.微众卡金额不变,状态为“已用完”

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products":[{
				"name":"商品1",
				"price":50,
				"count":1
			}],
			"weizoom_card":[{
				"card_name":"0000003",
				"card_pass":"1231231"
			}]
		}
		"""

	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 20.0,
			"product_price": 50.0,
			"products":[{
				"name":"商品1",
				"price":50.00,
				"count":1
			}]
		}
		"""
	Given jobs登录系统
	Then jobs能获取微众卡'0000003'
		"""
		{
			"status":"已用完",
			"price":0.00
		}
		"""

@mall2 @mall.pay_weizoom_card
Scenario:6 用未激活的微众卡购买商品时
	bill用未激活的微众卡购买jobs的商品时
	1.创建订单失败，提示"微众卡未激活"
	2.微众卡金额不变,状态为“未激活”

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products":[{
				"name":"商品1",
				"price":50,
				"count":1
			}],
			"weizoom_card":[{
				"card_name":"0000005",
				"card_pass":"1231231"
			}]
		}
		"""
	Then bill获得创建订单失败的信息'微众卡未激活'

	When bill购买jobs的商品
		"""
		{
			"products":[{
				"name":"商品1",
				"price":50,
				"count":1
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 50.0,
			"product_price": 50.0,
			"products":[{
				"name":"商品1",
				"price":50.00,
				"count":1
			}]
		}
		"""
	Given jobs登录系统
	Then jobs能获取微众卡'0000005'
		"""
		{
			"status":"未激活",
			"price":30.00
		}
		"""

@mall2 @mall.pay_weizoom_card
Scenario:7 用已过期的微众卡购买商品时
	bill用已用过期的微众卡购买jobs的商品时
	1.提示"微众卡已过期"
	2.微众卡金额不变,状态为“已过期”

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products":[{
				"name":"商品1",
				"price":50,
				"count":1
			}],
			"weizoom_card":[{
				"card_name":"0000006",
				"card_pass":"1231231"
			}]
		}
		"""

	Then bill获得创建订单失败的信息'微众卡已过期'
	When bill购买jobs的商品
		"""
		{
			"products":[{
				"name":"商品1",
				"price":50,
				"count":1
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 50.0,
			"product_price": 50.0,
			"products":[{
				"name":"商品1",
				"price":50.00,
				"count":1
			}]
		}
		"""
	Given jobs登录系统
	Then jobs能获取微众卡'0000006'
		"""
		{
			"status":"已过期",
			"price":30.00
		}
		"""

@mall2 @mall.pay_weizoom_card
Scenario:8 用已使用过的微众卡购买商品时
	1.创建订单成功，订单状态为“待发货”
	2.扣除微众卡金额,状态为“已用完”

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products":[{
				"name":"商品1",
				"price":50,
				"count":1
			}],
			"weizoom_card":[{
				"card_name":"0000002",
				"card_pass":"1234567"
			}]
		}
		"""

	Then bill成功创建订单
		"""
		{
			"status": "待发货",
			"final_price": 0.0,
			"product_price": 50.0,
			"weizoom_card_money":50.00,
			"products":[{
				"name":"商品1",
				"price":50.00,
				"count":1
			}]
		}
		"""
	Given jobs登录系统
	Then jobs能获取微众卡'0000002'
		"""
		{
			"status":"已用完",
			"price":0.00
		}
		"""

@mall2 @mall.pay_weizoom_card
Scenario:9 用10张微众卡共同支付
	1.创建订单成功，订单状态为“待支付”
	2.扣除微众卡金额,状态为“已用完”
	Given jobs登录系统
	And jobs已创建微众卡
		"""
		{
			"cards":[{
				"id":"1000001",
				"password":"1234567",
				"status":"未使用",
				"price":1.00
			},{
				"id":"1000002",
				"password":"1234567",
				"status":"已使用",
				"price":1.00
			},{
				"id":"1000003",
				"password":"1234567",
				"status":"未使用",
				"price":1.00
			},{
				"id":"1000004",
				"password":"1234567",
				"status":"未使用",
				"price":1.00
			},{
				"id":"1000005",
				"password":"1234567",
				"status":"已使用",
				"price":1.00
			},{
				"id":"1000006",
				"password":"1234567",
				"status":"已使用",
				"price":1.00
			},{
				"id":"1000007",
				"password":"1234567",
				"status":"未使用",
				"price":1.00
			},{
				"id":"1000008",
				"password":"1234567",
				"status":"未使用",
				"price":1.00
			},{
				"id":"1000009",
				"password":"1234567",
				"status":"已使用",
				"price":1.00
			},{
				"id":"1000010",
				"password":"1234567",
				"status":"已使用",
				"price":1.00
			},{
				"id":"1000011",
				"password":"1234567",
				"status":"已使用",
				"price":1.00
			}]
		}
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products":[{
				"name":"商品1",
				"price":50,
				"count":1
			}],
			"weizoom_card":[{
				"card_name":"1000001",
				"card_pass":"1234567"
			},{
				"card_name":"1000002",
				"card_pass":"1234567"
			},{
				"card_name":"1000003",
				"card_pass":"1234567"
			},{
				"card_name":"1000004",
				"card_pass":"1234567"
			},{
				"card_name":"1000005",
				"card_pass":"1234567"
			},{
				"card_name":"1000006",
				"card_pass":"1234567"
			},{
				"card_name":"1000007",
				"card_pass":"1234567"
			},{
				"card_name":"1000008",
				"card_pass":"1234567"
			},{
				"card_name":"1000009",
				"card_pass":"1234567"
			},{
				"card_name":"1000010",
				"card_pass":"1234567"
			}]
		}
		"""

	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 40.0,
			"product_price": 50.0,
			"weizoom_card_money":10.00,
			"products":[{
				"name":"商品1",
				"price":50.00,
				"count":1
			}]
		}
		"""
	Given jobs登录系统
	Then jobs能获取微众卡
		"""
		[{
			"id":"1000001",
			"password":"1234567",
			"status":"已用完",
			"price":0.00
		},{
			"id":"1000002",
			"password":"1234567",
			"status":"已用完",
			"price":0.00
		},{
			"id":"1000003",
			"password":"1234567",
			"status":"已用完",
			"price":0.00
		},{
			"id":"1000004",
			"password":"1234567",
			"status":"已用完",
			"price":0.00
		},{
			"id":"1000005",
			"password":"1234567",
			"status":"已用完",
			"price":0.00
		},{
			"id":"1000006",
			"password":"1234567",
			"status":"已用完",
			"price":0.00
		},{
			"id":"1000007",
			"password":"1234567",
			"status":"已用完",
			"price":0.00
		},{
			"id":"1000008",
			"password":"1234567",
			"status":"已用完",
			"price":0.00
		},{
			"id":"1000009",
			"password":"1234567",
			"status":"已用完",
			"price":0.00
		},{
			"id":"1000010",
			"password":"1234567",
			"status":"已用完",
			"price":0.00
		},{
			"id":"1000011",
			"password":"1234567",
			"status":"已使用",
			"price":1.00
		}]
		"""

@mall2 @mall.pay_weizoom_card
Scenario:10 用11张微众卡共同支付
	1.创建订单失败错误提示：只能使用10张微众卡
	2.微众卡金额,状态不变
	Given jobs登录系统
	And jobs已创建微众卡
		"""
		{
			"cards":[{
				"id":"1000001",
				"password":"1234567",
				"status":"已使用",
				"price":1.00
			},{
				"id":"1000002",
				"password":"1234567",
				"status":"已使用",
				"price":1.00
			},{
				"id":"1000003",
				"password":"1234567",
				"status":"未使用",
				"price":1.00
			},{
				"id":"1000004",
				"password":"1234567",
				"status":"未使用",
				"price":1.00
			},{
				"id":"1000005",
				"password":"1234567",
				"status":"已使用",
				"price":1.00
			},{
				"id":"1000006",
				"password":"1234567",
				"status":"已使用",
				"price":1.00
			},{
				"id":"1000007",
				"password":"1234567",
				"status":"未使用",
				"price":1.00
			},{
				"id":"1000008",
				"password":"1234567",
				"status":"未使用",
				"price":1.00
			},{
				"id":"1000009",
				"password":"1234567",
				"status":"已使用",
				"price":1.00
			},{
				"id":"1000010",
				"password":"1234567",
				"status":"已使用",
				"price":1.00
			},{
				"id":"1000011",
				"password":"1234567",
				"status":"已使用",
				"price":1.00
			}]
		}
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products":[{
				"name":"商品1",
				"price":50,
				"count":1
			}],
			"weizoom_card":[{
				"card_name":"1000001",
				"card_pass":"1234567"
			},{
				"card_name":"1000002",
				"card_pass":"1234567"
			},{
				"card_name":"1000003",
				"card_pass":"1234567"
			},{
				"card_name":"1000004",
				"card_pass":"1234567"
			},{
				"card_name":"1000005",
				"card_pass":"1234567"
			},{
				"card_name":"1000006",
				"card_pass":"1234567"
			},{
				"card_name":"1000007",
				"card_pass":"1234567"
			},{
				"card_name":"1000008",
				"card_pass":"1234567"
			},{
				"card_name":"1000009",
				"card_pass":"1234567"
			},{
				"card_name":"1000010",
				"card_pass":"1234567"
			},{
				"card_name":"1000011",
				"card_pass":"1234567"
			}]
		}
		"""

	Then bill获得创建订单失败的信息'微众卡只能使用十张'
	Given jobs登录系统
	Then jobs能获取微众卡
		"""
		[{
			"id":"1000001",
			"password":"1234567",
			"status":"已使用",
			"price":1.00
		},{
			"id":"1000002",
			"password":"1234567",
			"status":"已使用",
			"price":1.00
		},{
			"id":"1000003",
			"password":"1234567",
			"status":"未使用",
			"price":1.00
		},{
			"id":"1000004",
			"password":"1234567",
			"status":"未使用",
			"price":1.00
		},{
			"id":"1000005",
			"password":"1234567",
			"status":"已使用",
			"price":1.00
		},{
			"id":"1000006",
			"password":"1234567",
			"status":"已使用",
			"price":1.00
		},{
			"id":"1000007",
			"password":"1234567",
			"status":"未使用",
			"price":1.00
		},{
			"id":"1000008",
			"password":"1234567",
			"status":"未使用",
			"price":1.00
		},{
			"id":"1000009",
			"password":"1234567",
			"status":"已使用",
			"price":1.00
		},{
			"id":"1000010",
			"password":"1234567",
			"status":"已使用",
			"price":1.00
		},{
			"id":"1000011",
			"password":"1234567",
			"status":"已使用",
			"price":1.00
		}]
		"""

@mall2 @mall.pay_weizoom_card
Scenario:11 用微众卡购买商品时，输入两张同样的卡号密码
	bill用微众卡购买jobs的商品时,输入错误的卡号密码
	1.创建订单失败，错误提示"该微众卡已经添加"
	2.微众卡金额,状态不变

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products":[{
				"name":"商品1",
				"price":50,
				"count":1
			}],
			"weizoom_card":[{
				"card_name":"0000001",
				"card_pass":"1234567"
			},{
				"card_name":"0000001",
				"card_pass":"1234567"
			}]
		}
		"""

	Then bill获得创建订单失败的信息'该微众卡已经添加'


	Given jobs登录系统
	Then jobs能获取微众卡'0000001'
		"""
		{
			"status":"未使用",
			"price":100.00
		}
		"""

@mall2 @mall @mall.pay_weizoom_card
Scenario:12 用已用完的微众卡购买商品时
	bill用已用完的微众卡购买jobs的商品时
	1.创建订单成功，订单状态为“等待支付”
	2.微众卡金额不变,状态为“已用完”

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products":[{
				"name":"商品1",
				"price":50,
				"count":1
			}],
			"weizoom_card":[{
				"card_name":"0000004",
				"card_pass":"1231231"
			}]
		}
		"""

	Then bill成功创建订单
	"""
	{
		"status": "待支付",
		"final_price": 50.0,
		"product_price": 50.0,
		"products":[{
			"name":"商品1",
			"price":50.00,
			"count":1
		}]
	}
	"""
	Given jobs登录系统
	Then jobs能获取微众卡'0000004'
	"""
	{
		"status":"已用完",
		"price":0.00
	}
	"""

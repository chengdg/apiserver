# watcher: zhangsanxiang@weizoom.com,benchi@weizoom.com
#_author_:张三香 2015.01.12

Feature:校验手机端支付结果页面

Background:
	Given 重置'weapp'的bdd环境
	Given 重置'weizoom_card'的bdd环境
	Given jobs登录系统::weapp
	And jobs已有微众卡支付权限::weapp
	And jobs已添加支付方式::weapp
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

	#创建微众卡
	Given test登录管理系统::weizoom_card
	When test新建通用卡::weizoom_card
		"""
		[{
			"name":"100元微众卡",
			"prefix_value":"100",
			"type":"virtual",
			"money":"100.00",
			"num":"2",
			"comments":"微众卡"
		},{
			"name":"50元微众卡",
			"prefix_value":"050",
			"type":"virtual",
			"money":"50.00",
			"num":"1",
			"comments":"微众卡"
		}]
		"""

	#微众卡审批出库
	When test下订单::weizoom_card
			"""
			[{
				"card_info":[{
					"name":"100元微众卡",
					"order_num":"2",
					"start_date":"2016-04-07 00:00",
					"end_date":"2019-10-07 00:00"
				},{
					"name":"50元微众卡",
					"order_num":"1",
					"start_date":"2016-04-07 00:00",
					"end_date":"2019-10-07 00:00"
				}],
				"order_info":{
					"order_id":"0001"
				}
			}]
			"""
	And test批量激活订单'0001'的卡::weizoom_card

	And jobs已添加商品::weapp
		"""
		[{
			"name": "商品1",
			"price": 100.00
		}]
		"""

	And bill关注jobs的公众号

@mall3 @ztq
Scenario:1 支付结果页面支付方式为'微信支付'
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id": "001",
			"pay_type": "微信支付",
			"products":[{
				"name":"商品1",
				"price":100.00,
				"count":1
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 100.00,
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1
			}]
		}
		"""
	When bill使用支付方式'微信支付'进行支付
		"""
		{
			"is_sync": true
		}
		"""

	Then bill获得订单支付结果
		"""
		{
			"order_id":"001",
			"final_price":100.00,
			"pay_type": "微信支付"
		}
		"""


	Then bill支付订单成功
		"""
		{
			"status": "待发货",
			"final_price": 100.00,
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1
			}]
		}
		"""

@mall3 @ztq
Scenario:2 支付结果页面支付方式为'支付宝'
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"001",
			"pay_type": "支付宝",
			"products":[{
				"name":"商品1",
				"price":100.00,
				"count":1
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 100.00,
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1
			}]
		}
		"""
	When bill使用支付方式'支付宝'进行支付
	Then bill获得订单支付结果
		"""
		{
			"order_id":"001",
			"final_price":100.00,
			"pay_type": "支付宝"
		}
		"""
	Then bill支付订单成功
		"""
		{
			"status": "待发货",
			"final_price": 100.00,
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1
			}]
		}
		"""

@mall3 @ztq
Scenario:3 支付结果页面支付方式为'货到付款'
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id": "001",
			"pay_type": "货到付款",
			"products":[{
				"name":"商品1",
				"price":100.00,
				"count":1
			}]
		}
		"""
	Then bill获得订单支付结果
		"""
		{
			"order_id":"001",
			"final_price":100.00,
			"pay_type": "货到付款"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待发货",
			"final_price": 100.00,
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1
			}]
		}
		"""

@mall3 @ztq
Scenario:4 支付结果页面支付方式为'优惠抵扣'，使用优惠券支付
	#bill选择'支付宝'支付方式，单品券抵扣全部

	Given jobs登录系统::weapp
	Given jobs已添加了优惠券规则::weapp
		"""
		[{
			"name": "优惠券1",
			"money": 100.00,
			"start_date": "今天",
			"end_date": "1天后",
			"coupon_id_prefix": "coupon1_id_",
			"coupon_product": "商品1"
		}]
		"""
	When bill领取jobs的优惠券::weapp
		"""
		[{
			"name": "优惠券1",
			"coupon_ids": ["coupon1_id_1"]
		}]
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"001",
			"pay_type": "支付宝",
			"products":[{
				"name":"商品1",
				"price":100.00,
				"count":1
			}],
			"coupon": "coupon1_id_1"
		}
		"""
	Then bill获得订单支付结果
		"""
		{
			"order_id":"001",
			"final_price":0.00,
			"pay_type": "优惠抵扣"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待发货",
			"final_price": 0.00,
			"product_price": 100.00,
			"coupon_money": 100.00,
			"products":[{
				"name":"商品1",
				"price":100.00,
				"count":1
			}]
		}
		"""

@mall3 @ztq
Scenario:5 支付结果页面支付方式为'优惠抵扣'，使用整单积分抵扣
	#bill选择'货到付款'支付方式，整单积分抵扣全部

	Given jobs登录系统::weapp
	Given jobs设定会员积分策略::weapp
		"""
		{
			"integral_each_yuan": 2,
			"use_ceiling": 100
		}
		"""
	When bill访问jobs的webapp
	When bill获得jobs的200会员积分
	When bill购买jobs的商品
		"""
		{
			"order_id":"001",
			"pay_type": "货到付款",
			"integral": 200,
			"integral_money": 100.00,
			"products":[{
				"name":"商品1",
				"price":100.00,
				"count":1
			}]
		}
		"""
	Then bill获得订单支付结果
		"""
		{
			"order_id":"001",
			"final_price":0.00,
			"pay_type": "优惠抵扣"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待发货",
			"final_price": 0.00,
			"product_price": 100.00,
			"integral_money":100.00,
			"products":[{
				"name":"商品1",
				"price":100.00,
				"count":1
			}]
		}
		"""

@mall3 @ztq @weizoom_card
Scenario:6 支付结果页面支付方式为'优惠抵扣'，使用微众卡支付
	#bill选择'微信支付'支付方式，使用微众卡抵扣全部

	When bill访问jobs的webapp
	When bill绑定微众卡
		"""
		{
			"binding_date":"2016-06-16",
			"binding_shop":"jobs",
			"weizoom_card_info":
				{
					"id":"100000001",
					"password":"1234567"
				}
		}
		"""
	When bill购买jobs的商品
		"""
		{
			"order_id":"001",
			"pay_type": "微信支付",
			"products":[{
				"name":"商品1",
				"price":100.00,
				"count":1
			}],
			"weizoom_card":[{
				"card_name":"100000001",
				"card_pass":"1234567"
			}]
		}
		"""
	Then bill获得订单支付结果
		"""
		{
			"order_id":"001",
			"final_price":0.00,
			"pay_type": "优惠抵扣"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待发货",
			"final_price": 0.00,
			"product_price": 100.00,
			"weizoom_card_money":100.00,
			"products":[{
				"name":"商品1",
				"price":100.00,
				"count":1
			}]
		}
		"""

@mall3 @ztq
Scenario:7 支付结果页面支付方式为'优惠抵扣'，使用微众卡和优惠券支付
	#bill选择'微信支付'支付方式，使用微众卡和全体券抵扣全部

	Given jobs登录系统::weapp
	Given jobs已添加了优惠券规则::weapp
		"""
		[{
			"name": "优惠券1",
			"money": 50.00,
			"start_date": "今天",
			"end_date": "1天后",
			"coupon_id_prefix": "coupon1_id_"
		}]
		"""
	When bill领取jobs的优惠券::weapp
		"""
		[{
			"name": "优惠券1",
			"coupon_ids": ["coupon1_id_1"]
		}]
		"""
	When bill访问jobs的webapp
	When bill绑定微众卡
	"""
	{
		"binding_date":"2016-06-16",
		"binding_shop":"jobs",
		"weizoom_card_info":
			{
				"id":"050000001",
				"password":"1234567"
			}
	}
	"""
	When bill购买jobs的商品
		"""
		{
			"order_id":"001",
			"pay_type": "微信支付",
			"products":[{
				"name":"商品1",
				"price":100.00,
				"count":1
			}],
			"weizoom_card":[{
				"card_name":"050000001",
				"card_pass":"1234567"
			}],
			"coupon": "coupon1_id_1"
		}
		"""
	Then bill获得订单支付结果
		"""
		{
			"order_id":"001",
			"final_price":0.00,
			"pay_type": "优惠抵扣"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待发货",
			"final_price": 0.00,
			"product_price": 100.00,
			"weizoom_card_money":50.00,
			"coupon_money": 50.00,
			"products":[{
				"name":"商品1",
				"price":100.00,
				"count":1
			}]
		}
		"""

@mall3 @ztq
Scenario:8 支付结果页面支付方式为'优惠抵扣'，使用微众卡和积分支付
	#bill选择'微信支付'支付方式，使用微众卡和单品积分抵扣全部

	Given jobs登录系统::weapp
	Given jobs设定会员积分策略::weapp
		"""
		{
			"integral_each_yuan": 2
		}
		"""
	When jobs创建积分应用活动::weapp
		"""
		[{
			"name": "商品1积分应用",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品1",
			"is_permanant_active": false,
			"rules": [{
				"member_grade": "全部",
				"discount": 50,
				"discount_money": 50.00
			}]
		}]
		"""
	When bill访问jobs的webapp
	When bill获得jobs的200会员积分
	When bill绑定微众卡
	"""
	{
		"binding_date":"2016-06-16",
		"binding_shop":"jobs",
		"weizoom_card_info":
			{
				"id":"100000002",
				"password":"1234567"
			}
	}
	"""
	When bill购买jobs的商品
		"""
		{
			"order_id":"001",
			"pay_type": "微信支付",
			"products":[{
				"name":"商品1",
				"price":100.00,
				"count":1,
				"integral": 100,
				"integral_money": 50.00
			}],
			"weizoom_card":[{
				"card_name":"100000002",
				"card_pass":"1234567"
			}]
		}
		"""
	Then bill获得订单支付结果
		"""
		{
			"order_id":"001",
			"final_price":0.00,
			"pay_type": "优惠抵扣"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待发货",
			"final_price": 0.00,
			"product_price": 100.00,
			"weizoom_card_money":50.00,
			"integral_money":50.00,
			"products":[{
				"name":"商品1",
				"price":100.00,
				"count":1
			}]
		}
		"""


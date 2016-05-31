Feature:使用新微众卡购买商品
"""
涉及微众卡下单的demo
"""

Background:
	Given 重置weapp的bdd环境
	Given 重置weizoom_card的bdd环境
	Given jobs登录系统:weapp
	And jobs已有微众卡支付权限:weapp
	And jobs已添加支付方式:weapp
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
	And jobs已添加商品:weapp
		"""
		[{
			"name": "商品1",
			"price": 50.00
		}]
		"""

	#创建微众卡
	Given test登录管理系统:weizoom_card
	When test新建通用卡:weizoom_card
		"""
		[{
			"name":"微众卡",
			"prefix_value":"888",
			"type":"virtual",
			"money":"10.00",
			"num":"2",
			"comments":"微众卡"
		}]
		"""

	#微众卡审批出库
		When test下订单:weizoom_card
			"""
			[{
				"card_info":[{
					"name":"微众卡",
					"order_num":"2",
					"start_date":"2016-04-07 00:00",
					"end_date":"2019-10-07 00:00"
				}],
				"order_info":{
					"order_id":"0001",
					"order_attribute":"发售卡",
					"company":"窝夫小子",
					"responsible_person":"研发",
					"contact":"025-6623558",
					"sale_name":"姜晓明",
					"sale_deparment":"销售",
					"discount_way":{
						"way":"减免支付",
						"relief_money":"5.00"
					},		
					"invoice_limit"	:{
						"is_limit":"on",
						"invoice_title":"南京纳容网络技术有限公司",
						"invoice_content":"报销"
					},	
					"comments":""
					}		
				}]
				"""
		And test批量激活订单'0001'的卡:weizoom_card
#		Then test能获得'微众卡'订单详情列表:weizoom_card
#			"""
#			[{
#				"card_num":"888000001",
#				"money":"10.00"
#			}]
#			"""

	Given bill关注jobs的公众号


Scenario:1 微众卡金额大于订单金额时进行支付
	bill用微众卡购买jobs的商品时,微众卡金额大于订单金额
	1.自动扣除微众卡金额
	2.创建订单成功，订单状态为“等待发货”，支付方式为“微众卡支付”
	3.微众卡金额减少,状态为“已使用”

	Given jobs登录系统:weapp
#	Then jobs能获取微众卡'888000001':weapp
#		"""
#		{
#			"status":"未使用",
#			"price":10.00
#		}
#		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"pay_type": "货到付款",
			"products":[{
				"name":"商品1",
				"price":50.00,
				"count":1
			}],
			"weizoom_card":[{
				"card_name":"888000001",
				"card_pass":"1234567"
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待发货",
			"final_price": 40.00,
			"product_price": 50.00,
			"weizoom_card_money":10.00,
			"products":[{
				"name":"商品1",
				"price":50.00,
				"count":1
			}]
		}
		"""

	When bill进行微众卡余额查询
	"""
	{
		"id":"888000001",
		"password":"1234567"
	}
	"""
	Then bill获得微众卡余额查询结果
	"""
	{
		"card_remaining":0.00
	}
	"""



#	Given jobs登录系统:weapp
#	Then jobs能获取微众卡'888000001':weapp
#		"""
#		{
#			"status":"已用完",
#			"price":0.00
#		}
#		"""
# watcher: fengxuejing@weizoom.com,benchi@weizoom.com
# __author__ : "冯雪静"

Feature: 自营平台团购订单同步到商家
	"""
	商家提交商品到自营平台创建团购-团购成功订单同步到商家
		1.在自营平台的团购订单未成功，订单不会同步到商家
		2.在自营平台的团购订单失败，订单不会同步到商家
		3.在自营平台的团购订单成功，同步到商家，团购的icon不显示，订单金额是商品的采购价
	"""

#特殊说明：jobs表示自营平台,bill表示商家
Background:
	#商家bill的商品信息
	Given 重置weapp的bdd环境
	Given bill登录系统:weapp
	Given 添加bill店铺名称为'bill商家':weapp
	When bill已添加支付方式:weapp
		"""
		[{
			"type": "微信支付",
			"is_active": "启用"
		}, {
			"type": "支付宝",
			"is_active": "启用"
		}, {
			"type": "货到付款",
			"is_active": "启用"
		}]





		"""
	And bill添加邮费配置:weapp
		"""
		[{
			"name":"顺丰",
			"first_weight":1,
			"first_weight_price":15.00,
			"added_weight":1,
			"added_weight_price":5.00
		}]
		"""
	And bill选择'顺丰'运费配置:weapp
	And bill已添加商品:weapp
		"""
		[{
			"name": "bill无规格商品1",
			"created_at": "2015-07-02 10:20",
			"model": {
				"models": {
					"standard": {
						"price": 11.12,
						"user_code":"1112",
						"weight": 5.0,
						"stock_type": "无限"
					}
				}
			},
			"postage": 2.00
		},{
			"name": "bill无规格商品2",
			"created_at": "2015-07-03 10:20",
			"model": {
				"models": {
					"standard": {
						"price": 22.12,
						"user_code":"2212",
						"weight":1.0,
						"stock_type": "无限"
					}
				}
			},
			"postage": "顺丰"
		}]
		"""
	#自营平台jobs登录
	Given 设置jobs为自营平台账号:weapp
	Given jobs登录系统:weapp
	When jobs添加微信证书:weapp
	When jobs已添加支付方式:weapp
		"""
		[{
			"type": "微信支付",
			"is_active": "启用"
		}, {
			"type": "支付宝",
			"is_active": "启用"
		}, {
			"type": "货到付款",
			"is_active": "启用"
		}]
		"""
	And jobs添加邮费配置:weapp
		"""
		[{
			"name":"顺丰",
			"first_weight":1,
			"first_weight_price":15.00,
			"added_weight":1,
			"added_weight_price":5.00
		}]
		"""
	And jobs选择'顺丰'运费配置:weapp
	And jobs将商品池商品批量放入待售于'2015-08-02 12:30':weapp
		"""
		[
			"bill无规格商品2",
			"bill无规格商品1"
		]
		"""
	When jobs更新商品'bill无规格商品2':weapp
		"""
		{
			"name": "bill无规格商品2",
			"supplier":"bill商家",
			"purchase_price": 9.00,
			"model": {
				"models": {
					"standard": {
						"price": 222.12,
						"user_code":"2212",
						"weight":1.0,
						"stock_type": "无限"
					}
				}
			},
			"postage": 10.00
		}
		"""
	When jobs更新商品'bill无规格商品1':weapp
		"""
		{
			"name": "bill无规格商品1",
			"supplier":"bill商家",
			"purchase_price": 9.00,
			"model": {
				"models": {
					"standard": {
						"price": 122.12,
						"user_code":"2212",
						"weight":1.0,
						"stock_type": "无限"
					}
				}
			},
			"postage": "顺丰"
		}
		"""
	When jobs批量上架商品:weapp
		"""
		[
			"bill无规格商品2",
			"bill无规格商品1"
		]
		"""
	When jobs新建团购活动:weapp
		"""
		[{
			"group_name":"团购活动1",
			"start_date":"今天",
			"end_date":"2天后",
			"product_name":"bill无规格商品1",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":10.00
				}],
				"ship_date":20,
				"product_counts":100,
				"material_image":"1.jpg",
				"share_description":"团购活动1分享描述"
		},{
			"group_name":"团购活动2",
			"start_date":"今天",
			"end_date":"2天后",
			"product_name":"bill无规格商品2",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":20.00
				},{
					"group_type":10,
					"group_days":2,
					"group_price":21.00
				}],
				"ship_date":20,
				"product_counts":100,
				"material_image":"1.jpg",
				"share_description":"团购活动2分享描述"
		}]
		"""
	When jobs开启团购活动'团购活动1':weapp
	When jobs开启团购活动'团购活动2':weapp

@eugene @sync_order
Scenario:1 自营平台团购活动未成功，订单不同步到商户平台
	商户同步到自营平台的商户创建团购活动
	1.团购订单支付后未成功，订单不同步到商户平台

	Given tom关注jobs的公众号
	#tom参与团购"团购活动1"开团
	When tom访问jobs的webapp
	When tom参加jobs的团购活动"团购活动2"进行开团:weapp
		"""
		{
			"group_name": "团购活动2",
			"group_leader": "tom",
			"group_dict":
				{
					"group_type":"10",
					"group_days":"2",
					"group_price":"21.00"
				},
			"products": {
				"name": "bill无规格商品2"
			}
		}
		"""
	When tom提交团购订单
		"""
		{
			"ship_name": "tom",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"order_id":"001",
			"pay_type":"微信支付"
		}
		"""
	When tom使用支付方式'微信支付'进行支付

	Given jobs登录系统:weapp
	#团购活动未成功，不在后台显示订单
	Then jobs可以看到订单列表:weapp
		"""
		[]
		"""
	#团购活动的订单未成功不同步到商家平台
	Given bill登录系统:weapp
	Then bill可以看到订单列表:weapp
		"""
		[]
		"""

@eugene @sync_order
Scenario:2 自营平台团购活动失败，订单不同步到商户平台
	商户同步到自营平台的商户创建团购活动
	1.团购订单支付后活动失败，订单不同步到商户平台

	Given tom关注jobs的公众号
	#tom参与团购"团购活动1"开团
	When tom访问jobs的webapp
	When tom参加jobs的团购活动"团购活动1"进行开团:weapp
		"""
		{
			"group_name": "团购活动1",
			"group_leader": "tom",
			"group_dict":
				{
					"group_type":"5",
					"group_days":"1",
					"group_price":"10.00"
				},
			"products": {
				"name": "bill无规格商品1"
			}
		}
		"""
	When tom提交团购订单
		"""
		{
			"ship_name": "tom",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"order_id":"001",
			"pay_type":"微信支付"
		}
		"""
	When tom使用支付方式'微信支付'进行支付
	Given bill登录系统:weapp
	When bill'下架'商品'bill无规格商品1':weapp

	#商户下架自营平台参加团购活动的商品，自营平台的团购活动失败
	#团购订单状态为退款中
	Given jobs登录系统:weapp
	Then jobs可以看到订单列表:weapp
		"""
		[{
			"order_no":"001",
			"is_group_buying":"true",
			"status": "退款中",
			"buyer":"tom",
			"final_price":10.00,
			"save_money":112.12,
			"methods_of_payment": "微信支付",
			"actions": [],
			"products":
				[{
					"name":"bill无规格商品1",
					"supplier":"bill商家",
					"price":122.12,
					"count":1
				}]
		}]
		"""
	And jobs获得财务审核'团购退款'订单列表:weapp
		"""
		[{
			"order_no":"001",
			"supplier":"bill商家",
			"is_group_buying":"true",
			"status": "退款中",
			"buyer":"tom",
			"final_price":10.00,
			"save_money":112.12,
			"methods_of_payment": "微信支付",
			"actions": [],
			"products":
				[{
					"name":"bill无规格商品1",
					"price":122.12,
					"count":1
				}]
		}]
		"""
	#团购订单状态为退款中,不同步到商家
	Given bill登录系统:weapp
	Then bill可以看到订单列表:weapp
		"""
		[]
		"""
	And bill获得财务审核'团购退款'订单列表:weapp
		"""
		[]
		"""

@eugene @sync_order
Scenario:3 自营平台团购活动成功，订单同步到商户平台
	商户同步到自营平台的商户创建团购活动
	1.团购订单支付后活动成功，订单同步到商户平台

	Given tom关注jobs的公众号
	And tom1关注jobs的公众号
	And tom2关注jobs的公众号
	And tom3关注jobs的公众号
	And tom4关注jobs的公众号

	When tom访问jobs的webapp
	When tom参加jobs的团购活动"团购活动1"进行开团:weapp
		"""
		{
			"group_name": "团购活动1",
			"group_leader": "tom",
			"group_dict":
				{
					"group_type":"5",
					"group_days":"1",
					"group_price":"10.00"
				},
			"products": {
				"name": "bill无规格商品1"
			}
		}
		"""
	When tom提交团购订单
		"""
		{
			"ship_name": "tom",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"order_id":"001",
			"pay_type":"微信支付"
		}
		"""
	When tom使用支付方式'微信支付'进行支付
	#tom1参与tom开的团
	When tom1访问jobs的webapp
	Then tom1能获得"团购活动1"的已开团活动列表:weapp
		"""
		[{
			"group_name": "团购活动1",
			"group_leader": "tom",
			"product_name": "bill无规格商品1",
			"participant_count": "1/5"
		}]
		"""
	When tom1参加tom的团购活动"团购活动1":weapp
		"""
		{
			"group_name": "团购活动1",
			"group_leader": "tom",
			"group_dict":
				{
					"group_type":5,
					"group_days":1,
					"group_price":10.00
				},
			"products": {
				"name": "bill无规格商品1"
			}
		}
		"""
	When tom1提交团购订单
		"""
		{
			"ship_name": "tom1",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"order_id":"002",
			"pay_type":"微信支付"
		}
		"""
	When tom1使用支付方式'微信支付'进行支付

	#tom2参与tom开的团
	When tom2访问jobs的webapp
	Then tom2能获得"团购活动1"的已开团活动列表:weapp
		"""
		[{
			"group_name": "团购活动1",
			"group_leader": "tom",
			"product_name": "bill无规格商品1",
			"participant_count": "2/5"
		}]
		"""
	When tom2参加tom的团购活动"团购活动1":weapp
		"""
		{
			"group_name": "团购活动1",
			"group_leader": "tom",
			"group_dict":
				{
					"group_type":5,
					"group_days":1,
					"group_price":10.00
				},
			"products": {
				"name": "bill无规格商品1"
			}
		}
		"""
	When tom2提交团购订单
		"""
		{
			"ship_name": "tom2",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"order_id":"003",
			"pay_type":"微信支付"
		}
		"""
	When tom2使用支付方式'微信支付'进行支付

	#tom3参与tom开的团
	When tom3访问jobs的webapp
	Then tom3能获得"团购活动1"的已开团活动列表:weapp
		"""
		[{
			"group_name": "团购活动1",
			"group_leader": "tom",
			"product_name": "bill无规格商品1",
			"participant_count": "3/5"
		}]
		"""
	When tom3参加tom的团购活动"团购活动1":weapp
		"""
		{
			"group_name": "团购活动1",
			"group_leader": "tom",
			"group_dict":
				{
					"group_type":5,
					"group_days":1,
					"group_price":10.00
				},
			"products": {
				"name": "bill无规格商品1"
			}
		}
		"""
	When tom3提交团购订单
		"""
		{
			"ship_name": "tom3",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"order_id":"004",
			"pay_type":"微信支付"
		}
		"""
	When tom3使用支付方式'微信支付'进行支付

	#tom4参与tom开的团
	When tom4访问jobs的webapp
	Then tom4能获得"团购活动1"的已开团活动列表:weapp
		"""
		[{
			"group_name": "团购活动1",
			"group_leader": "tom",
			"product_name": "bill无规格商品1",
			"participant_count": "4/5"
		}]
		"""
	When tom4参加tom的团购活动"团购活动1":weapp
		"""
		{
			"group_name": "团购活动1",
			"group_leader": "tom",
			"group_dict":
				{
					"group_type":5,
					"group_days":1,
					"group_price":10.00
				},
			"products": {
				"name": "bill无规格商品1"
			}
		}
		"""
	When tom4提交团购订单
		"""
		{
			"ship_name": "tom4",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"order_id":"005",
			"pay_type":"微信支付"
		}
		"""
	When tom4使用支付方式'微信支付'进行支付
	#Then tom4获得提示信息'恭喜您团购成功 商家将在该商品团购结束20天内进行发货'

	#团购成功，后台可以看到待发货订单
	Given jobs登录系统:weapp
	Then jobs可以看到订单列表:weapp
		"""
		[{
			"order_no":"005",
			"is_group_buying":"true",
			"status": "待发货",
			"buyer":"tom4",
			"final_price":10.00,
			"save_money":112.12,
			"methods_of_payment": "微信支付",
			"actions": ["发货"],
			"products":
				[{
					"name":"bill无规格商品1",
					"supplier":"bill商家",
					"price":122.12,
					"count":1
				}]
		},{
			"order_no":"004",
			"is_group_buying":"true",
			"status": "待发货",
			"buyer":"tom3",
			"final_price":10.00,
			"save_money":112.12,
			"methods_of_payment": "微信支付",
			"actions": ["发货"],
			"products":
				[{
					"name":"bill无规格商品1",
					"supplier":"bill商家",
					"price":122.12,
					"count":1
				}]
		},{
			"order_no":"003",
			"is_group_buying":"true",
			"status": "待发货",
			"buyer":"tom2",
			"final_price":10.00,
			"save_money":112.12,
			"methods_of_payment": "微信支付",
			"actions": ["发货"],
			"products":
				[{
					"name":"bill无规格商品1",
					"price":122.12,
					"supplier":"bill商家",
					"count":1
				}]
		},{
			"order_no":"002",
			"is_group_buying":"true",
			"status": "待发货",
			"buyer":"tom1",
			"final_price":10.00,
			"save_money":112.12,
			"methods_of_payment": "微信支付",
			"actions": ["发货"],
			"products":
				[{
					"name":"bill无规格商品1",
					"supplier":"bill商家",
					"price":122.12,
					"count":1
				}]
		},{
			"order_no":"001",
			"is_group_buying":"true",
			"status": "待发货",
			"buyer":"tom",
			"final_price":10.00,
			"save_money":112.12,
			"methods_of_payment": "微信支付",
			"actions": ["发货"],
			"products":
				[{
					"name":"bill无规格商品1",
					"supplier":"bill商家",
					"price":122.12,
					"count":1
				}]
		}]
		"""

	#团购订单成功,同步到商家，不显示团购的icon，订单金额为商品的采购价
	Given bill登录系统:weapp
	Then bill可以看到订单列表:weapp
		"""
		[{
			"order_no":"005-bill商家",
			"sources": "商城",
			"status": "待发货",
			"buyer":"tom4",
			"final_price":9.00,
			"methods_of_payment": "微信支付",
			"actions": ["发货"],
			"products":
				[{
					"name":"bill无规格商品1",
					"price":"",
					"count":1
				}]
		},{
			"order_no":"004-bill商家",
			"sources": "商城",
			"status": "待发货",
			"buyer":"tom3",
			"final_price":9.00,
			"methods_of_payment": "微信支付",
			"actions": ["发货"],
			"products":
				[{
					"name":"bill无规格商品1",
					"price":"",
					"count":1
				}]
		},{
			"order_no":"003-bill商家",
			"sources": "商城",
			"status": "待发货",
			"buyer":"tom2",
			"final_price":9.00,
			"methods_of_payment": "微信支付",
			"actions": ["发货"],
			"products":
				[{
					"name":"bill无规格商品1",
					"price":"",
					"count":1
				}]
		},{
			"order_no":"002-bill商家",
			"sources": "商城",
			"status": "待发货",
			"buyer":"tom1",
			"final_price":9.00,
			"methods_of_payment": "微信支付",
			"actions": ["发货"],
			"products":
				[{
					"name":"bill无规格商品1",
					"price":"",
					"count":1
				}]
		},{
			"order_no":"001-bill商家",
			"sources": "商城",
			"status": "待发货",
			"buyer":"tom",
			"final_price":9.00,
			"methods_of_payment": "微信支付",
			"actions": ["发货"],
			"products":
				[{
					"name":"bill无规格商品1",
					"price":"",
					"count":1
				}]
		}]
		"""








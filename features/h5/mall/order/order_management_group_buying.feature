# watcher: benchi@weizoom.com, zhangsanxiang@weizoom.com
#_author_:张三香 2016.03.09

Feature:订单管理-团购
	"""
		1、订单编号后面增加团购订单标识-'团'，与普通订单区分开来
		2、在'所有订单'中，待支付和团购中的待发货订单都隐藏，团购成功的待发货订单显示出来
		3、'财务审核'里增加'团购退款'选项卡，显示所有退款中的订单，但是没有退款成功的操作按钮；当退款金额打到用户账户里自动标记退款完成
		4、团购的退款订单只显示在'财务审核-团购退款'中，其他选项卡中不显示
		5、团购成功的订单，订单列表中单价显示商品的原价，优惠金额=原价-团购价
	"""

Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
	And jobs已添加支付方式:weapp
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
	When jobs开通使用微众卡权限:weapp
	When jobs添加支付方式:weapp
		"""
		[{
			"type": "微众卡支付",
			"is_active": "启用"
		}]
		"""
	Given jobs已添加商品:weapp
		"""
		[{
			"name":"商品1",
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"user_code":"0101",
						"weight":1.0,
						"stock_type": "有限",
						"stocks": 100
					}
				}
			},
			"postage":10.0,
			"distribution_time":"on"
		},{
			"name":"商品2",
			"model": {
				"models": {
					"standard": {
						"price": 200.00,
						"user_code":"0102",
						"weight":1.0,
						"stock_type": "无限"
					}
				}
			}
		}]
		"""
	Given jobs已创建微众卡:weapp
		"""
		[{
			"cards": [{
				"id": "0000001",
				"password": "1234567",
				"status": "未使用",
				"price": 50
			},{
			"cards": [{
				"id": "0000002",
				"password": "2234567",
				"status": "未使用",
				"price": 200
		}]
		"""
	When jobs新建团购活动:weapp
		"""
		[{
			"group_name":"团购活动1",
			"start_time":"今天",
			"end_time":"2天后",
			"product_name":"商品1",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":90.00
				}],
				"ship_date":20,
				"product_counts":100,
				"material_image":"1.jpg",
				"share_description":"团购活动1分享描述"
		},{
			"group_name":"团购活动2",
			"start_time":"今天",
			"end_time":"2天后",
			"product_name":"商品2",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":190.00
				},{
					"group_type":10,
					"group_days":2,
					"group_price":188.00
				}],
				"ship_date":20,
				"product_counts":100,
				"material_image":"1.jpg",
				"share_description":"团购活动2分享描述"
		}]
		"""

	Given bill关注jobs的公众号
	And tom关注jobs的公众号
	And bill1关注jobs的公众号
	And bill2关注jobs的公众号
	And bill3关注jobs的公众号

	#订单数据
	When bill访问jobs的webapp
	#00101-待发货（团购中,bill开团'团购活动1'）
		When bill参加jobs的团购活动
			"""
			{
				"group_name": "团购活动1",
				"group_leader": "bill",
				"group_dict":
					[{
						"group_type":5,
						"group_days":1,
						"group_price":90.00
					}],
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"distribution_time":"5天后 10:00-12:30",
				"order_id":"00101",
				"pay_type":"微信支付",
				"products": [{
					"name": "商品1"
				}]
			}
			"""
		When bill使用支付方式'微信支付'进行支付
	#00102-待支付（tom参团'团购活动1'）
		When tom参加jobs的团购活动
			"""
			{
				"group_name": "团购活动1",
				"group_leader": "bill",
				"group_dict":
					[{
						"group_type":5,
						"group_days":1,
						"group_price":90.00
					}],
				"ship_name": "tom",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"distribution_time":"5天后 10:00-12:30",
				"order_id":"00102",
				"pay_type":"微信支付",
				"products": [{
					"name": "商品1"
				}]
			}
			"""
	#00103-待发货（团购中，有微众卡支付，bill1参团'团购活动1'）
		When bill1参加jobs的团购活动
			"""
			{
				"group_name": "团购活动1",
				"group_leader": "bill",
				"group_dict":
					[{
						"group_type":5,
						"group_days":1,
						"group_price":90.00
					}],
				"ship_name": "bill1",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"distribution_time":"5天后 10:00-12:30",
				"order_id":"00103",
				"pay_type":"微信支付",
				"products": [{
					"name": "商品1"
				}],
				"weizoom_card":[{
					"card_name":"0000001",
					"card_pass":"1234567"
						}]
			}
			"""
		When bill1使用支付方式'微信支付'进行支付

	#00201-待发货（团购成功,tom开团'团购活动2'）
		When tom参加jobs的团购活动
			"""
			{
				"group_name": "团购活动2",
				"group_leader": "tom",
				"group_dict":
					[{
						"group_type":5,
						"group_days":1,
						"group_price":190.00
					}],
				"ship_name": "tom",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"order_id":"00201",
				"pay_type":"微信支付",
				"products": [{
					"name": "商品2"
				}]
			}
			"""
		When tom使用支付方式'微信支付'进行支付
	#00202-待发货（团购成功,bill参团'团购活动2'）
		When bill参加jobs的团购活动
			"""
			{
				"group_name": "团购活动2",
				"group_leader": "tom",
				"group_dict":
					[{
						"group_type":5,
						"group_days":1,
						"group_price":190.00
					}],
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"order_id":"00202",
				"pay_type":"微信支付",
				"products": [{
					"name": "商品2"
				}]
			}
			"""
		When bill使用支付方式'微信支付'进行支付
	#00203-待发货（团购成功,bill1参团'团购活动2'）
		When bill1参加jobs的团购活动
			"""
			{
				"group_name": "团购活动2",
				"group_leader": "tom",
				"group_dict":
					[{
						"group_type":5,
						"group_days":1,
						"group_price":190.00
					}],
				"ship_name": "bill1",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"order_id":"00203",
				"pay_type":"微信支付",
				"products": [{
					"name": "商品2"
				}]
			}
			"""
		When bill1使用支付方式'微信支付'进行支付
	#00204-待发货（团购成功,bill2参团'团购活动2'）
		When bill2参加jobs的团购活动
			"""
			{
				"group_name": "团购活动2",
				"group_leader": "tom",
				"group_dict":
					[{
						"group_type":5,
						"group_days":1,
						"group_price":190.00
					}],
				"ship_name": "bill2",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"order_id":"00204",
				"pay_type":"微信支付",
				"products": [{
					"name": "商品2"
				}]
			}
			"""
		When bill2使用支付方式'微信支付'进行支付
	#00205-待发货（团购成功,bill3参团'团购活动2'）
		When bill3参加jobs的团购活动
			"""
			{
				"group_name": "团购活动2",
				"group_leader": "tom",
				"group_dict":
					[{
						"group_type":5,
						"group_days":1,
						"group_price":190.00
					}],
				"ship_name": "bill3",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"order_id":"00205",
				"pay_type":"微信支付",
				"products": [{
					"name": "商品2"
				}],
				"weizoom_card":[{
					"card_name":"0000001",
					"card_pass":"1234567"
						}]
			}
			"""

@order
Scenario:1 所有订单-查看团购订单
	#待支付和团购中的'待发货'订单在订单列表中不显示
	#团购成功的订单,订单列表页不能进行【申请退款】和【取消订单】操作
	#团购成功的订单,订单详情页页不能进行【申请退款】和【取消订单】操作

	Given jobs登录系统:weapp
	Then jobs可以看到订单列表:weapp
		"""
		[{
			"order_no":"00205",
			"sources": "本店",
			"is_group_buying":"true",
			"status": "待发货",
			"buyer":"bill3",
			"final_price":190.00,
			"save_money":10.0,
			"methods_of_payment": "优惠抵扣",
			"actions": ["发货"],
			"products":
				[{
					"name":"商品2",
					"price":200.00,
					"count":1
				}]
		},{
			"order_no":"00204",
			"sources": "本店",
			"is_group_buying":"true",
			"status": "待发货",
			"buyer":"bill2",
			"final_price":190.00,
			"save_money":10.0,
			"methods_of_payment": "微信支付",
			"actions": ["发货"],
			"products":
				[{
					"name":"商品2",
					"price":200.00,
					"count":1
				}]
		},{
			"order_no":"00203",
			"sources": "本店",
			"is_group_buying":"true",
			"status": "待发货",
			"buyer":"bill1",
			"final_price":190.00,
			"save_money":10.0,
			"methods_of_payment": "微信支付",
			"actions": ["发货"],
			"products":
				[{
					"name":"商品2",
					"price":200.00,
					"count":1
				}]
		},{
			"order_no":"00202",
			"sources": "本店",
			"is_group_buying":"true",
			"status": "待发货",
			"buyer":"bill",
			"final_price":190.00,
			"save_money":10.0,
			"methods_of_payment": "微信支付",
			"actions": ["发货"],
			"products":
				[{
					"name":"商品2",
					"price":200.00,
					"count":1
				}]
		},{
			"order_no":"00201",
			"sources": "本店",
			"is_group_buying":"true",
			"status": "待发货",
			"buyer":"tom",
			"final_price":190.00,
			"save_money":10.0,
			"methods_of_payment": "微信支付",
			"actions": ["发货"],
			"products":
				[{
					"name":"商品2",
					"price":200.00,
					"count":1
				}]
		}]
		"""
	#优惠抵扣方式-订单详情页也不能进行'取消订单'操作
	And jobs能获得订单'00205':weapp
		"""
		{
			"order_no":"00205",
			"sources": "本店",
			"status": "待发货",
			"final_price":190.00,
			"methods_of_payment": "优惠抵扣",
			"actions": ["发货"],
			"products":
				[{
					"name":"商品2",
					"price":200.00,
					"count":1
				}]
		}
		"""
	#微信支付方式-订单详情页也不能进行'申请退款'操作
	And jobs能获得订单'00204':weapp
		"""
		{
			"order_no":"00204",
			"sources": "本店",
			"status": "待发货",
			"final_price":190.00,
			"methods_of_payment": "微信支付",
			"actions": ["发货"],
			"products":
				[{
					"name":"商品2",
					"price":200.00,
					"count":1
				}]
		}
		"""

@order
Scenario:2 财务审核-查看'团购退款'订单
	Given jobs登录系统:weapp
	When jobs'结束'团购活动'团购活动1':weapp
	Then jobs可以看到订单列表:weapp
		"""
		[{
			"order_no":"00205",
			"sources": "本店",
			"is_group_buying":"true",
			"status": "待发货",
			"buyer":"bill3",
			"final_price":190.00,
			"save_money":10.0,
			"methods_of_payment": "优惠抵扣",
			"actions": ["发货"],
			"products":
				[{
					"name":"商品2",
					"price":200.00,
					"count":1
				}]
		},{
			"order_no":"00204",
			"sources": "本店",
			"is_group_buying":"true",
			"status": "待发货",
			"buyer":"bill2",
			"final_price":190.00,
			"save_money":10.0,
			"methods_of_payment": "微信支付",
			"actions": ["发货"],
			"products":
				[{
					"name":"商品2",
					"price":200.00,
					"count":1
				}]
		},{
			"order_no":"00203",
			"sources": "本店",
			"is_group_buying":"true",
			"status": "待发货",
			"buyer":"bill1",
			"final_price":190.00,
			"save_money":10.0,
			"methods_of_payment": "微信支付",
			"actions": ["发货"],
			"products":
				[{
					"name":"商品2",
					"price":200.00,
					"count":1
				}]
		},{
			"order_no":"00202",
			"sources": "本店",
			"is_group_buying":"true",
			"status": "待发货",
			"buyer":"bill",
			"final_price":190.00,
			"save_money":10.0,
			"methods_of_payment": "微信支付",
			"actions": ["发货"],
			"products":
				[{
					"name":"商品2",
					"price":200.00,
					"count":1
				}]
		},{
			"order_no":"00201",
			"sources": "本店",
			"is_group_buying":"true",
			"status": "待发货",
			"buyer":"tom",
			"final_price":190.00,
			"save_money":10.0,
			"methods_of_payment": "微信支付",
			"actions": ["发货"],
			"products":
				[{
					"name":"商品2",
					"price":200.00,
					"count":1
				}]
		}]
		"""
	And jobs获得财务审核'团购退款'订单列表:weapp
		"""
		[{
			"order_no":"00103",
			"sources": "本店",
			"is_group_buying":"true",
			"status": "退款中",
			"buyer":"bill1",
			"final_price":90.00,
			"save_money":10.0,
			"methods_of_payment": "微信支付",
			"actions": [],
			"products":
				[{
					"name":"商品1",
					"price":100.00,
					"count":1
				}]
		},{
			"order_no":"00101",
			"sources": "本店",
			"is_group_buying":"true",
			"status": "退款中",
			"buyer":"bill",
			"final_price":90.00,
			"save_money":10.0,
			"methods_of_payment": "微信支付",
			"actions": [],
			"products":
				[{
					"name":"商品1",
					"price":100.00,
					"count":1
				}]
		}]
		"""
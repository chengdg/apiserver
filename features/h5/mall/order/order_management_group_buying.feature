# watcher: benchi@weizoom.com, zhangsanxiang@weizoom.com
#_author_:张三香 2016.03.09

Feature:订单管理-团购
	"""
		1、订单编号后面增加团购订单标识-'团'，与普通订单区分开来
		2、在"所有订单"中团购相关订单显示规则:
			a.待支付和团购中的待发货订单都隐藏
			b.团购成功的'待发货'订单显示出来,如果团购失败'待发货'订单变为'退款中'订单显示出来
			c.优惠抵扣方式的订单,团购失败后该订单状态为'已取消',显示在"所有订单中"
			d.15分钟未支付的'已取消'订单,在"所有订单"中不显示
		3、"财务审核"里增加'团购退款'选项卡:
			a.显示所有团购的'退款中'和'退款完成'状态的订单;
			b.'退款中'的订单没有【退款成功】的操作按钮,当退款金额打到用户账户里自动标记为'退款完成'
			c.团购退款的订单只显示在'团购退款'这个选项卡中,全部、退款中和退款完成这3个选项卡中不显示团购退款的订单
		5、团购成功的订单，订单列表中单价显示商品的原价，优惠金额=原价-团购价
		6、查询条件'订单类型'下拉框中增加'团购订单'
	"""

Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
	When jobs添加微信证书:weapp
	Given jobs已添加支付方式:weapp
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
			"postage":10.00,
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
		},{
			"name":"商品3",
			"model": {
				"models": {
					"standard": {
						"price": 300.00,
						"user_code":"0103",
						"weight":1.0,
						"stock_type": "无限"
					}
				}
			}
		}]
		"""
	Given jobs已创建微众卡:weapp
		"""
		{
			"cards": [{
				"id": "0000000",
				"password": "0234567",
				"status": "未使用",
				"price": 50.00
			},{
				"id": "0000001",
				"password": "1234567",
				"status": "未使用",
				"price": 50.00
			},{
				"id": "0000002",
				"password": "2234567",
				"status": "未使用",
				"price": 100.00
			},{
				"id": "0000003",
				"password": "3234567",
				"status": "未使用",
				"price": 200.00
			}]
		}
		"""
	When jobs新建团购活动:weapp
		"""
		[{
			"group_name":"团购活动1",
			"start_date":"今天",
			"end_date":"2天后",
			"product_name":"商品1",
			"group_dict":{
				"0":{
					"group_type":"5",
					"group_days":"1",
					"group_price":"90.00"
					}
				},
				"ship_date":20,
				"product_counts":100,
				"material_image":"1.jpg",
				"share_description":"团购活动1分享描述"
		},{
			"group_name":"团购活动2",
			"start_date":"今天",
			"end_date":"2天后",
			"product_name":"商品2",
			"group_dict":{
				"0":{
					"group_type":"5",
					"group_days":"1",
					"group_price":"190.00"
					},
				"1":{
					"group_type":"10",
					"group_days":"2",
					"group_price":"188.00"
					}
				},
				"ship_date":20,
				"product_counts":100,
				"material_image":"1.jpg",
				"share_description":"团购活动2分享描述"
		}]
		"""
	When jobs开启团购活动'团购活动1':weapp
	When jobs开启团购活动'团购活动2':weapp

	Given bill关注jobs的公众号
	And tom关注jobs的公众号
	And bill1关注jobs的公众号
	And bill2关注jobs的公众号
	And bill3关注jobs的公众号

	#订单数据
	#00101-待发货（团购中,bill开团'团购活动1'）
		When bill访问jobs的webapp
		When bill参加jobs的团购活动"团购活动1"进行开团:weapp
			"""
			{
				"group_name": "团购活动1",
				"group_leader": "bill",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":90.00
					},
				"products": {
					"name": "商品1"
				}
			}
			"""
		When bill提交团购订单
			"""
			{
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"distribution_time":"5天后 10:00-12:30",
				"order_id":"00101",
				"pay_type":"微信支付"
			}
			"""
		When bill使用支付方式'微信支付'进行支付
	#00102-待支付（有用微众卡,tom参团'团购活动1'）
		When tom访问jobs的webapp
		When tom参加bill的团购活动"团购活动1":weapp
			"""
			{
				"group_name": "团购活动1",
				"group_leader": "bill",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":90.00
					},
				"products": {
					"name": "商品1"
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
				"distribution_time":"5天后 10:00-12:30",
				"order_id":"00102",
				"pay_type":"微信支付",
				"weizoom_card":[{
					"card_name":"0000000",
					"card_pass":"0234567"
						}]
			}
			"""
	#00103-待发货（团购中，现金+微众卡支付，bill1参团'团购活动1'）
		When bill1访问jobs的webapp
		When bill1参加bill的团购活动"团购活动1":weapp
			"""
			{
				"group_name": "团购活动1",
				"group_leader": "bill",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":90.00
					},
				"products": {
					"name": "商品1"
				}
			}
			"""
		When bill1提交团购订单
			"""
			{
				"ship_name": "bill1",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"distribution_time":"5天后 10:00-12:30",
				"order_id":"00103",
				"pay_type":"微信支付",
				"weizoom_card":[{
					"card_name":"0000001",
					"card_pass":"1234567"
						}]
			}
			"""
		When bill1使用支付方式'微信支付'进行支付
	#00104-待发货（团购中，全额微众卡支付，bill2参团'团购活动1'）
		When bill2访问jobs的webapp
		When bill2参加bill的团购活动"团购活动1":weapp
			"""
			{
				"group_name": "团购活动1",
				"group_leader": "bill",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":90.00
					},
				"products": {
					"name": "商品1"
				}
			}
			"""
		When bill2提交团购订单
			"""
			{
				"ship_name": "bill2",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"distribution_time":"5天后 10:00-12:30",
				"order_id":"00104",
				"pay_type":"微信支付",
				"weizoom_card":[{
					"card_name":"0000002",
					"card_pass":"2234567"
						}]
			}
			"""

	#00105-待支付（非团购订单，bill购买'商品3'）
		When bill访问jobs的webapp
		When bill购买jobs的商品
			"""
			{
				"order_id": "00105",
				"pay_type":"微信支付",
				"products": [{
					"name": "商品3",
					"count": 1
				}]
			}
			"""

	#00201-待发货（团购成功,tom开团'团购活动2'）
		When tom访问jobs的webapp
		When tom参加jobs的团购活动"团购活动2"进行开团:weapp
			"""
			{
				"group_name": "团购活动2",
				"group_leader": "tom",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":190.00
					},
				"products": {
					"name": "商品2"
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
				"order_id":"00201",
				"pay_type":"微信支付"
			}
			"""
		When tom使用支付方式'微信支付'进行支付
	#00202-待发货（团购成功,bill参团'团购活动2'）
		When bill访问jobs的webapp
		When bill参加tom的团购活动"团购活动2":weapp
			"""
			{
				"group_name": "团购活动2",
				"group_leader": "tom",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":190.00
					},
				"products": {
					"name": "商品2"
				}
			}
			"""
		When bill提交团购订单
			"""
			{
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"order_id":"00202",
				"pay_type":"微信支付"
			}
			"""
		When bill使用支付方式'微信支付'进行支付
	#00203-待发货（团购成功,bill1参团'团购活动2'）
		When bill1访问jobs的webapp
		When bill1参加tom的团购活动"团购活动2":weapp
			"""
			{
				"group_name": "团购活动2",
				"group_leader": "tom",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":190.00
					},
				"products": {
					"name": "商品2"
				}
			}
			"""
		When bill1提交团购订单
			"""
			{
				"ship_name": "bill1",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"order_id":"00203",
				"pay_type":"微信支付"
			}
			"""
		When bill1使用支付方式'微信支付'进行支付
	#00204-待发货（团购成功,bill2参团'团购活动2'）
		When bill2访问jobs的webapp
		When bill2参加tom的团购活动"团购活动2":weapp
			"""
			{
				"group_name": "团购活动2",
				"group_leader": "tom",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":190.00
					},
				"products": {
					"name": "商品2"
				}
			}
			"""
		When bill2提交团购订单
			"""
			{
				"ship_name": "bill2",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"order_id":"00204",
				"pay_type":"微信支付"
			}
			"""
		When bill2使用支付方式'微信支付'进行支付
	#00205-待发货（团购成功,bill3参团'团购活动2'）
		When bill3访问jobs的webapp
		When bill3参加tom的团购活动"团购活动2":weapp
			"""
			{
				"group_name": "团购活动2",
				"group_leader": "tom",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":190.00
					},
				"products": {
					"name": "商品2"
				}
			}
			"""
		When bill3提交团购订单
			"""
			{
				"ship_name": "bill2",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"order_id":"00205",
				"pay_type":"微信支付",
				"weizoom_card":[{
					"card_name":"0000003",
					"card_pass":"3234567"
						}]
			}
			"""

@mall3 @order @eugene
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
			"save_money":10.00,
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
			"save_money":10.00,
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
			"save_money":10.00,
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
			"save_money":10.00,
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
			"save_money":10.00,
			"methods_of_payment": "微信支付",
			"actions": ["发货"],
			"products":
				[{
					"name":"商品2",
					"price":200.00,
					"count":1
				}]
		},{
			"order_no":"00105",
			"sources": "本店",
			"is_group_buying":"false",
			"status": "待支付",
			"buyer":"bill",
			"final_price":300.00,
			"save_money":0.00,
			"methods_of_payment": "微信支付",
			"actions": ["支付","修改价格","取消订单"],
			"products":
				[{
					"name":"商品3",
					"price":300.00,
					"count":1
				}]
		}]
		"""

	#查看团购订单的订单详情页
		#优惠抵扣方式-订单详情页也不能进行'取消订单'操作
		And jobs能获得订单'00205':weapp
			"""
			{
				"order_no":"00205",
				"sources": "本店",
				"status": "待发货",
				"final_price":0.00,
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

	#对团购成功的订单进行【发货】、【标记完成】操作
		#进行【发货】
		When jobs对订单进行发货:weapp
			"""
			{
				"order_no":"00205",
				"logistics":"顺丰速运",
				"number":"123456789",
				"shipper":"jobs"
			}
			"""
		When jobs对订单进行发货:weapp
			"""
			{
				"order_no": "00204",
				"logistics": "off",
				"shipper": ""
			}
			"""
		Then jobs可以看到订单列表:weapp
			"""
			[{
				"order_no":"00205",
				"sources": "本店",
				"is_group_buying":"true",
				"status": "已发货",
				"buyer":"bill3",
				"final_price":190.00,
				"save_money":10.00,
				"methods_of_payment": "优惠抵扣",
				"logistics": "顺丰速运",
				"number": "123456789",
				"shipper": "jobs",
				"actions": ["标记完成","修改物流"],
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
				"status": "已发货",
				"buyer":"bill2",
				"final_price":190.00,
				"save_money":10.00,
				"methods_of_payment": "微信支付",
				"actions": ["标记完成"],
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
				"save_money":10.00,
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
				"save_money":10.00,
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
				"save_money":10.00,
				"methods_of_payment": "微信支付",
				"actions": ["发货"],
				"products":
					[{
						"name":"商品2",
						"price":200.00,
						"count":1
					}]
			},{
				"order_no":"00105",
				"sources": "本店",
				"is_group_buying":"false",
				"status": "待支付",
				"buyer":"bill",
				"final_price":300.00,
				"save_money":0.00,
				"methods_of_payment": "微信支付",
				"actions": ["支付","修改价格","取消订单"],
				"products":
					[{
						"name":"商品3",
						"price":300.00,
						"count":1
					}]
			}]
			"""
		#进行【标记完成】
		When jobs'完成'订单'00205':weapp
		When jobs'完成'订单'00204':weapp
		Then jobs可以看到订单列表:weapp
			"""
			[{
				"order_no":"00205",
				"sources": "本店",
				"is_group_buying":"true",
				"status": "已完成",
				"buyer":"bill3",
				"final_price":190.00,
				"save_money":10.00,
				"methods_of_payment": "优惠抵扣",
				"logistics": "顺丰速运",
				"number": "123456789",
				"shipper": "jobs",
				"actions": [],
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
				"status": "已完成",
				"buyer":"bill2",
				"final_price":190.00,
				"save_money":10.00,
				"methods_of_payment": "微信支付",
				"actions": [],
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
				"save_money":10.00,
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
				"save_money":10.00,
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
				"save_money":10.00,
				"methods_of_payment": "微信支付",
				"actions": ["发货"],
				"products":
					[{
						"name":"商品2",
						"price":200.00,
						"count":1
					}]
			},{
				"order_no":"00105",
				"sources": "本店",
				"is_group_buying":"false",
				"status": "待支付",
				"buyer":"bill",
				"final_price":300.00,
				"save_money":0.00,
				"methods_of_payment": "微信支付",
				"actions": ["支付","修改价格","取消订单"],
				"products":
					[{
						"name":"商品3",
						"price":300.00,
						"count":1
					}]
			}]
			"""

@mall3 @order @eugene
Scenario:2 所有订单-团购订单查询
	When jobs根据给定条件查询订单:weapp
		"""
		{
			"order_type": "团购订单"
		}
		"""
	Then jobs可以看到订单列表:weapp
		"""
		[{
			"order_no":"00205",
			"sources": "本店",
			"is_group_buying":"true",
			"status": "待发货",
			"buyer":"bill3",
			"final_price":190.00,
			"save_money":10.00,
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
			"save_money":10.00,
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
			"save_money":10.00,
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
			"save_money":10.00,
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
			"save_money":10.00,
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

@mall3 @order @eugene @tgyc
Scenario:3 查看团购失败的订单
	#所有订单-显示团购失败的'退款中'（退款成功）和优惠抵扣方式的'已取消'订单
	#财务审核-团购失败的'退款中'（退款成功）的订单只显示在"团购退款"选项卡中

	#团购失败前,查看微众卡余额
		When tom访问jobs的webapp
		When tom进行微众卡余额查询
			"""
			{
				"id":"0000000",
				"password":"0234567"
			}
			"""
		Then tom获得微众卡余额查询结果
			"""
			{
				"card_remaining":0.00
			}
			"""

		When bill1访问jobs的webapp
		When bill1进行微众卡余额查询
			"""
			{
				"id":"0000001",
				"password":"1234567"
			}
			"""
		Then bill1获得微众卡余额查询结果
			"""
			{
				"card_remaining":0.00
			}
			"""

		When bill2访问jobs的webapp
		When bill2进行微众卡余额查询
			"""
			{
				"id":"0000002",
				"password":"2234567"
			}
			"""
		Then bill2获得微众卡余额查询结果
			"""
			{
				"card_remaining":10.00
			}
			"""

	#查看团购失败的订单
		Given jobs登录系统:weapp
		When jobs关闭团购活动'团购活动1':weapp
		Then jobs可以看到订单列表:weapp
			"""
			[{
				"order_no":"00205",
				"sources": "本店",
				"is_group_buying":"true",
				"status": "待发货",
				"buyer":"bill3",
				"final_price":190.00,
				"save_money":10.00,
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
				"save_money":10.00,
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
				"save_money":10.00,
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
				"save_money":10.00,
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
				"save_money":10.00,
				"methods_of_payment": "微信支付",
				"actions": ["发货"],
				"products":
					[{
						"name":"商品2",
						"price":200.00,
						"count":1
					}]
			},{
				"order_no":"00105",
				"sources": "本店",
				"is_group_buying":"false",
				"status": "待支付",
				"buyer":"bill",
				"final_price":300.00,
				"save_money":0.00,
				"methods_of_payment": "微信支付",
				"actions": ["支付","修改价格","取消订单"],
				"products":
					[{
						"name":"商品3",
						"price":300.00,
						"count":1
					}]
			},{
				"order_no":"00104",
				"sources": "本店",
				"is_group_buying":"true",
				"status": "已取消",
				"buyer":"bill2",
				"final_price":90.00,
				"save_money":10.00,
				"methods_of_payment": "优惠抵扣",
				"actions": [],
				"products":
					[{
						"name":"商品1",
						"price":100.00,
						"count":1
					}]
			},{
				"order_no":"00103",
				"sources": "本店",
				"is_group_buying":"true",
				"status": "退款中",
				"buyer":"bill1",
				"final_price":90.00,
				"save_money":10.00,
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
				"save_money":10.00,
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
		And jobs获得财务审核'团购退款'订单列表:weapp
			"""
			[{
				"order_no":"00103",
				"sources": "本店",
				"is_group_buying":"true",
				"status": "退款中",
				"buyer":"bill1",
				"final_price":90.00,
				"save_money":10.00,
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
				"save_money":10.00,
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

	#团购失败后，查看微众卡余额
		#待支付->已取消（订单取消后，微众卡的钱退回）
			When tom访问jobs的webapp
			When tom进行微众卡余额查询
				"""
				{
					"id":"0000000",
					"password":"0234567"
				}
				"""
			Then tom获得微众卡余额查询结果
				"""
				{
					"card_remaining":50.00
				}
				"""
		#待发货->已取消（订单取消后，微众卡的钱退回）
			When bill2访问jobs的webapp
			When bill2进行微众卡余额查询
				"""
				{
					"id":"0000002",
					"password":"2234567"
				}
				"""
			Then bill2获得微众卡余额查询结果
				"""
				{
					"card_remaining":100.00
				}
				"""

	#微信自动退款,订单状态自动标记为'退款成功'(因无法实现steps，所以注释掉)
		# When 微信'退款成功'订单'00103':weapp
		# When 微信'退款成功'订单'00101':weapp
		# #现金+微众卡支付的订单，订单"退款成功"后，微众卡的钱退回
		# 	When bill1访问jobs的webapp
		# 	When bill1进行微众卡余额查询
		# 		"""
		# 		{
		# 			"id":"0000001",
		# 			"password":"1234567"
		# 		}
		# 		"""
		# 	Then bill1获得微众卡余额查询结果
		# 		"""
		# 		{
		# 			"card_remaining":50.00
		# 		}
		# 		"""

		# Given jobs登录系统:weapp
		# Then jobs可以看到订单列表:weapp
		# 	"""
		# 	[{
		# 		"order_no":"00205",
		# 		"sources": "本店",
		# 		"is_group_buying":"true",
		# 		"status": "待发货",
		# 		"buyer":"bill3",
		# 		"final_price":190.00,
		# 		"save_money":10.00,
		# 		"methods_of_payment": "优惠抵扣",
		# 		"actions": ["发货"],
		# 		"products":
		# 			[{
		# 				"name":"商品2",
		# 				"price":200.00,
		# 				"count":1
		# 			}]
		# 	},{
		# 		"order_no":"00204",
		# 		"sources": "本店",
		# 		"is_group_buying":"true",
		# 		"status": "待发货",
		# 		"buyer":"bill2",
		# 		"final_price":190.00,
		# 		"save_money":10.00,
		# 		"methods_of_payment": "微信支付",
		# 		"actions": ["发货"],
		# 		"products":
		# 			[{
		# 				"name":"商品2",
		# 				"price":200.00,
		# 				"count":1
		# 			}]
		# 	},{
		# 		"order_no":"00203",
		# 		"sources": "本店",
		# 		"is_group_buying":"true",
		# 		"status": "待发货",
		# 		"buyer":"bill1",
		# 		"final_price":190.00,
		# 		"save_money":10.00,
		# 		"methods_of_payment": "微信支付",
		# 		"actions": ["发货"],
		# 		"products":
		# 			[{
		# 				"name":"商品2",
		# 				"price":200.00,
		# 				"count":1
		# 			}]
		# 	},{
		# 		"order_no":"00202",
		# 		"sources": "本店",
		# 		"is_group_buying":"true",
		# 		"status": "待发货",
		# 		"buyer":"bill",
		# 		"final_price":190.00,
		# 		"save_money":10.00,
		# 		"methods_of_payment": "微信支付",
		# 		"actions": ["发货"],
		# 		"products":
		# 			[{
		# 				"name":"商品2",
		# 				"price":200.00,
		# 				"count":1
		# 			}]
		# 	},{
		# 		"order_no":"00201",
		# 		"sources": "本店",
		# 		"is_group_buying":"true",
		# 		"status": "待发货",
		# 		"buyer":"tom",
		# 		"final_price":190.00,
		# 		"save_money":10.00,
		# 		"methods_of_payment": "微信支付",
		# 		"actions": ["发货"],
		# 		"products":
		# 			[{
		# 				"name":"商品2",
		# 				"price":200.00,
		# 				"count":1
		# 			}]
		# 	},{
		# 		"order_no":"00105",
		# 		"sources": "本店",
		# 		"is_group_buying":"false",
		# 		"status": "待支付",
		# 		"buyer":"bill",
		# 		"final_price":300.00,
		# 		"save_money":0.00,
		# 		"methods_of_payment": "微信支付",
		# 		"actions": ["支付","修改价格","取消订单"],
		# 		"products":
		# 			[{
		# 				"name":"商品3",
		# 				"price":300.00,
		# 				"count":1
		# 			}]
		# 	},{
		# 		"order_no":"00104",
		# 		"sources": "本店",
		# 		"is_group_buying":"ture",
		# 		"status": "已取消",
		# 		"buyer":"bill2",
		# 		"final_price":90.00,
		# 		"save_money":10.00,
		# 		"methods_of_payment": "优惠抵扣",
		# 		"actions": [],
		# 		"products":
		# 			[{
		# 				"name":"商品1",
		# 				"price":100.00,
		# 				"count":1
		# 			}]
		# 	},{
		# 		"order_no":"00103",
		# 		"sources": "本店",
		# 		"is_group_buying":"true",
		# 		"status": "退款成功",
		# 		"buyer":"bill1",
		# 		"final_price":90.00,
		# 		"save_money":10.00,
		# 		"methods_of_payment": "微信支付",
		# 		"actions": [],
		# 		"products":
		# 			[{
		# 				"name":"商品1",
		# 				"price":100.00,
		# 				"count":1
		# 			}]
		# 	},{
		# 		"order_no":"00101",
		# 		"sources": "本店",
		# 		"is_group_buying":"true",
		# 		"status": "退款成功",
		# 		"buyer":"bill",
		# 		"final_price":90.00,
		# 		"save_money":10.00,
		# 		"methods_of_payment": "微信支付",
		# 		"actions": [],
		# 		"products":
		# 			[{
		# 				"name":"商品1",
		# 				"price":100.00,
		# 				"count":1
		# 			}]
		# 	}]
		# 	"""
		# And jobs获得财务审核'团购退款'订单列表:weapp
		# 	"""
		# 	[{
		# 		"order_no":"00103",
		# 		"sources": "本店",
		# 		"is_group_buying":"true",
		# 		"status": "退款完成",
		# 		"buyer":"bill1",
		# 		"final_price":90.00,
		# 		"save_money":10.00,
		# 		"methods_of_payment": "微信支付",
		# 		"actions": [],
		# 		"products":
		# 			[{
		# 				"name":"商品1",
		# 				"price":100.00,
		# 				"count":1
		# 			}]
		# 	},{
		# 		"order_no":"00101",
		# 		"sources": "本店",
		# 		"is_group_buying":"true",
		# 		"status": "退款完成",
		# 		"buyer":"bill",
		# 		"final_price":90.00,
		# 		"save_money":10.00,
		# 		"methods_of_payment": "微信支付",
		# 		"actions": [],
		# 		"products":
		# 			[{
		# 				"name":"商品1",
		# 				"price":100.00,
		# 				"count":1
		# 			}]
		# 	}]
		# 	"""

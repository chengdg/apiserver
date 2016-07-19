# watcher:wangli@weizoomm.com,benchi@weizoom.com
#_author_:王丽 2016.03.09

Feature:从个人中心浏览不同状态的订单列表中的团购订单
"""
	1 团购的订单按照订单状态不同对应显示在个人中心的不同状态的订单列表中
	2 团购订单在订单列表和订单详情中订单状态右侧有“团”字小图标
	3 当前台出现待支付的团购订单有15min判断期，超过15min，待支付订单被取消。15min之内可以进行再次支付
	4 不显示所有团购自动取消的订单
	5 当因为某种原因导致第一次支付没有完成，现在可以通过两种方式进行二次支付
		1)通过全部订单中的待支付订单进行支付。
		2)通过团购活动链接进入时，提示“开团支付未完成，是否继续”。如果点“是”进入编辑订单页面，如果点否，取消之前生成的待支付订单
	6 订单列表中，团购订单状态为"待发货"的显示"查看团购"按钮，其他状态不显示；
	订单详情中，团购订单状态为{"待发货"，"已发货"，"已完成"}的显示"查看团购"按钮，其他状态不显示；
"""

Background:
	Given 重置'weapp'的bdd环境
	Given 重置'weizoom_card'的bdd环境
	Given jobs登录系统::weapp
	When jobs添加微信证书::weapp

	Given jobs已有微众卡支付权限::weapp
	And jobs已添加支付方式::weapp
		"""
		[{
			"type": "微众卡支付"
		},{
			"type": "微信支付"
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
			"num":"1",
			"comments":"微众卡"
		},{
			"name":"20元微众卡",
			"prefix_value":"020",
			"type":"virtual",
			"money":"20.00",
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
					"order_num":"1",
					"start_date":"2016-04-07 00:00",
					"end_date":"2019-10-07 00:00"
				},{
					"name":"20元微众卡",
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

	And jobs已添加商品规格::weapp
		"""
		[{
			"name": "尺寸",
			"type": "文字",
			"values": [{
				"name": "M"
			}, {
				"name": "S"
			}]
		}]
		"""
	And jobs已添加商品::weapp
		"""
		[{
			"name": "商品1",
			"price":100.00,
			"postage": 10.00
		}, {
			"name": "商品2",
			"price": 50.00,
			"distribution_time":"on",
			"postage": "顺丰"
		},{
			"name": "商品3",
			"is_enable_model": "启用规格",
			"model": {
				"models": {
					"M": {
						"price": 30.00
					},
					"S": {
						"price": 30.00
					}
				}
			}
		},{
			"name": "商品4",
			"price": 40.00,
			"stock_type": "有限",
			"stocks": 10
		}]
		"""

	When jobs新建团购活动::weapp
		"""
		[{
			"group_name": "团购活动1",
			"start_date": "2015-07-08 00:00:00",
			"end_date": "2天后",
			"product_name": "商品1",
			"group_dict":[{
				"group_type":"5",
				"group_days": "6",
				"group_price": "80.00"
			},{
				"group_type": "10",
				"group_days": "10",
				"group_price": "50.00"
			}],
			"ship_date": 20,
			"product_counts": 100,
			"material_image": "1.jpg",
			"share_description": "团购分享描述"
		},{
			"group_name": "团购活动2",
			"start_date": "2015-07-08 00:00:00",
			"end_date": "3天后",
			"product_name": "商品2",
			"group_dict":[{
				"group_type": "5",
				"group_days": "6",
				"group_price": "40.00"
			}],
			"ship_date": 10,
			"product_counts": 200,
			"material_image": "1.jpg",
			"share_description": "团购分享描述"
		}]
		"""
	When jobs开启团购活动'团购活动1'::weapp
	When jobs开启团购活动'团购活动2'::weapp

	Given bill关注jobs的公众号
	Given tom关注jobs的公众号
	Given tom1关注jobs的公众号
	Given tom2关注jobs的公众号

@mall3 @group_t @weizoom_card
Scenario:1 订单列表只有团购订单-团购进行中
	1 同一个会员参与同一个团购活动的不同团-未成团
	2 同一个会员参与不同团购活动的团-未成团

	#bill作为团长开团参与团购活动"团购活动1"
		When bill访问jobs的webapp
		When bill参加jobs的团购活动"团购活动1"进行开团::weapp
			"""
			{
				"group_name": "团购活动1",
				"group_leader": "bill",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":80.00
					},
				"products": {
					"name": "商品1"
				}
			}
			"""
		When bill提交团购订单
			"""
			{
				"order_id": "0001",
				"date": "2015-08-08 00:00:00",
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付"
			}
			"""
		When bill使用支付方式'微信支付'进行支付
		When bill访问个人中心
		Then bill查看个人中心'全部'订单列表
			"""
			[{
				"order_no": "0001",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.08 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			}]
			"""
		Then bill查看个人中心'待发货'订单列表
			"""
			[{
				"order_no": "0001",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.08 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			}]
			"""

	#tom参团"bill作为团长"购买
		When tom访问jobs的webapp
		When tom参加bill的团购活动"团购活动1"::weapp
			"""
			{
				"group_name": "团购活动1",
				"group_leader": "bill",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":80.00
					},
				"products": {
					"name": "商品1"
				}
			}
			"""
		When tom提交团购订单
			"""
			{
				"order_id": "0002",
				"date": "2015-08-09 00:00:00",
				"ship_name": "tom",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付"
			}
			"""
		When tom使用支付方式'微信支付'进行支付
		When tom访问个人中心
		Then tom查看个人中心'全部'订单列表
			"""
			[{
				"order_no": "0002",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.09 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			}]
			"""
		Then tom查看个人中心'待发货'订单列表
			"""
			[{
				"order_no": "0002",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.09 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			}]
			"""

	#tom作为团长开团参与团购活动"团购活动1"
		When tom访问jobs的webapp
		When tom参加jobs的团购活动"团购活动1"进行开团::weapp
			"""
			{
				"group_name": "团购活动1",
				"group_leader": "tom",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":80.00
					},
				"products": {
					"name": "商品1"
				}
			}
			"""
		When tom提交团购订单
			"""
			{
				"order_id": "0003",
				"date": "2015-08-10 00:00:00",
				"ship_name": "tom",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付"
			}
			"""
		When tom使用支付方式'微信支付'进行支付
		When tom访问个人中心
		Then tom查看个人中心'全部'订单列表
			"""
			[{
				"order_no": "0003",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.10 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			},{
				"order_no": "0002",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.09 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			}]
			"""
		Then tom查看个人中心'待发货'订单列表
			"""
			[{
				"order_no": "0003",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.10 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			},{
				"order_no": "0002",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.09 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			}]
			"""

	#bill参团"tom作为团长"购买：微众卡支付的订单，实付金额为0
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
		When bill参加tom的团购活动"团购活动1"::weapp
			"""
			{
				"group_name": "团购活动1",
				"group_leader": "tom",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":80.00
					},
				"products": {
					"name": "商品1"
				}
			}
			"""
		When bill提交团购订单
			"""
			{
				"order_id": "0004",
				"date": "2015-08-09 00:00:00",
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付",
				"weizoom_card":[{
					"card_name":"100000001",
					"card_pass":"1234567"
				}]
			}
			"""
		When bill访问个人中心
		Then bill查看个人中心'全部'订单列表
			"""
			[{
				"order_no": "0004",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.09 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 0.00
			},{
				"order_no": "0001",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.08 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			}]
			"""
		Then bill查看个人中心'待发货'订单列表
			"""
			[{
				"order_no": "0004",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.09 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 0.00
			},{
				"order_no": "0001",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.08 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			}]
			"""

	#bill作为团长开团参与团购活动"团购活动2"
		When bill访问jobs的webapp
		When bill参加jobs的团购活动"团购活动2"进行开团::weapp
			"""
			{
				"group_name": "团购活动2",
				"group_leader": "bill",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":40.00
					},
				"products": {
					"name": "商品2"
				}
			}
			"""
		When bill提交团购订单
			"""
			{
				"order_id": "0005",
				"date": "2015-08-10 00:00:00",
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付"
			}
			"""
		When bill使用支付方式'微信支付'进行支付
		When bill访问个人中心
		Then bill查看个人中心'全部'订单列表
			"""
			[{
				"order_no": "0005",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.10 00:00",
				"products": [{
					"name": "商品2"
				}],
				"counts": 1,
				"final_price": 40.00
			},{
				"order_no": "0004",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.09 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 0.00
			},{
				"order_no": "0001",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.08 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			}]
			"""
		Then bill查看个人中心'待发货'订单列表
			"""
			[{
				"order_no": "0005",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.10 00:00",
				"products": [{
					"name": "商品2"
				}],
				"counts": 1,
				"final_price": 40.00
			},{
				"order_no": "0004",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.09 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 0.00
			},{
				"order_no": "0001",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.08 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			}]
			"""

	#tom参团"bill作为团长"购买：微众卡支付部分订单金额
		When tom访问jobs的webapp
		When tom绑定微众卡
			"""
			{
				"binding_date":"2016-06-16",
				"binding_shop":"jobs",
				"weizoom_card_info":
					{
						"id":"020000001",
						"password":"1234567"
					}
			}
			"""
		When tom参加bill的团购活动"团购活动2"::weapp
			"""
			{
				"group_name": "团购活动2",
				"group_leader": "bill",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":80.00
					},
				"products": {
					"name": "商品2"
				}
			}
			"""
		When tom提交团购订单
			"""
			{
				"order_id": "0006",
				"date": "2015-08-10 00:00:00",
				"ship_name": "tom",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付",
				"weizoom_card":[{
					"card_name":"020000001",
					"card_pass":"1234567"
				}]
			}
			"""
		When tom使用支付方式'微信支付'进行支付
		When tom访问个人中心
		Then tom查看个人中心'全部'订单列表
			"""
			[{
				"order_no": "0006",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.10 00:00",
				"products": [{
					"name": "商品2"
				}],
				"counts": 1,
				"final_price": 20.00
			},{
				"order_no": "0003",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.10 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			},{
				"order_no": "0002",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.09 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			}]
			"""
		Then tom查看个人中心'待发货'订单列表
			"""
			[{
				"order_no": "0006",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.10 00:00",
				"products": [{
					"name": "商品2"
				}],
				"counts": 1,
				"final_price": 20.00
			},{
				"order_no": "0003",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.10 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			},{
				"order_no": "0002",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.09 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			}]
			"""

@mall3 @group_t
Scenario:2 订单列表只有团购订单-团购未成团(退款成功，微信退款不能用feature实现)
	#1 由于团购活动时间过期、组团时间过期、手动结束团购活动造成未组团成功
	#团购支付的所有订单自动进入"退款中"状态，自动退款

	#bill作为团长开团参与团购活动"团购活动1"
		When bill访问jobs的webapp
		When bill参加jobs的团购活动"团购活动1"进行开团::weapp
			"""
			{
				"group_name": "团购活动1",
				"group_leader": "bill",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":80.00
					},
				"products": {
					"name": "商品1"
				}
			}
			"""
		When bill提交团购订单
			"""
			{
				"order_id": "0001",
				"date": "2015-08-08 00:00:00",
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付"
			}
			"""
		When bill使用支付方式'微信支付'进行支付

	#tom参团"bill作为团长"购买
		When tom访问jobs的webapp
		When tom参加bill的团购活动"团购活动1"::weapp
			"""
			{
				"group_name": "团购活动1",
				"group_leader": "bill",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":80.00
					},
				"products": {
					"name": "商品1"
				}
			}
			"""
		When tom提交团购订单
			"""
			{
				"order_id": "0002",
				"date": "2015-08-08 00:00:00",
				"ship_name": "tom",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付"
			}
			"""
		When tom使用支付方式'微信支付'进行支付

	#手动结束团购活动，未成功的团订单进入退款
		Given jobs登录系统::weapp
		When jobs关闭团购活动'团购活动1'::weapp

		When bill访问jobs的webapp
		When bill访问个人中心
		Then bill查看个人中心'全部'订单列表
			"""
			[{
				"order_no": "0001",
				"is_group_buying": "true",
				"status": "退款中",
				"created_at": "2015.08.08 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			}]
			"""

		When tom访问jobs的webapp
		When tom访问个人中心
		Then tom查看个人中心'全部'订单列表
			"""
			[{
				"order_no": "0002",
				"is_group_buying": "true",
				"status": "退款中",
				"created_at": "2015.08.08 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			}]
			"""

@mall3 @group_t @gyct12 @ztqb
Scenario:3 订单列表只有团购订单-团购成团订单发货、完成订单
	#团购成功的订单进行发货和完成订单

	#bill作为团长开团参与团购活动"团购活动1"
		When bill访问jobs的webapp
		When bill参加jobs的团购活动"团购活动1"进行开团::weapp
			"""
			{
				"group_name": "团购活动1",
				"group_leader": "bill",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":80.00
					},
				"products": {
					"name": "商品1"
				}
			}
			"""
		When bill提交团购订单
			"""
			{
				"order_id": "0001",
				"date": "2015-08-08 00:00:00",
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付"
			}
			"""
		When bill使用支付方式'微信支付'进行支付

	#tom参团"bill作为团长"购买
		When tom访问jobs的webapp
		When tom参加bill的团购活动"团购活动1"::weapp
			"""
			{
				"group_name": "团购活动1",
				"group_leader": "bill",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":80.00
					},
				"products": {
					"name": "商品1"
				}
			}
			"""
		When tom提交团购订单
			"""
			{
				"order_id": "0002",
				"date": "2015-08-09 00:00:00",
				"ship_name": "tom",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付"
			}
			"""
		When tom使用支付方式'微信支付'进行支付

	#tom1参团"bill作为团长"购买
		When tom1访问jobs的webapp
		When tom1参加bill的团购活动"团购活动1"::weapp
			"""
			{
				"group_name": "团购活动1",
				"group_leader": "bill",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":80.00
					},
				"products": {
					"name": "商品1"
				}
			}
			"""
		When tom1提交团购订单
			"""
			{
				"order_id": "0003",
				"date": "2015-08-10 00:00:00",
				"ship_name": "tom1",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付"
			}
			"""
		When tom1使用支付方式'微信支付'进行支付

	#tom2参团"bill作为团长"购买
		When tom2访问jobs的webapp
		When tom2参加bill的团购活动"团购活动1"::weapp
			"""
			{
				"group_name": "团购活动1",
				"group_leader": "bill",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":80.00
					},
				"products": {
					"name": "商品1"
				}
			}
			"""
		When tom2提交团购订单
			"""
			{
				"order_id": "0004",
				"date": "2015-08-11 00:00:00",
				"ship_name": "tom2",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付"
			}
			"""
		When tom2使用支付方式'微信支付'进行支付

	#非会员参团购买
	#tom3参团"bill作为团长"购买
		When tom3访问jobs的webapp
		When tom3参加bill的团购活动"团购活动1"::weapp
			"""
			{
				"group_name": "团购活动1",
				"group_leader": "bill",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":80.00
					},
				"products": {
					"name": "商品1"
				}
			}
			"""
		When tom3提交团购订单
			"""
			{
				"order_id": "0005",
				"date": "2015-08-12 00:00:00",
				"ship_name": "tom3",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付"
			}
			"""
		When tom3使用支付方式'微信支付'进行支付

	#团购成功，对订单进行发货
		Given jobs登录系统::weapp
		When jobs对订单进行发货::weapp
			"""
			{
				"order_no":"0001",
				"logistics":"顺丰速运",
				"number":"123456789"
			}
			"""
		When jobs对订单进行发货::weapp
			"""
			{
				"order_no": "0002",
				"logistics": "off",
				"shipper": ""
			}
			"""

		When bill访问jobs的webapp
		When bill访问个人中心
		Then bill查看个人中心'全部'订单列表
			"""
			[{
				"order_no": "0001",
				"is_group_buying": "true",
				"status": "待收货",
				"created_at": "2015.08.08 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			}]
			""" 

		When tom访问jobs的webapp
		When tom访问个人中心
		Then tom查看个人中心'全部'订单列表
			"""
			[{
				"order_no": "0002",
				"is_group_buying": "true",
				"status": "待收货",
				"created_at": "2015.08.09 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			}]
			""" 

	#确认收货
		Given jobs登录系统::weapp
		When jobs完成订单'0001'::weapp

		When tom访问jobs的webapp
		When tom确认收货订单'0002'
		When tom访问个人中心
		Then tom查看个人中心'全部'订单列表
			"""
			[{
				"order_no": "0002",
				"is_group_buying": "true",
				"status": "已完成",
				"created_at": "2015.08.09 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			}]
			""" 

		When bill访问jobs的webapp
		When bill访问个人中心
		Then bill查看个人中心'全部'订单列表
			"""
			[{
				"order_no": "0001",
				"is_group_buying": "true",
				"status": "已完成",
				"created_at": "2015.08.08 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			}]
			""" 
			
@mall3 @group_t
Scenario:4 订单列表团购进行中订单+普通订单
	#在开团之前，购买团购商品
		When bill访问jobs的webapp
		When bill购买jobs的商品
			"""
			{
				"order_id": "1001",
				"date": "2015-08-05 00:00:00",
				"pay_type":"微信支付",
				"products": [{
					"name": "商品3",
					"model": "M",
					"count": 1
				}]
			}
			"""
		Then bill成功创建订单
			"""
			{
				"order_no":"1001",
				"is_group_buying": "false",
				"status": "待支付",
				"final_price": 30.00,
				"products": [{
					"name": "商品3",
					"price": 30.00,
					"count": 1
				}]
			}
			"""
		When bill购买jobs的商品
			"""
			{
				"order_id": "1002",
				"date": "2015-08-06 00:00:00",
				"pay_type":"微信支付",
				"products": [{
					"name": "商品4",
					"count": 1
				}]
			}
			"""
		Then bill成功创建订单
			"""
			{
				"order_no":"1002",
				"is_group_buying": "false",
				"status": "待支付",
				"final_price": 40.00,
				"products": [{
					"name": "商品4",
					"price": 40.00,
					"count": 1
				}]
			}
			"""

		When bill访问个人中心
		Then bill查看个人中心'全部'订单列表
			"""
			[{
				"order_no": "1002",
				"is_group_buying": "false",
				"status": "待支付",
				"created_at": "2015.08.06 00:00",
				"products": [{
					"name": "商品4"
				}],
				"counts": 1,
				"final_price": 40.00
			},{
				"order_no": "1001",
				"is_group_buying": "false",
				"status": "待支付",
				"created_at": "2015.08.05 00:00",
				"products": [{
					"name": "商品3"
				}],
				"counts": 1,
				"final_price": 30.00
			}]
			"""
		Then bill查看个人中心'待支付'订单列表
			"""
			[{
				"order_no": "1002",
				"is_group_buying": "false",
				"status": "待支付",
				"created_at": "2015.08.06 00:00",
				"products": [{
					"name": "商品4"
				}],
				"counts": 1,
				"final_price": 40.00
			},{
				"order_no": "1001",
				"is_group_buying": "false",
				"status": "待支付",
				"created_at": "2015.08.05 00:00",
				"products": [{
					"name": "商品3"
				}],
				"counts": 1,
				"final_price": 30.00
			}]
			"""

	#创建商品4的团购活动

		Given jobs登录系统::weapp
		When jobs新建团购活动::weapp
			"""
			[{
				"group_name": "团购活动4",
				"start_date": "2015-07-08 00:00:00",
				"end_date": "2天后",
				"product_name": "商品4",
				"group_dict":[{
					"group_type": "5",
					"group_days": "1",
					"group_price": "20.00"
				}],
				"ship_date": 20,
				"product_counts": 100,
				"material_image": "1.jpg",
				"share_description": "团购分享描述"
			}]
			"""
		When jobs开启团购活动'团购活动4'::weapp

	#bill作为团长开团参与团购活动"团购活动4"
		When bill访问jobs的webapp
		When bill参加jobs的团购活动"团购活动4"进行开团::weapp
			"""
			{
				"group_name": "团购活动4",
				"group_leader": "bill",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":20.00
					},
				"products": {
					"name": "商品4"
				}
			}
			"""
		When bill提交团购订单
			"""
			{
				"order_id": "0001",
				"date": "2015-08-08 00:00:00",
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付"
			}
			"""
		Then bill成功创建订单
			"""
			{
				"order_no":"0001",
				"is_group_buying": "true",
				"status": "待支付",
				"final_price": 20.00,
				"products": [{
					"name": "商品4",
					"price": 20.00,
					"count": 1
				}]
			}
			"""
		When bill使用支付方式'微信支付'进行支付
		Then bill成功创建订单
			"""
			{
				"order_no":"0001",
				"is_group_buying": "true",
				"status": "待发货",
				"final_price": 20.00,
				"products": [{
					"name": "商品4",
					"price": 20.00,
					"count": 1
				}]
			}
			"""
		When bill访问个人中心
		Then bill查看个人中心'全部'订单列表
			"""
			[{
				"order_no": "0001",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.08 00:00",
				"products": [{
					"name": "商品4"
				}],
				"counts": 1,
				"final_price": 20.00
			},{
				"order_no": "1002",
				"is_group_buying": "false",
				"status": "待支付",
				"created_at": "2015.08.06 00:00",
				"products": [{
					"name": "商品4"
				}],
				"counts": 1,
				"final_price": 40.00
			},{
				"order_no": "1001",
				"is_group_buying": "false",
				"status": "待支付",
				"created_at": "2015.08.05 00:00",
				"products": [{
					"name": "商品3"
				}],
				"counts": 1,
				"final_price": 30.00
			}]
			"""
		Then bill查看个人中心'待发货'订单列表
			"""
			[{
				"order_no": "0001",
				"is_group_buying": "true",
				"status": "待发货",
				"created_at": "2015.08.08 00:00",
				"products": [{
					"name": "商品4"
				}],
				"counts": 1,
				"final_price": 20.00
			}]
			"""
		Then bill查看个人中心'待支付'订单列表
			"""
			[{
				"order_no": "1002",
				"is_group_buying": "false",
				"status": "待支付",
				"created_at": "2015.08.06 00:00",
				"products": [{
					"name": "商品4"
				}],
				"counts": 1,
				"final_price": 40.00
			},{
				"order_no": "1001",
				"is_group_buying": "false",
				"status": "待支付",
				"created_at": "2015.08.05 00:00",
				"products": [{
					"name": "商品3"
				}],
				"counts": 1,
				"final_price": 30.00
			}]
			"""

@mall3
Scenario:5 订单列表团购订单-手机端开团未支付订单
		When bill访问jobs的webapp
		When bill参加jobs的团购活动"团购活动1"进行开团::weapp
			"""
			{
				"group_name": "团购活动1",
				"group_leader": "bill",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":80.00
					},
				"products": {
					"name": "商品1"
				}
			}
			"""
		When bill提交团购订单
			"""
			{
				"order_id": "0001",
				"date": "2015-08-08 00:00:00",
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付"
			}
			"""

		When bill访问个人中心
		Then bill查看个人中心'全部'订单列表
			"""
			[{
				"order_no": "0001",
				"is_group_buying": "true",
				"status": "待支付",
				"created_at": "2015.08.08 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			}]
			"""

		#活动结束，开团未支付订单自动取消
		Given jobs登录系统::weapp
		When jobs关闭团购活动'团购活动1'::weapp

		When bill访问jobs的webapp
		When bill访问个人中心
		Then bill查看个人中心'全部'订单列表
			"""
			[]
			"""

@mall3 @group_t
Scenario:6 订单列表团购订单-手机端参团未支付订单
	#bill作为团长开团参与团购活动"团购活动1"
		When bill访问jobs的webapp
		When bill参加jobs的团购活动"团购活动1"进行开团::weapp
			"""
			{
				"group_name": "团购活动1",
				"group_leader": "bill",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":80.00
					},
				"products": {
					"name": "商品1"
				}
			}
			"""
		When bill提交团购订单
			"""
			{
				"order_id": "0001",
				"date": "2015-08-08 00:00:00",
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付"
			}
			"""
		When bill使用支付方式'微信支付'进行支付

	#tom参团"bill作为团长"购买
		When tom访问jobs的webapp
		When tom参加bill的团购活动"团购活动1"::weapp
			"""
			{
				"group_name": "团购活动1",
				"group_leader": "bill",
				"group_dict":
					{
						"group_type":5,
						"group_days":1,
						"group_price":80.00
					},
				"products": {
					"name": "商品1"
				}
			}
			"""
		When tom提交团购订单
			"""
			{
				"order_id": "0002",
				"date": "2015-08-08 00:00:00",
				"ship_name": "tom",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付"
			}
			"""

		When tom访问个人中心
		Then tom查看个人中心'全部'订单列表
			"""
			[{
				"order_no": "0002",
				"is_group_buying": "true",
				"status": "待支付",
				"created_at": "2015.08.08 00:00",
				"products": [{
					"name": "商品1"
				}],
				"counts": 1,
				"final_price": 80.00
			}]
			"""

	#手动结束团购活动，未成功的团订单进入退款
		Given jobs登录系统::weapp
		When jobs关闭团购活动'团购活动1'::weapp

		When tom访问jobs的webapp
		When tom访问个人中心
		Then tom查看个人中心'全部'订单列表
			"""
			[]
			"""

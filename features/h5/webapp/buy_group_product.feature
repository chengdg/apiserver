# watcher: fengxuejing@weizoom.com,benchi@weizoom.com
# __author__ : "冯雪静"
# __editor__ : "王丽" 2016-03-22
#团购：手机端购买
Feature: 手机端购买团购活动
	"""
	手机端访问团购活动，进行购买
		1.团购商品在商品列表页显示商品的原价
		2.会员访问团购活动，能进行开团购买
		3.会员可开团也可参团，非会员可以参团，不能开团
		4.开团后，人数达到上限，团购成功，获得成功页面，参与团购会员手机端会收到模板消息
		5.开团后，人数没有达到标准，期限到了，团购失败，支付的订单自动退款
		6.下单成功，库存减少，团购失败，库存恢复
		7.开团时下单不进行支付，不能成功开团
		8.一个会员可以参加多个团，对一个团购活动只能开一次团，不能重复参加，也不能重复开团
		9.参团列表参团人数一样的话以开团时间倒序显示，优先显示团购差一人的团
		10.商品加入购物车后，后台对此商品创建团购活动，此商品在购物车为失效状态，结束活动后，购物车的商品恢复正常
	"""

Background:
	Given 重置weapp的bdd环境
	Given 重置weizoom_card的bdd环境
	Given jobs登录系统:weapp
	When jobs添加微信证书:weapp
	Given jobs已有微众卡支付权限:weapp
	And jobs已添加支付方式:weapp
		"""
		[{
			"type": "支付宝"
		},{
			"type": "微众卡支付"
		}, {
			"type": "货到付款"
		}, {
			"type": "微信支付"
		}]
		"""

	#创建微众卡
	Given test登录管理系统:weizoom_card
	When test新建通用卡:weizoom_card
		"""
		[{
			"name":"100元微众卡",
			"prefix_value":"100",
			"type":"virtual",
			"money":"100.00",
			"num":"1",
			"comments":"微众卡"
		}]
		"""

	#微众卡审批出库
	When test下订单:weizoom_card
			"""
			[{
				"card_info":[{
					"name":"100元微众卡",
					"order_num":"1",
					"start_date":"2016-04-07 00:00",
					"end_date":"2019-10-07 00:00"
				}],
				"order_info":{
					"order_id":"0001"
				}
			}]
			"""
	And test批量激活订单'0001'的卡:weizoom_card

	When jobs添加邮费配置:weapp
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
	And jobs已添加商品:weapp
		"""
		[{
			"name": "商品1",
			"price": 100.00,
			"weight": 1,
			"postage": "顺丰",
			"distribution_time":"on"
		}, {
			"name": "商品2",
			"price": 100.00,
			"weight": 1,
			"stock_type": "有限",
			"stocks": 100,
			"postage": 10.00
		}, {
			"name": "商品3",
			"price": 100.00,
			"stock_type": "有限",
			"stocks": 9
		}]
		"""
	And jobs新建团购活动:weapp
		"""
		[{
			"group_name":"团购1",
			"start_date":"今天",
			"end_date":"2天后",
			"product_name":"商品1",
			"group_dict":{
				"0":{
					"group_type":"5",
					"group_days":"1",
					"group_price":"20.00"
					},
				"1":{
					"group_type":"10",
					"group_days":"2",
					"group_price":"10.00"
				}
			},
			"ship_date":"20",
			"product_counts":"100",
			"material_image":"1.jpg",
			"share_description":"团购分享描述"
		}, {
			"group_name":"团购2",
			"start_date":"今天",
			"end_date":"3天后",
			"product_name":"商品2",
			"group_dict":{
				"0":{
					"group_type":"5",
					"group_days":"2",
					"group_price":"21.00"
					},
				"1":{
					"group_type":"10",
					"group_days":"2",
					"group_price":"11.00"
				}
			},
			"ship_date":"20",
			"product_counts":"100",
			"material_image":"1.jpg",
			"share_description":"团购分享描述"
		}]
		"""
	When jobs开启团购活动'团购1':weapp
	When jobs开启团购活动'团购2':weapp

	Given bill关注jobs的公众号
	And tom关注jobs的公众号

@mall3 @nj_group
Scenario: 1 会员访问团购活动首页能进行开团
	jobs创建团购，活动期内
	1.bill获得商品列表页
	2.会员bill可以开团购买，开团成功后就不能重复开一个团购活动
	3.会员tom可以通过bill分享的链接直接参团
	4.非会员nokia通过分享链接能直接参团，不能开团购买

	When bill访问jobs的webapp
	And bill浏览jobs的webapp的'全部'商品列表页
	Then bill获得webapp商品列表
		"""
		[{
			"name": "商品3",
			"price": 100.00
		}, {
			"name": "商品2",
			"price": 100.00
		}, {
			"name": "商品1",
			"price": 100.00
		}]
		"""

	#bill是已关注的会员可以直接开团
	#获得的是所有jobs开启的团购活动列表
	Then bill能获得jobs的团购活动列表:weapp
		"""
		[{
			"group_name": "团购2",
			"group_dict":
				[{
					"group_type":"5",
					"group_price":"21.00"
				},{
					"group_type":"10",
					"group_price":"11.00"
				}]
		},{
			"group_name": "团购1",
			"group_dict":
				[{
					"group_type":"5",
					"group_price":"20.00"
				},{
					"group_type":"10",
					"group_price":"10.00"
				}]
		}]
		"""

	#bill开“团购5人团”，团购活动只能使用微信支付，有配送时间，运费0元
	#支付完成后跳转到活动详情页-显示邀请好友参团
	When bill参加jobs的团购活动"团购1"进行开团:weapp
		"""
		{
			"group_name": "团购1",
			"group_leader": "bill",
			"group_dict":
				{
					"group_type":5,
					"group_days":1,
					"group_price":20.00
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
			"pay_type":"微信支付"
		}
		"""
	When bill使用支付方式'微信支付'进行支付
	Then bill成功创建订单
		"""
		{
			"is_group_buying": "true",
			"status": "待发货",
			"final_price": 20.00,
			"postage": 0.00,
			"products": [{
				"name": "商品1",
				"price": 20.00,
				"count": 1
			}]
		}
		"""

	#bill开团后，就不能重复开一个团购活动
	When bill参加jobs的团购活动"团购1"进行开团:weapp
		"""
		{
			"group_name": "团购1",
			"group_leader": "bill",
			"group_dict":
				{
					"group_type":5,
					"group_days":1,
					"group_price":20.00
				},
			"products": {
				"name": "商品1"
			}
		}
		"""
	Then bill得到团购活动提示"只能开团一次":weapp

@mall3 @nj_group
Scenario: 2 会员可以通过分享链接直接参加团购活动
	bill开团后分享团购活动链接
	1.会员tom可以直接参加团购活动，参加后就不能重复参加，可以开团
	2.非会员nokia通过分享链接能直接参团，不能开团购买

	When bill访问jobs的webapp
	When bill参加jobs的团购活动"团购2"进行开团:weapp
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
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
			"pay_type":"微信支付"
		}
		"""
	When bill使用支付方式'微信支付'进行支付
	Then bill成功创建订单
		"""
		{
			"is_group_buying": "true",
			"status": "待发货",
			"final_price": 21.00,
			"postage": 0.00,
			"products": [{
				"name": "商品2",
				"price": 21.00,
				"count": 1
			}]
		}
		"""

	When bill把jobs的团购活动"团购2"的链接分享到朋友圈:weapp

	#会员打开链接显示-我要参团，看看还有什么团
	When tom访问jobs的webapp
	Then tom能获得bill在"团购2"下的团购活动页面:weapp
		"""
		[{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_price":21.00,
					"offered":[{
						"number":1,
						"member":["bill"]
						}]
				}]
		}]
		"""
	Then tom能获得jobs的参团商品列表:weapp
		"""
		[{
			"group_name": "团购2"
		},{
			"group_name": "团购1"
		}]
		"""
	Then tom能获得"团购2"的已开团活动列表:weapp
		"""
		[{
			"group_name": "团购2",
			"group_leader": "bill",
			"product_name": "商品2",
			"participant_count": "1/5"
		}]
		"""

	#支付完成后跳转到活动详情页显示-邀请好友参团,我要开团
	When tom参加bill的团购活动"团购2":weapp
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
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
			"pay_type":"微信支付"
		}
		"""
	When tom使用支付方式'微信支付'进行支付
	Then tom成功创建订单
		"""
		{
			"is_group_buying": "true",
			"status": "待发货",
			"final_price": 21.00,
			"postage": 0.00,
			"products": [{
				"name": "商品2",
				"price": 21.00,
				"count": 1
			}]
		}
		"""

	Then tom能获得"团购1"的已开团活动列表:weapp
		"""
		[]
		"""
	Then tom能获得"团购2"的已开团活动列表:weapp
		"""
		[]
		"""

	When 清空浏览器:weapp
	When nokia点击bill分享链接:weapp
	When nokia关注jobs的公众号
	When nokia取消关注jobs的公众号
	When nokia访问jobs的webapp
	Then nokia能获得jobs的团购活动列表:weapp
		"""
		[{
			"group_name": "团购2",
			"group_dict":
				[{
					"group_type":"5",
					"group_price":"21.00"
				},{
					"group_type":"10",
					"group_price":"11.00"
				}]
		},{
			"group_name": "团购1",
			"group_dict":
				[{
					"group_type":"5",
					"group_price":"20.00"
				},{
					"group_type":"10",
					"group_price":"10.00"
				}]
		}]
		"""

	#非会员支付完成后跳转二维码引导关注
	When nokia参加bill的团购活动"团购2":weapp
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				},
			"pay_type":"微信支付",
			"products": {
				"name": "商品2"
			}
		}
		"""
	When nokia提交团购订单
		"""
		{
			"ship_name": "nokia",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type":"微信支付"
		}
		"""
	When nokia使用支付方式'微信支付'进行支付
	Then nokia成功创建订单
		"""
		{
			"is_group_buying": "true",
			"status": "待发货",
			"final_price": 21.00,
			"postage": 0.00,
			"products": [{
				"name": "商品2",
				"price": 21.00,
				"count": 1
			}]
		}
		"""

	#非会员不能开团,点击“我要开团”弹出二维码
	Then nokia能获得jobs的团购活动列表:weapp
		"""
		[{
			"group_name": "团购2",
			"group_dict":
				[{
					"group_type":"5",
					"group_price":"21.00"
				},{
					"group_type":"10",
					"group_price":"11.00"
				}]
		},{
			"group_name": "团购1",
			"group_dict":
				[{
					"group_type":"5",
					"group_price":"20.00"
				},{
					"group_type":"10",
					"group_price":"10.00"
				}]
		}]
		"""
	Then nokia能获得"团购1"的已开团活动列表:weapp
		"""
		[]
		"""
	Then nokia能获得"团购2"的已开团活动列表:weapp
		"""
		[]
		"""

@mall3 @nj_group
Scenario: 3 会员开团后团购活动成功
	会员开团后
	1.在活动期内团购人数达到开团人数，团购成功
	2.团购人数达到开团人数，不能再参加此团购

	Given tom1关注jobs的公众号
	And tom2关注jobs的公众号
	And tom3关注jobs的公众号
	And tom4关注jobs的公众号

	#bill参与团购"团购2"开团
	When bill访问jobs的webapp
	When bill参加jobs的团购活动"团购2"进行开团:weapp
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				{
					"group_type":"5",
					"group_days":"1",
					"group_price":"21.00"
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
			"pay_type":"微信支付"
		}
		"""
	When bill使用支付方式'微信支付'进行支付

	#tom参与bill开的团
	When tom访问jobs的webapp
	Then tom能获得"团购2"的已开团活动列表:weapp
		"""
		[{
			"group_name": "团购2",
			"group_leader": "bill",
			"product_name": "商品2",
			"participant_count": "1/5"
		}]
		"""
	When tom参加bill的团购活动"团购2":weapp
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
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
			"pay_type":"微信支付"
		}
		"""
	When tom使用支付方式'微信支付'进行支付

	#tom1参与bill开的团
	When tom1访问jobs的webapp
	Then tom1能获得"团购2"的已开团活动列表:weapp
		"""
		[{
			"group_name": "团购2",
			"group_leader": "bill",
			"product_name": "商品2",
			"participant_count": "2/5"
		}]
		"""
	When tom1参加bill的团购活动"团购2":weapp
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				},
			"products": {
				"name": "商品2"
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
			"pay_type":"微信支付"
		}
		"""
	When tom1使用支付方式'微信支付'进行支付

	#tom2参与bill开的团
	When tom2访问jobs的webapp
	Then tom2能获得"团购2"的已开团活动列表:weapp
		"""
		[{
			"group_name": "团购2",
			"group_leader": "bill",
			"product_name": "商品2",
			"participant_count": "3/5"
		}]
		"""
	When tom2参加bill的团购活动"团购2":weapp
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				},
			"products": {
				"name": "商品2"
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
			"pay_type":"微信支付"
		}
		"""
	When tom2使用支付方式'微信支付'进行支付

	#tom3参与bill开的团
	When tom3访问jobs的webapp
	Then tom3能获得"团购2"的已开团活动列表:weapp
		"""
		[{
			"group_name": "团购2",
			"group_leader": "bill",
			"product_name": "商品2",
			"participant_count": "4/5"
		}]
		"""
	When tom3参加bill的团购活动"团购2":weapp
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				},
			"products": {
				"name": "商品2"
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
			"pay_type":"微信支付"
		}
		"""
	When tom3使用支付方式'微信支付'进行支付
	#Then tom3获得提示信息'恭喜您团购成功 商家将在该商品团购结束20天内进行发货'

	#团购活动达到上限，团购成功，下一个人就不能参加这个活动了
	When tom4访问jobs的webapp
	Then tom4能获得"团购2"的已开团活动列表:weapp
		"""
		[]
		"""

@mall3 @nj_group
Scenario: 4 会员开团后团购活动失败
	会员开团后
	1.没有在期限内达到人数，团购活动失败
	2.结束活动，团购活动失败
	3.团购失败后，用微众卡支付的订单直接返还微众卡
	4.库存恢复

	When bill访问jobs的webapp
	When bill参加jobs的团购活动"团购2"进行开团:weapp
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				},
			"products": {
				"name": "商品2"
			}
		}
		"""
	When bill提交团购订单
		"""
		{
			"order_id":"10086",
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

	When bill进行微众卡余额查询
		"""
		{
			"id":"100000001",
			"password":"1234567"
		}
		"""
	Then bill获得微众卡余额查询结果
		"""
		{
			"card_remaining":79.00
		}
		"""

	#下单成功，库存减少
	Given jobs登录系统:weapp
	Then jobs能获取商品'商品2':weapp
		"""
		{
			"name": "商品2",
			"price": 100.00,
			"weight": 1,
			"stock_type": "有限",
			"stocks": 99,
			"postage": 10.00
		}
		"""
	When jobs关闭团购活动'团购2':weapp

	When bill访问jobs的webapp
	When bill进行微众卡余额查询
		"""
		{
			"id":"100000001",
			"password":"1234567"
		}
		"""
	Then bill获得微众卡余额查询结果
		"""
		{
			"card_remaining":100.00
		}
		"""

	#团购失败，库存恢复
	Given jobs登录系统:weapp
	Then jobs能获取商品'商品2':weapp
		"""
		{
			"name": "商品2",
			"price": 100.00,
			"weight": 1,
			"stock_type": "有限",
			"stocks": 100,
			"postage": 10.00
		}
		"""

	When bill访问jobs的webapp
	Then bill手机端获取订单'10086'
		"""
		{
			"order_no": "10086",
			"status": "已取消"
		}
		"""

@mall3 @nj_group
Scenario: 5 会员开团不进行支付，开团不成功
	会员开团不进行支付，开团不成功
	1.其他会员获取不到参团列表

	When bill访问jobs的webapp
	When bill参加jobs的团购活动"团购2"进行开团:weapp
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				},
			"products": {
				"name": "商品2"
			}
		}
		"""
	When bill提交团购订单
		"""
		{
			"order_id":"001",
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
			"is_group_buying": "true",
			"status": "待支付",
			"final_price": 21.00,
			"postage": 0.00,
			"products": [{
				"name": "商品2",
				"price": 21.00,
				"count": 1
			}]
		}
		"""

	When tom3访问jobs的webapp
	Then tom3能获得"团购2"的已开团活动列表:weapp
		"""
		[]
		"""

@mall3 @nj_group
Scenario: 6 一个会员可以参加多个会员开启的团购活动
	1.一个会员既能开团又能参团，可以参加多个团购活动

	Given tom1关注jobs的公众号
	And tom2关注jobs的公众号
	And tom3关注jobs的公众号

	When bill访问jobs的webapp
	When bill参加jobs的团购活动"团购2"进行开团:weapp
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				},
			"products": {
				"name": "商品2"
			}
		}
		"""
	When bill提交团购订单
		"""
		{
			"order_id":"001",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type":"微信支付"
		}
		"""
	When bill使用支付方式'微信支付'进行支付

	When tom访问jobs的webapp
	When tom参加jobs的团购活动"团购2"进行开团:weapp
		"""
		{
			"group_name": "团购2",
			"group_leader": "tom",
			"group_dict":
				{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				},
			"products": {
				"name": "商品2"
			}
		}
		"""
	When tom提交团购订单
		"""
		{
			"order_id":"002",
			"ship_name": "tom",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type":"微信支付"
		}
		"""
	When tom使用支付方式'微信支付'进行支付

	When tom1访问jobs的webapp
	#参团列表参团人数一样的话以开团时间倒序显示
	Then tom1能获得"团购2"的已开团活动列表:weapp
		"""
		[{
			"group_name": "团购2",
			"group_leader": "bill",
			"product_name": "商品2",
			"participant_count": "1/5"
		},{
			"group_name": "团购2",
			"group_leader": "tom",
			"product_name": "商品2",
			"participant_count": "1/5"
		}]
		"""
	When tom1参加bill的团购活动"团购2":weapp
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				},
			"products": {
				"name": "商品2"
			}
		}
		"""
	When tom1提交团购订单
		"""
		{
			"order_id":"003",
			"ship_name": "tom1",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type":"微信支付"
		}
		"""
	When tom1使用支付方式'微信支付'进行支付
	When tom1参加tom的团购活动"团购2":weapp
		"""
		{
			"group_name": "团购2",
			"group_leader": "tom",
			"group_dict":
				{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				},
			"products": {
				"name": "商品2"
			}
		}
		"""
	When tom1提交团购订单
		"""
		{
			"order_id":"004",
			"ship_name": "tom1",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type":"微信支付"
		}
		"""
	When tom1使用支付方式'微信支付'进行支付

	When tom访问jobs的webapp
	Then tom能获得"团购2"的已开团活动列表:weapp
		"""
		[{
			"group_name": "团购2",
			"group_leader": "bill",
			"product_name": "商品2",
			"participant_count": "2/5"
		}]
		"""
	When tom参加bill的团购活动"团购2":weapp
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				},
			"products": {
				"name": "商品2"
			}
		}
		"""
	When tom提交团购订单
		"""
		{
			"order_id":"005",
			"ship_name": "tom",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type":"微信支付"
		}
		"""
	When tom使用支付方式'微信支付'进行支付

	When tom3访问jobs的webapp
	When tom3参加bill的团购活动"团购2":weapp
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				},
			"products": {
				"name": "商品2"
			}
		}
		"""
	When tom3提交团购订单
		"""
		{
			"order_id":"006",
			"ship_name": "tom3",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type":"微信支付"
		}
		"""
	When tom3使用支付方式'微信支付'进行支付

	When tom2访问jobs的webapp
	#参团列表优先显示拼团人数差一人的团购活动
	Then tom2能获得"团购2"的已开团活动列表:weapp
		"""
		[{
			"group_name": "团购2",
			"group_leader": "bill",
			"product_name": "商品2",
			"participant_count": "4/5"
		},{
			"group_name": "团购2",
			"group_leader": "tom",
			"product_name": "商品2",
			"participant_count": "2/5"
		}]
		"""

@mall3 @nj_group
Scenario: 7 会员把商品添加购物车后，后台把这个商品创建成团购活动
	会员把商品3添加到购物车，后台把商品创建成团购活动
	1.商品3在购物车为失效状态
	2.结束活动后，商品恢复到正常状态

	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品3",
			"count": 1
		}]
		"""
	Then bill能获得购物车
		"""
		{
			"product_groups": [{
				"products": [{
					"name": "商品3",
					"price": 100.00,
					"count": 1
				}]
			}],
			"invalid_products": []
		}
		"""

	Given jobs登录系统:weapp
	When jobs新建团购活动:weapp
		"""
		[{
			"group_name":"团购3",
			"start_date":"今天",
			"end_date":"2天后",
			"product_name":"商品3",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":20.00
				},{
					"group_type":10,
					"group_days":2,
					"group_price":10.00
				}],
				"ship_date":20,
				"product_counts":100,
				"material_image":"1.jpg",
				"share_description":"团购分享描述"
		}]
		"""
	When jobs开启团购活动'团购3':weapp

	When bill访问jobs的webapp
	Then bill能获得购物车
		"""
		{
			"product_groups": [],
			"invalid_products": [{
				"name": "商品3",
				"price": 100.00,
				"count": 1
			}]
		}
		"""

	Given jobs登录系统:weapp
	When jobs关闭团购活动'团购3':weapp

	When bill访问jobs的webapp
	Then bill能获得购物车
		"""
		{
			"product_groups": [{
				"products": [{
					"name": "商品3",
					"price": 100.00,
					"count": 1
				}]
			}],
			"invalid_products": []
		}
		"""





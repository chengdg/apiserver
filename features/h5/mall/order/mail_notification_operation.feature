#author: 王丽 2016-01-14

Feature:运营邮件通知-后台触发
	jobs设定开启运营邮件通知，后台操作订单满足相应的条件，配置的运营邮箱可以收到相应的邮件通知

Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
	Given jobs设定会员积分策略:weapp
		"""
		{
			"integral_each_yuan": 2
		}
		"""
	And jobs已添加支付方式:weapp
		"""
		[{
			"type": "货到付款"
		}, {
			"type": "微信支付"
		}]
		"""
	And jobs已添加商品:weapp
		"""
		[{
			"name": "商品1",
			"price":100.0
		},{
			"name": "商品2",
			"price":100.0
		},{
			"name": "商品3",
			"price":100.0
		},{
			"name": "商品4",
			"price":100.0
		},{
			"name": "赠品",
			"price":10.0
		}]
		"""

	When jobs创建积分应用活动:weapp
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
				"discount_money": 50.0
			}]
		}]
		"""
	When jobs创建买赠活动:weapp
		"""
		[{
			"name": "商品2买一赠一",
			"promotion_title":"",
			"start_date": "今天",
			"end_date": "1天后",
			"member_grade": "普通会员",
			"product_name": "商品2",
			"premium_products": 
			[{
				"name": "赠品",
				"count": 1
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	When jobs创建限时抢购活动:weapp
		"""
		[{
			"name": "商品3限时抢购",
			"promotion_title":"",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name":"商品3",
			"member_grade": "全部会员",
			"count_per_purchase": 2,
			"promotion_price": 50.00,
			"limit_period": 1
		}]
		"""
	Given jobs已添加了优惠券规则:weapp
		"""
		[{
			"name": "单品券4",
			"money": 50,
			"start_date": "今天",
			"end_date": "2天后",
			"coupon_id_prefix": "coupon1_id_",
			"coupon_product": "商品4"
		},{
			"name": "全体券",
			"money": 100,
			"start_date": "今天",
			"end_date": "2天后",
			"coupon_id_prefix": "coupon2_id_"
		}]
		"""
	And jobs初始化邮件通知:weapp
	Given bill关注jobs的公众号
	Given tom关注jobs的公众号

	Given jobs登录系统:weapp
	When jobs为会员发放优惠券:weapp
		"""
		{
			"name": "单品券4",
			"count": 1,
			"members": ["tom"]
		}
		"""
	When jobs为会员发放优惠券:weapp
		"""
		{
			"name": "全体券",
			"count": 1,
			"members": ["bill"]
		}
		"""

@configuration @mail
Scenario:1 启用"付款时"邮件通知
	#1 bill购买单个商品（积分活动）；配置运营接收邮件，可以正确只收到一次邮件通知
	#2 tom购买多个商品（买赠、限时抢购、优惠券）；配置运营接收邮件，可以正确只收到一次邮件通知
	
	Given jobs登录系统:weapp
	When jobs配置'付款时'邮件通知:weapp
		"""
		{
			"emails":"ceshi@weizoom.com",
			"member_ids":""
		}
		"""
	When jobs启用'付款时'邮件通知:weapp
	#购买单个商品（积分活动），成功下单
		When bill访问jobs的webapp
		When bill获得jobs的200会员积分
		When bill购买jobs的商品
			"""
			{
				"order_id":"0000001",
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type": "微信支付",
				"products": [{
					"name": "商品1",
					"count": 1,
					"integral": 100,
					"integral_money":50.00
				}]
			}
			"""
		Then bill成功创建订单
			"""
			{
				"order_no":"0000001",
				"status": "待支付",
				"final_price": 50.0,
				"product_price": 100.00,
				"integral": 100,
				"integral_money":50.00,
				"products": [{
					"name": "商品1",
					"count": 1
				}]
			}
			"""
		Given jobs登录系统:weapp
		When jobs'支付'订单'0000001':weapp

		Then server能发送邮件
			"""
			{
				"content":{
					"buyer_name": "bill",
					"product_name":"商品1",
					"order_status":"待发货",
					"buy_count":"1",
					"total_price":50.0,
					"integral":100,
					"ship_name":"bill",
					"ship_tel": "13811223344",
					"buyer_address":"北京市 北京市 海淀区 泰兴大厦"
				},
				"mails":"ceshi@weizoom.com"
			}
			"""

	#购买多个商品（买赠、限时抢购、优惠券），成功下单
		When tom访问jobs的webapp
		When tom购买jobs的商品
			"""
			{
				"order_id":"0000002",
				"ship_name": "tom",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type": "微信支付",
				"products": [{
					"name": "商品2",
					"count": 1
				},{
					"name": "商品3",
					"count": 2
				},{
					"name": "商品4",
					"count": 1
				}],
				"coupon": "coupon1_id_1"
			}
			"""
		Then tom成功创建订单
			"""
			{
				"order_no":"0000002",
				"status": "待支付",
				"final_price": 250.0,
				"products": [{
					"name": "商品2",
					"count": 1,
					"promotion": {
						"type": "premium_sale"
					}
				},{
					"name": "赠品",
					"count": 1,
					"promotion": {
						"type": "premium_sale:premium_product"
					}
				},{
					"name": "商品3",
					"count": 2
				},{
					"name": "商品4",
					"count": 1
				}],
				"coupon_money": 50.0
			}
			"""
		Given jobs登录系统:weapp
		When jobs'支付'订单'0000002':weapp
		Then server能发送邮件
			"""
			{
				"content":{
					"buyer_name": "tom",
					"product_name":"商品2,商品3,商品4",
					"order_status":"待发货",
					"buy_count":"1,2,1",
					"total_price":250.0,
					"coupon":"coupon1_id_1,￥50.0",
					"ship_name":"bill",
					"ship_tel": "13811223344",
					"buyer_address":"北京市 北京市 海淀区 泰兴大厦"

				},
				"mails":"ceshi@weizoom.com"
			}
			"""

@configuration @mail
Scenario:2 启用"取消时"邮件通知
	#1 bill购买单个商品（积分活动）；配置运营接收邮件，可以正确只收到一次邮件通知
	#2 tom购买多个商品（买赠、限时抢购、优惠券）；配置运营接收邮件，可以正确只收到一次邮件通知

	Given jobs登录系统:weapp
	When jobs配置'取消时'邮件通知:weapp
		"""
		{
			"emails":"ceshi@weizoom.com",
			"member_ids":""
		}
		"""
	When jobs启用'取消时'邮件通知:weapp
	#购买单个商品（积分活动），成功下单
		When bill访问jobs的webapp
		When bill获得jobs的200会员积分
		When bill购买jobs的商品
			"""
			{
				"order_id":"0000001",
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type": "微信支付",
				"products": [{
					"name": "商品1",
					"count": 1,
					"integral": 100,
					"integral_money":50.00
				}]
			}
			"""
		Then bill成功创建订单
			"""
			{
				"order_no":"0000001",
				"status": "待支付",
				"final_price": 50.0,
				"product_price": 100.00,
				"integral": 100,
				"integral_money":50.00,
				"products": [{
					"name": "商品1",
					"count": 1
				}]
			}
			"""
		Given jobs登录系统:weapp
		When jobs取消订单'0000001'

		Then server能发送邮件
			"""
			{
				"content":{
					"buyer_name": "bill",
					"product_name":"商品1",
					"order_status":"已取消",
					"buy_count":"1",
					"total_price":50.0,
					"integral":100,
					"ship_name":"bill",
					"ship_tel": "13811223344",
					"buyer_address":"北京市 北京市 海淀区 泰兴大厦"
				},
				"mails":"ceshi@weizoom.com"
			}
			"""
	#购买多个商品（买赠、限时抢购、优惠券），成功下单
		When 清空浏览器:weapp
		When tom访问jobs的webapp
		When tom购买jobs的商品
			"""
			{
				"order_id":"0000002",
				"ship_name": "tom",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type": "微信支付",
				"products": [{
					"name": "商品2",
					"count": 1
				},{
					"name": "商品3",
					"count": 2
				},{
					"name": "商品4",
					"count": 1
				}],
				"coupon": "coupon1_id_1"
			}
			"""
		Then tom成功创建订单
			"""
			{
				"order_no":"0000002",
				"status": "待支付",
				"final_price": 250.0,
				"products": [{
					"name": "商品2",
					"count": 1,
					"promotion": {
						"type": "premium_sale"
					}
				},{
					"name": "赠品",
					"count": 1,
					"promotion": {
						"type": "premium_sale:premium_product"
					}
				},{
					"name": "商品3",
					"count": 2
				},{
					"name": "商品4",
					"count": 1
				}],
				"coupon_money": 50.0
			}
			"""
		When tom使用支付方式'微信支付'进行支付
		Given jobs登录系统:weapp
		When jobs取消订单'0000002':weapp

		Then server能发送邮件
			"""
			{
				"content":{
					"buyer_name": "tom",
					"product_name":"商品2,商品3,商品4",
					"order_status":"已取消",
					"buy_count":"1,2,1",
					"total_price":250.0,
					"coupon":"coupon1_id_1,￥50.0",					
					"ship_name":"tom",
					"ship_tel": "13811223344",
					"buyer_address":"北京市 北京市 海淀区 泰兴大厦"

				},
				"mails":"ceshi@weizoom.com"
			}
			"""
	#购买单个商品（积分活动），成功下单，优惠券抵扣的订单，订单完成后取消
		When bill访问jobs的webapp
		When bill获得jobs的200会员积分
		When bill购买jobs的商品
			"""
			{
				"order_id":"0000003",
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type": "微信支付",
				"products": [{
					"name": "商品1",
					"count": 1
				}],
				"coupon": "coupon2_id_1"
			}
			"""
		Then bill成功创建订单
			"""
			{
				"order_no":"0000003",
				"status": "待发货",
				"final_price": 0.00,
				"product_price": 100.00,
				"products": [{
					"name": "商品1",
					"count": 1
				}],
				"coupon_money": 100.00
			}
			"""
		Given jobs登录系统:weapp
		When jobs对订单进行发货:weapp
			"""
			{
				"order_no":"0000003",
				"logistics":"顺丰速运",
				"number":"123456789"
			}
			"""
		When jobs完成订单'0000003':weapp
		When jobs取消订单'0000003'

		Then server能发送邮件
			"""
			{
				"content":{
					"buyer_name": "bill",
					"product_name":"商品1",
					"order_status":"已取消",
					"buy_count":"1",
					"total_price":0.0,
					"coupon":"coupon2_id_1,￥100.0",	
					"ship_name":"bill",
					"ship_tel": "13811223344",
					"buyer_address":"北京市 北京市 海淀区 泰兴大厦"
				},
				"mails":"ceshi@weizoom.com"
			}
			"""

@configuration @mail
Scenario:3 启用"发货时"邮件通知
	#1 bill购买单个商品（积分活动）；配置运营接收邮件，可以正确只收到一次邮件通知
	#2 tom购买多个商品（买赠、限时抢购、优惠券）；配置运营接收邮件，可以正确只收到一次邮件通知

	Given jobs登录系统:weapp
	When jobs配置'发货时'邮件通知:weapp
		"""
		{
			"emails":"ceshi@weizoom.com",
			"member_ids":""
		}
		"""
	When jobs启用'发货时'邮件通知:weapp
	#购买单个商品（积分活动），成功下单
		When bill访问jobs的webapp
		When bill获得jobs的200会员积分
		When bill购买jobs的商品
			"""
			{
				"order_id":"0000001",
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type": "货到付款",
				"products": [{
					"name": "商品1",
					"count": 1,
					"integral": 100,
					"integral_money":50.00
				}]
			}
			"""
		Then bill成功创建订单
			"""
			{
				"order_no":"0000001",
				"status": "待发货",
				"final_price": 50.0,
				"product_price": 100.00,
				"integral": 100,
				"integral_money":50.00,
				"products": [{
					"name": "商品1",
					"count": 1
				}]
			}
			"""
		Given jobs登录系统:weapp
		When jobs对订单进行发货:weapp
			"""
			{
				"order_no":"0000001",
				"logistics":"顺丰速运",
				"number":"123456789"
			}
			"""

		Then server能发送邮件
			"""
			{
				"content":{
					"buyer_name": "bill",
					"product_name":"商品1",
					"order_status":"已发货",
					"buy_count":"1",
					"total_price":50.0,
					"integral":100,
					"ship_name":"bill",
					"ship_tel": "13811223344",
					"buyer_address":"北京市 北京市 海淀区 泰兴大厦"
				},
				"mails":"ceshi@weizoom.com"
			}
			"""
	#购买多个商品（买赠、限时抢购、优惠券），成功下单
		When tom访问jobs的webapp
		When tom购买jobs的商品
			"""
			{
				"order_id":"0000002",
				"ship_name": "tom",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type": "微信支付",
				"products": [{
					"name": "商品2",
					"count": 1
				},{
					"name": "商品3",
					"count": 2
				},{
					"name": "商品4",
					"count": 1
				}],
				"coupon": "coupon1_id_1"
			}
			"""
		Then tom成功创建订单
			"""
			{
				"order_no":"0000002",
				"status": "待支付",
				"final_price": 250.0,
				"products": [{
					"name": "商品2",
					"count": 1,
					"promotion": {
						"type": "premium_sale"
					}
				},{
					"name": "赠品",
					"count": 1,
					"promotion": {
						"type": "premium_sale:premium_product"
					}
				},{
					"name": "商品3",
					"count": 2
				},{
					"name": "商品4",
					"count": 1
				}],
				"coupon_money": 50.0
			}
			"""
		When tom使用支付方式'微信支付'进行支付
		Given jobs登录系统:weapp
		When jobs对订单进行发货:weapp
			"""
			{
				"order_no":"0000002",
				"logistics":"顺丰速运",
				"number":"123456789"
			}
			"""

		Then server能发送邮件
			"""
			{
				"content":{
					"buyer_name": "tom",
					"product_name":"商品2,商品3,商品4",
					"order_status":"已发货",
					"buy_count":"1,2,1",
					"total_price":250.0,
					"coupon":"coupon1_id_1,￥50.0",
					"ship_name":"tom",
					"ship_tel": "13811223344",
					"buyer_address":"北京市 北京市 海淀区 泰兴大厦"

				},
				"mails":"ceshi@weizoom.com"
			}
			"""

@configuration @mail
Scenario:4 启用"完成时"邮件通知
	#1 bill购买单个商品（积分活动）；配置运营接收邮件，可以正确只收到一次邮件通知
	#2 tom购买多个商品（买赠、限时抢购、优惠券）；配置运营接收邮件，可以正确只收到一次邮件通知

	Given jobs登录系统:weapp
	When jobs配置'完成时'邮件通知:weapp
		"""
		{
			"emails":"ceshi@weizoom.com",
			"member_ids":""
		}
		"""
	When jobs启用'完成时'邮件通知:weapp
	#购买单个商品（积分活动），成功下单
		When bill访问jobs的webapp
		When bill获得jobs的200会员积分
		When bill购买jobs的商品
			"""
			{
				"order_id":"0000001",
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type": "货到付款",
				"products": [{
					"name": "商品1",
					"count": 1,
					"integral": 100,
					"integral_money":50.00
				}]
			}
			"""
		Then bill成功创建订单
			"""
			{
				"order_no":"0000001",
				"status": "待发货",
				"final_price": 50.0,
				"product_price": 100.00,
				"integral": 100,
				"integral_money":50.00,
				"products": [{
					"name": "商品1",
					"count": 1
				}]
			}
			"""
		Given jobs登录系统:weapp
		When jobs对订单进行发货:weapp
			"""
			{
				"order_no":"0000001",
				"logistics":"顺丰速运",
				"number":"123456789"
			}
			"""
		When jobs完成订单'0000001':weapp

		Then server能发送邮件
			"""
			{
				"content":{
					"buyer_name": "bill",
					"product_name":"商品1",
					"order_status":"已完成",
					"buy_count":"1",
					"total_price":50.0,
					"integral":100,
					"ship_name":"bill",
					"ship_tel": "13811223344",
					"buyer_address":"北京市 北京市 海淀区 泰兴大厦"

				},
				"mails":"ceshi@weizoom.com"
			}
			"""
	#购买多个商品（买赠、限时抢购、优惠券），成功下单
		When tom访问jobs的webapp
		When tom购买jobs的商品
			"""
			{
				"order_id":"0000002",
				"ship_name": "tom",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type": "微信支付",
				"products": [{
					"name": "商品2",
					"count": 1
				},{
					"name": "商品3",
					"count": 2
				},{
					"name": "商品4",
					"count": 1
				}],
				"coupon": "coupon1_id_1"
			}
			"""
		Then tom成功创建订单
			"""
			{
				"order_no":"0000002",
				"status": "待支付",
				"final_price": 250.0,
				"products": [{
					"name": "商品2",
					"count": 1,
					"promotion": {
						"type": "premium_sale"
					}
				},{
					"name": "赠品",
					"count": 1,
					"promotion": {
						"type": "premium_sale:premium_product"
					}
				},{
					"name": "商品3",
					"count": 2
				},{
					"name": "商品4",
					"count": 1
				}],
				"coupon_money": 50.0
			}
			"""
		When tom使用支付方式'微信支付'进行支付
		Given jobs登录系统:weapp
		When jobs对订单进行发货:weapp
			"""
			{
				"order_no":"0000002",
				"logistics":"顺丰速运",
				"number":"123456789"
			}
			"""
		When jobs完成订单'0000002':weapp

		Then server能发送邮件
			"""
			{
				"content":{
					"buyer_name": "tom",
					"product_name":"商品2,商品3,商品4",
					"order_status":"已完成",
					"buy_count":"1,2,1",
					"total_price":250.0,
					"coupon":"coupon1_id_1,￥50.0",
					"ship_name":"tom",
					"ship_tel": "13811223344",
					"buyer_address":"北京市 北京市 海淀区 泰兴大厦"
					"buyer_address":"北京市 北京市 海淀区 泰兴大厦"

				},
				"mails":"ceshi@weizoom.com"
			}
			"""

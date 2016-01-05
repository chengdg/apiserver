#_author_:张三香 2015.01.05

Feature:校验后台所有订单列表页的订单总数

Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
	Given jobs已添加商品分类:weapp
		"""
		[{
			"name": "分类1"
		}, {
			"name": "分类2"
		}, {
			"name": "分类3"
		}]
		"""
	And jobs已有微众卡支付权限:weapp
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
	And jobs已添加商品规格:weapp
		"""
		[{
			"name": "颜色",
			"type": "图片",
			"values": [{
				"name": "黑色",
				"image": "/standard_static/test_resource_img/hangzhou1.jpg"
			}, {
				"name": "白色",
				"image": "/standard_static/test_resource_img/hangzhou2.jpg"
			}]
		}, {
			"name": "尺寸",
			"type": "文字",
			"values": [{
				"name": "M"
			}, {
				"name": "S"
			}]
		}]
		"""
	And jobs已添加商品:weapp
		"""
		[{
			"name": "商品1",
			"price": 9.9
		}, {
			"name": "商品2",
			"price": 8.8
		},{
			"name": "商品3",
			"is_enable_model": "启用规格",
			"model": {
				"models": {
					"黑色 M": {
						"price": 10.0
					}
				}
			}
		}, {
			"name": "商品4",
			"model": {
				"models": {
					"standard": {
						"price": 5.0,
						"stock_type": "有限",
						"stocks": 10
					}
				}
			}
		}]
		"""
	And bill关注jobs的公众号
	And tom关注jobs的公众号

	#构造订单数据
	#待支付订单-001
		When bill访问jobs的webapp
		And bill购买jobs的商品
			"""
			{
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付",
				"order_id":"001",
				"products": [{
					"name": "商品1",
					"count": 2
				}]
			}
			"""
	#待发货订单-002
		When bill访问jobs的webapp
		And bill购买jobs的商品
			"""
			{
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"货到付款",
				"order_id":"002",
				"products": [{
					"name": "商品2",
					"count": 1
				}]
			}
			"""
	#已取消订单-003
		When bill访问jobs的webapp
		And bill购买jobs的商品
			"""
			{
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付",
				"order_id":"003",
				"products": [{
					"name": "商品3",
					"model":"黑色 M",
					"count": 2
				}]
			}
			"""
		When bill取消订单'003'
	#已发货订单-004
		When bill访问jobs的webapp
		And bill购买jobs的商品
			"""
			{
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"货到付款",
				"order_id":"004",
				"products": [{
					"name": "商品1",
					"count": 4
				}]
			}
			"""
	#已完成订单-005
		When tom访问jobs的webapp
		And tom购买jobs的商品
			"""
			{
				"ship_name": "tom",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"货到付款",
				"order_id":"005",
				"products": [{
					"name": "商品1",
					"count": 2
				}]
			}
			"""
	#退款中订单-006
		When tom访问jobs的webapp
		And tom购买jobs的商品
			"""
			{
				"ship_name": "tom",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付",
				"order_id":"006",
				"products": [{
					"name": "商品1",
					"count": 2
				}]
			}
			"""
		When tom使用支付方式'微信支付'进行支付
	#退款完成订单-007
		When tom访问jobs的webapp
		And tom购买jobs的商品
			"""
			{
				"ship_name": "tom",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付",
				"order_id":"007",
				"products": [{
					"name": "商品1",
					"count": 2
				}]
			}
			"""
		When tom使用支付方式'微信支付'进行支付

	Given jobs登录系统:weapp
	When jobs对订单进行发货:weapp
		"""
		{
			"order_no":"004",
			"logistics":"顺丰速运",
			"number":"123456789",
			"shipper":"jobs",
			"date":"今天"
		}
		"""
	When jobs对订单进行发货:weapp
		"""
		{
			"order_no":"005",
			"logistics":"顺丰速运",
			"number":"123456789",
			"shipper":"jobs",
			"date":"今天"
		}
		"""
	When jobs'完成'订单'005':weapp

	When jobs对订单进行发货:weapp
		"""
		{
			"order_no":"006",
			"logistics":"顺丰速运",
			"number":"123456789",
			"shipper":"jobs",
			"date":"今天"
		}
		"""
	When jobs'完成'订单'006':weapp
	When jobs'申请退款'订单'006':weapp

	When jobs对订单进行发货:weapp
		"""
		{
			"order_no":"007",
			"logistics":"顺丰速运",
			"number":"123456789",
			"shipper":"jobs",
			"date":"今天"
		}
		"""
	When jobs'完成'订单'007':weapp
	When jobs'申请退款'订单'007':weapp
	When jobs通过财务审核'退款成功'订单'007':weapp

@mall3 @order @zr @ztq
Scenario:1 校验后台订单列表的所有订单数
	Given jobs登录系统:weapp
	Then jobs获得订单列表筛选结果:weapp
		"""
		{
			"total_orders_count":7
		}
		"""
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"order_id":"008",
			"pay_type":"微信支付",
			"products": [{
				"name": "商品1",
				"count": 2
			}],
			"ship_area": "北京市 北京市 海淀区",
			"customer_message": "bill的订单备注"
		}
		"""

	Given jobs登录系统:weapp
	Then jobs获得订单列表筛选结果:weapp
		"""
		{
			"total_orders_count":8
		}
		"""






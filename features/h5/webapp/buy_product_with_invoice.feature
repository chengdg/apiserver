# watcher: zhangsanxiang@weizoom.com, benchi@weizoom.com
#_author_:张三香 2016.01.20

Feature:购买支持开票的商品
	"""
	1.只要订单中含有支持开票的商品，手机端结算页就展示该发票选项
	2.发票类型选择'个人'时，手机端订单详情页发票信息显示：
		发票抬头：个人 xx
	3.发票类型选择'单位'时,手机端订单详情页发票信息显示：
		发票抬头:公司 XXXXXXX(公司名称)
	"""

Background:
	Given 重置'weapp'的bdd环境
	Given jobs登录系统::weapp
	And jobs已添加商品分类::weapp
		"""
		[{
			"name": "分类1"
		}, {
			"name": "分类2"
		}, {
			"name": "分类3"
		}]
		"""
	And jobs已添加商品规格::weapp
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
	When jobs已添加支付方式::weapp
		"""
		[{
			"type": "货到付款",
			"is_active": "启用"
		},{
			"type": "微信支付",
			"is_active": "启用"
		},{
			"type": "支付宝",
			"is_active": "启用"
		}]
		"""
	And jobs已添加商品::weapp
		"""
		[{
			"name": "支持开票1",
			"category": "分类1",
			"detail": "商品1的详情",
			"status": "在售",
			"invoice":true,
			"model": {
					"models": {
						"standard": {
							"price": 10.00,
							"weight": 1.0,
							"stock_type": "有限",
							"stocks": 3
						}
					}
				}
			},{
				"name": "支持开票2",
				"is_enable_model": "启用规格",
				"invoice":true,
				"model": {
					"models": {
						"黑色 S": {
							"price": 20.00,
							"weight": 3.1,
							"stock_type": "有限",
							"stocks": 3
						},
						"白色 S": {
							"price": 20.00,
							"weight": 1.0,
							"stock_type": "无限"
						}
					}
				}
		},{
			"name": "不支持开票3",
			"category": "分类2",
			"detail": "商品3的详情",
			"status": "在售",
			"invoice":false,
			"model": {
					"models": {
						"standard": {
							"price": 30.00,
							"weight": 1.0,
							"stock_type": "有限",
							"stocks": 3
						}
					}
				}
		}]
		"""
	And bill关注jobs的公众号

@mall3
Scenario:1 购买单个支持开发票的商品，选择'个人'发票
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"order_id":"001",
			"pay_type":"微信支付",
			"invoice":{
					"type":"个人",
					"value":"李李"
				},
			"products": [{
				"name": "支持开票1",
				"count": 1
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 10.00,
			"products": [{
				"name": "支持开票1",
				"price": 10.00,
				"count": 1
			}]
		}
		"""
	When bill访问jobs的webapp
	Then bill手机端获取订单'001'
		"""
		{
			"order_no": "001",
			"status":"待支付",
			"methods_of_payment":"微信支付",
			"invoice":{
					"type":"个人",
					"value":"李李"
				},
			"final_price": 10.00,
			"products": [{
				"name": "支持开票1",
				"price": 10.00,
				"count": 1
			}]
		}
		"""

@mall3
Scenario:2 购买多个支持开发票的商品,选择'单位'发票
	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "支持开票1",
			"count": 1
		},{
			"name": "支持开票2",
			"model": {
				"models":{
					"黑色 S": {
						"count": 1
					}
				}
			}
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"context": [{
					"name": "支持开票1"
				},{
					"name": "支持开票2",
					"model": "黑色,S"
			}]
		}
		"""
	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款",
			"invoice":{
					"type":"单位",
					"value":"北京微众文化传媒有限公司"
				}
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待发货",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 30.00,
			"products": [{
				"name": "支持开票1",
				"price": 10.00,
				"count": 1
			},{
				"name": "支持开票2",
				"price": 20.00,
				"model": "黑色 S",
				"count": 1
			}]
		}
		"""

@mall3
Scenario:3 购买支持开发票和不支持开发票的商品
	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "支持开票1",
			"count": 1
		},{
			"name": "支持开票2",
			"model": {
				"models":{
					"黑色 S": {
						"count": 1
					}
				}
			}
		},{
			"name": "不支持开票3",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"context": [{
					"name": "支持开票1"
				},{
					"name": "支持开票2",
					"model":"黑色,S"
				},{
					"name": "不支持开票3"
			}]
		}
		"""
	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款",
			"invoice":{
					"type":"单位",
					"value":"北京微众文化传媒有限公司"
				}
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待发货",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 60.00,
			"products": [{
				"name": "支持开票1",
				"price": 10.00,
				"count": 1
			},{
				"name": "支持开票2",
				"price": 20.00,
				"model":"黑色 S",
				"count": 1
			},{
				"name": "不支持开票3",
				"price": 30.00,
				"count": 1
			}]
		}
		"""
# watcher: zhangsanxiang@weizoom.com, benchi@weizoom.com
#_author_:张三香 2016.01.21

Feature: 购买有配送时间的商品

Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
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
			"name": "配送商品1",
			"shelve_type": "上架",
			"model": {
				"models": {
					"standard": {
						"price": 10.0,
						"weight": 5.5,
						"stock_type": "有限",
						"stocks": 3
					}
				}
			},
			"distribution_time":"on"
		},{
			"name": "配送商品2",
			"shelve_type": "上架",
			"distribution_time":"on",
			"is_enable_model": "启用规格",
			"model": {
				"models": {
					"黑色 S": {
						"price": 20.0,
						"weight": 3.1,
						"stock_type": "有限",
						"stocks": 3
					},
					"白色 S": {
						"price": 20.0,
						"weight": 1.0,
						"stock_type": "无限"
					}
				}
			}
		},{
			"name": "不配送商品3",
			"shelve_type": "上架",
			"distribution_time":"off",
			"model": {
				"models": {
					"standard": {
						"price": 30.0,
						"weight": 5.5,
						"stock_type": "有限",
						"stocks": 3
					}
				}
			}
		}]
		"""
	And jobs已添加支付方式:weapp
		"""
		[{
			"type": "微信支付"
		},{
			"type": "货到付款"
		}]
		"""
	And bill关注jobs的公众号
@mall3
Scenario:1 购买单个有配送时间的商品,订单状态为'待支付'
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"001",
			"pay_type": "微信支付",
			"distribution_time":"5天后 10:00-12:30",
			"products":[{
				"name":"配送商品1",
				"price":10.00,
				"count":1
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 10.00,
			"products": [{
				"name": "配送商品1",
				"price": 10.00,
				"count": 1
			}]
		}
		"""
@mall3
Scenario:2 购买多个有配送时间的商品,订单状态为'待发货'
	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "配送商品1",
			"count": 1
		},{
			"name": "配送商品2",
			"model": {
				"models":{
					"黑色 S": {
						"count": 1
					}
				}
			}
		},{
			"name": "配送商品2",
			"model": {
				"models":{
					"白色 S": {
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
					"name": "配送商品1"
				},{
					"name": "配送商品2",
					"model":"黑色,S"
				},{
					"name": "配送商品2",
					"model":"白色,S"
			}]
		}
		"""
	And bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款",
			"distribution_time":"10天后 10:00-12:30"
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
			"final_price": 50.0,
			"products": [{
				"name": "配送商品1",
				"price": 10.0,
				"count": 1
			},{
				"name": "配送商品2",
				"price": 20.0,
				"model": "黑色 S",
				"count": 1
			},{
				"name": "配送商品2",
				"price": 20.0,
				"model": "白色 S",
				"count": 1
			}]
		}
		"""
@mall3
Scenario:3 购买有配送时间和没有配送时间的商品,订单状态为'待发货'
	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "配送商品1",
			"count": 1
		},{
			"name": "不配送商品3",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"context": [{
					"name": "配送商品1"
				},{
					"name": "不配送商品3"
			}]
		}
		"""
	And bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款",
			"distribution_time":"10天后 10:00-12:30"
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
			"final_price": 40.0,
			"products": [{
				"name": "配送商品1",
				"price": 10.0,
				"count": 1
			},{
				"name": "不配送商品3",
				"price": 30.0,
				"count": 1
			}]
		}
		"""

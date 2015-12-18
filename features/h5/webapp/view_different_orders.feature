#_author_:bc 2015.12.18

Feature:从个人中心浏览不同状态的订单列表
	"""
		
	"""

Background:
	Given jobs登录系统
	And jobs已有微众卡支付权限
	And jobs已添加支付方式
		"""
		[{
			"type": "微众卡支付"
		}, {
			"type": "货到付款"
		}, {
			"type": "微信支付"
		}]
		"""
	And jobs已添加商品规格
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
	And jobs已添加商品
		"""
		[{
			"name": "商品1",
			"price":10.0
		}, {
			"name": "商品2",
			"price": 20.0
		},{
			"name": "商品3",
			"is_enable_model": "启用规格",
			"model": {
				"models": {
					"黑色 M": {
						"price": 30.0
					}
				}
			}
		}, {
			"name": "商品4",
			"model": {
				"models": {
					"standard": {
						"price": 40.0,
						"stock_type": "有限",
						"stocks": 2
					}
				}
			}
		}, {
			"name": "商品5",
			"price": 50.0,
			"pay_interfaces":[{
				"type": "在线支付"
			}]
		}]
		"""
	And bill关注jobs的公众号

	#构造订单数据
	When bill访问jobs的webapp
	#待支付订单
	And bill购买jobs的商品
		"""
		{
			"order_id":"001",
			"pay_type":"微信支付",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""

		And bill购买jobs的商品
		"""
		{
			"order_id":"002",
			"pay_type":"微信支付",
			"products": [{
				"name": "商品2",
				"count": 2
			}]
		}
		"""

	#待发货订单
	And bill购买jobs的商品
		"""
		{
			"order_id":"003",
			"pay_type":"货到付款",
			"products": [{
				"name": "商品1",
				"count": 1
			}, {
				"name": "商品2",
				"count": 1
			}, {
				"name": "商品3",
				"model": "黑色 M",
				"count": 1
			}]
		}
		"""

	#待收货订单
	And bill购买jobs的商品
		"""
		{
			"order_id":"004",
			"pay_type": "货到付款",
			"products": [{
				"name": "商品2",
				"count": 1
			},{
				"name": "商品4",
				"count": 1
			}]
		}
		"""

	

@personCenter @appallOrder @todo
Scenario:1 会员通过个人中心的'待支付',浏览订单列表信息
	When bill访问jobs的webapp
	And bill访问个人中心
	Then bill查看个人中心'待支付'订单列表
		"""
		[{
			"status": "待支付",
			"created_at": "今天",
			"products": [{
				"name": "商品2"
			}],
			"counts": 2,
			"final_price": 40.00,
			"actions": ["取消订单", "支付"]
		},{
			"status": "待支付",
			"created_at": "今天",
			"products": [{
				"name": "商品1"
			}],
			"counts": 2,
			"final_price": 40.00,
			"actions": ["取消订单", "支付"]
		}]
		"""

	

@personCenter @appallOrder @todo
Scenario:2 会员通过个人中心的'待发货',浏览订单列表信息
	When bill访问jobs的webapp
	And bill访问个人中心
	Then bill查看个人中心'待发货'订单列表
		"""
		[{
			"status": "待发货",
			"created_at": "今天",
			"products": [{
				"name": "商品1"
			},{
				"name": "商品2"
			},{
				"name": "商品2",
				"model": "黑色 M"
			}],
			"counts": 3,
			"final_price": 60.00
		}]
		"""

	

@personCenter @appallOrder @todo
Scenario:3 会员通过个人中心的'待收货',浏览订单列表信息
	When bill访问jobs的webapp
	And bill访问个人中心
	Then bill查看个人中心'待收货'订单列表
		"""
		[{
			"status": "待收货",
			"created_at": "今天",
			"products": [{
				"name": "商品2"
			},{
				"name": "商品4"
			}],
			"counts": 2,
			"final_price": 60.00,
			"actions": ["查看物流"]
		}]
		"""

	

@personCenter @appallOrder @todo
Scenario:4 会员通过个人中心的'全部订单',浏览订单列表信息
	When bill访问jobs的webapp
	And bill访问个人中心
	Then bill查看个人中心'全部订单列表'订单列表
		"""
		[{
			"status": "已取消",
			"created_at": "今天",
			"products": [{
				"name": "商品1"
			}],
			"counts": 1,
			"final_price": 10.00
		},{
			"status": "待收货",
			"created_at": "今天",
			"products": [{
				"name": "商品2"
			},{
				"name": "商品4"
			}],
			"counts": 2,
			"final_price": 60.00,
			"actions": ["查看物流"]
		},{
			"status": "待发货",
			"created_at": "今天",
			"products": [{
				"name": "商品1"
			},{
				"name": "商品2"
			},{
				"name": "商品2",
				"model": "黑色 M"
			}],
			"counts": 3,
			"final_price": 60.00
		},{
			"status": "待支付",
			"created_at": "今天",
			"products": [{
				"name": "商品2"
			}],
			"counts": 2,
			"final_price": 40.00,
			"actions": ["取消订单", "支付"]
		},{
			"status": "待支付",
			"created_at": "今天",
			"final_price": 10.00,
			"products": [{
				"name": "商品1"
			}],
			"counts": 1,
			"final_price": 20.00,
			"actions": ["取消订单", "支付"]
		}]
		"""

	

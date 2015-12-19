# #_author_:张三香 2015.12.15

# Feature:从个人中心浏览不同状态的订单列表
# 	"""
# 		说明：
# 		1.手机端有4个页面显示会员的订单列表信息,只是页面标题和默认进入页面时显示的内容不同

# 		2.下面4个页面中均包含：全部订单、待支付、待发货、待收货4个页签
# 			a.'全部订单列表'页面:
# 				进入方式:从'个人中心'点击'全部订单'进入
# 				显示：默认显示'全部订单'页签的列表信息，可以在4个页签中进行切换，但页面标题不变

# 			b.'待支付'页面：
# 				进入方式:从'个人中心'点击'待支付'进入
# 				显示：默认显示'待支付'页签的订单列表信息，可以在4个页签中进行切换，但页面标题不变

# 			c.'待发货'页面：
# 				进入方式:从'个人中心'点击'待发货'进入
# 				显示：默认显示'待发货'页签的订单列表信息，可以在4个页签中进行切换，但页面标题不变

# 			d.'待收货'页面:
# 				进入方式:从'个人中心'点击'待收货'进入
# 				显示：默认显示'待收货'页签的订单列表信息，可以在4个页签中进行切换，但页面标题不变
# 	"""

# Background:
# 	Given jobs登录系统
# 	And jobs已有微众卡支付权限
# 	And jobs已添加支付方式
# 		"""
# 		[{
# 			"type": "微众卡支付"
# 		}, {
# 			"type": "货到付款"
# 		}, {
# 			"type": "微信支付"
# 		}]
# 		"""
# 	And jobs已添加商品规格
# 		"""
# 		[{
# 			"name": "颜色",
# 			"type": "图片",
# 			"values": [{
# 				"name": "黑色",
# 				"image": "/standard_static/test_resource_img/hangzhou1.jpg"
# 			}, {
# 				"name": "白色",
# 				"image": "/standard_static/test_resource_img/hangzhou2.jpg"
# 			}]
# 		}, {
# 			"name": "尺寸",
# 			"type": "文字",
# 			"values": [{
# 				"name": "M"
# 			}, {
# 				"name": "S"
# 			}]
# 		}]
# 		"""
# 	And jobs已添加商品
# 		"""
# 		[{
# 			"name": "商品1",
# 			"price":10.0
# 		}, {
# 			"name": "商品2",
# 			"price": 20.0
# 		},{
# 			"name": "商品3",
# 			"is_enable_model": "启用规格",
# 			"model": {
# 				"models": {
# 					"黑色 M": {
# 						"price": 30.0
# 					}
# 				}
# 			}
# 		}, {
# 			"name": "商品4",
# 			"model": {
# 				"models": {
# 					"standard": {
# 						"price": 40.0,
# 						"stock_type": "有限",
# 						"stocks": 2
# 					}
# 				}
# 			}
# 		}, {
# 			"name": "商品5",
# 			"price": 50.0,
# 			"pay_interfaces":[{
# 				"type": "在线支付"
# 			}]
# 		}]
# 		"""
# 	And bill关注jobs的公众号

# 	#构造订单数据
# 	When bill访问jobs的webapp
# 	#待支付订单
# 	And bill购买jobs的商品
# 		"""
# 		{
# 			"order_id":"001",
# 			"pay_type":"微信支付",
# 			"products": [{
# 				"name": "商品1",
# 				"count": 1
# 			}]
# 		}
# 		"""

# 		And bill购买jobs的商品
# 		"""
# 		{
# 			"order_id":"002",
# 			"pay_type":"微信支付",
# 			"products": [{
# 				"name": "商品2",
# 				"count": 2
# 			}]
# 		}
# 		"""

# 	#待发货订单
# 	And bill购买jobs的商品
# 		"""
# 		{
# 			"order_id":"003",
# 			"pay_type":"货到付款",
# 			"products": [{
# 				"name": "商品1",
# 				"count": 1
# 			}, {
# 				"name": "商品2",
# 				"count": 1
# 			}, {
# 				"name": "商品3",
# 				"model": "黑色 M",
# 				"count": 1
# 			}]
# 		}
# 		"""

# 	#待收货订单
# 	And bill购买jobs的商品
# 		"""
# 		{
# 			"order_id":"004",
# 			"pay_type": "货到付款",
# 			"products": [{
# 				"name": "商品2",
# 				"count": 1
# 			},{
# 				"name": "商品4",
# 				"count": 1
# 			}]
# 		}
# 		"""

# 	#已取消订单
# 	When bill购买jobs的商品
# 		"""
# 		{
# 			"order_id":"005",
# 			"pay_type":"微信支付",
# 			"products": [{
# 				"name": "商品1",
# 				"count": 1
# 			}]
# 		}
# 		"""
# 	When bill取消订单'005'

# 	Given jobs登录系统
# 	When jobs填写发货信息
# 		"""
# 		[{
# 			"order_no": "004",
# 			"logistics_name":"顺丰速递",
# 			"number":"13013013011",
# 			"logistics":true,
# 			"ship_name": "bill"
# 		}]
# 		"""

# @personCenter @appallOrder @todo
# Scenario:1 会员通过个人中心的'待支付',浏览订单列表信息
# 	When bill访问jobs的webapp
# 	And bill访问个人中心
# 	And bill访问个人中心的'待支付'
# 	#页面标题为'待支付',默认显示'待支付'页签的订单信息
# 	Then bill获得webapp'待支付'页面的'待支付'订单列表
# 		"""
# 		[{
# 			"status": "待支付",
# 			"created_at": "今天",
# 			"products": [{
# 				"name": "商品2"
# 			}],
# 			"counts": 2,
# 			"final_price": 40.00,
# 			"actions": ["取消订单", "支付"]
# 		},{
# 			"status": "待支付",
# 			"created_at": "今天",
# 			"products": [{
# 				"name": "商品1"
# 			}],
# 			"counts": 2,
# 			"final_price": 40.00,
# 			"actions": ["取消订单", "支付"]
# 		}]
# 		"""

# 	#由'待支付'页签切换到'全部订单'页签，页面标题仍为'待支付'
# 	When bill浏览webapp'待支付'页面的'全部订单'
# 	Then bill获得webapp'待支付'页面的'全部订单'订单列表
# 		"""
# 		[{
# 			"status": "已取消",
# 			"created_at": "今天",
# 			"products": [{
# 				"name": "商品1"
# 			}],
# 			"counts": 1,
# 			"final_price": 10.00
# 		},{
# 			"status": "待收货",
# 			"created_at": "今天",
# 			"products": [{
# 				"name": "商品2"
# 			},{
# 				"name": "商品4"
# 			}],
# 			"counts": 2,
# 			"final_price": 60.00,
# 			"actions": ["查看物流"]
# 		},{
# 			"status": "待发货",
# 			"created_at": "今天",
# 			"products": [{
# 				"name": "商品1"
# 			},{
# 				"name": "商品2"
# 			},{
# 				"name": "商品2",
# 				"model": "黑色 M"
# 			}],
# 			"counts": 3,
# 			"final_price": 60.00
# 		},{
# 			"status": "待支付",
# 			"created_at": "今天",
# 			"products": [{
# 				"name": "商品2"
# 			}],
# 			"counts": 2,
# 			"final_price": 40.00,
# 			"actions": ["取消订单", "支付"]
# 		},{
# 			"status": "待支付",
# 			"created_at": "今天",
# 			"final_price": 10.00,
# 			"products": [{
# 				"name": "商品1"
# 			}],
# 			"counts": 1,
# 			"final_price": 20.00,
# 			"actions": ["取消订单", "支付"]
# 		}]
# 		"""

# @personCenter @appallOrder @todo
# Scenario:2 会员通过个人中心的'待发货',浏览订单列表信息
# 	When bill访问jobs的webapp
# 	And bill访问个人中心
# 	And bill访问个人中心的'待发货'
# 	#页面标题为'待发货',默认显示'待发货'页签的订单信息
# 	Then bill获得webapp'待发货'页面的'待发货'订单列表
# 		"""
# 		[{
# 			"status": "待发货",
# 			"created_at": "今天",
# 			"products": [{
# 				"name": "商品1"
# 			},{
# 				"name": "商品2"
# 			},{
# 				"name": "商品2",
# 				"model": "黑色 M"
# 			}],
# 			"counts": 3,
# 			"final_price": 60.00
# 		}]
# 		"""

# 	#由'待发货'页签切换到'待收货'页签，页面标题仍为'待发货'
# 	When bill浏览webapp'待发货'页面的'待收货'
# 	Then bill获得webapp'待发货'页面的'待收货'订单列表
# 		"""
# 		[{
# 			"status": "待收货",
# 			"created_at": "今天",
# 			"products": [{
# 				"name": "商品2"
# 			},{
# 				"name": "商品4"
# 			}],
# 			"counts": 2,
# 			"final_price": 60.00,
# 			"actions": ["查看物流"]
# 		}]
# 		"""

# @personCenter @appallOrder @todo
# Scenario:3 会员通过个人中心的'待收货',浏览订单列表信息
# 	When bill访问jobs的webapp
# 	And bill访问个人中心
# 	And bill访问个人中心的'待收货'
# 	#页面标题为'待收货',默认显示'待收货'页签的订单信息
# 	Then bill获得webapp'待收货'页面的'待收货'订单列表
# 		"""
# 		[{
# 			"status": "待收货",
# 			"created_at": "今天",
# 			"products": [{
# 				"name": "商品2"
# 			},{
# 				"name": "商品4"
# 			}],
# 			"counts": 2,
# 			"final_price": 60.00,
# 			"actions": ["查看物流"]
# 		}]
# 		"""

# 	#由'待收货'页签切换到'全部订单'页签，页面标题仍为'待收货'
# 	When bill浏览webapp'待收货'页面的'全部订单'
# 	Then bill获得webapp'待收货'页面的'全部订单'订单列表
# 		"""
# 		[{
# 			"status": "已取消",
# 			"created_at": "今天",
# 			"products": [{
# 				"name": "商品1"
# 			}],
# 			"counts": 1,
# 			"final_price": 10.00
# 		},{
# 			"status": "待收货",
# 			"created_at": "今天",
# 			"products": [{
# 				"name": "商品2"
# 			},{
# 				"name": "商品4"
# 			}],
# 			"counts": 2,
# 			"final_price": 60.00,
# 			"actions": ["查看物流"]
# 		},{
# 			"status": "待发货",
# 			"created_at": "今天",
# 			"products": [{
# 				"name": "商品1"
# 			},{
# 				"name": "商品2"
# 			},{
# 				"name": "商品2",
# 				"model": "黑色 M"
# 			}],
# 			"counts": 3,
# 			"final_price": 60.00
# 		},{
# 			"status": "待支付",
# 			"created_at": "今天",
# 			"products": [{
# 				"name": "商品2"
# 			}],
# 			"counts": 2,
# 			"final_price": 40.00,
# 			"actions": ["取消订单", "支付"]
# 		},{
# 			"status": "待支付",
# 			"created_at": "今天",
# 			"final_price": 10.00,
# 			"products": [{
# 				"name": "商品1"
# 			}],
# 			"counts": 1,
# 			"final_price": 20.00,
# 			"actions": ["取消订单", "支付"]
# 		}]
# 		"""

# @personCenter @appallOrder @todo
# Scenario:4 会员通过个人中心的'全部订单',浏览订单列表信息
# 	When bill访问jobs的webapp
# 	And bill访问个人中心
# 	And bill访问个人中心的'全部订单'
# 	Then bill获得webapp'全部订单列表'页面的'全部订单'订单列表
# 		"""
# 		[{
# 			"status": "已取消",
# 			"created_at": "今天",
# 			"products": [{
# 				"name": "商品1"
# 			}],
# 			"counts": 1,
# 			"final_price": 10.00
# 		},{
# 			"status": "待收货",
# 			"created_at": "今天",
# 			"products": [{
# 				"name": "商品2"
# 			},{
# 				"name": "商品4"
# 			}],
# 			"counts": 2,
# 			"final_price": 60.00,
# 			"actions": ["查看物流"]
# 		},{
# 			"status": "待发货",
# 			"created_at": "今天",
# 			"products": [{
# 				"name": "商品1"
# 			},{
# 				"name": "商品2"
# 			},{
# 				"name": "商品2",
# 				"model": "黑色 M"
# 			}],
# 			"counts": 3,
# 			"final_price": 60.00
# 		},{
# 			"status": "待支付",
# 			"created_at": "今天",
# 			"products": [{
# 				"name": "商品2"
# 			}],
# 			"counts": 2,
# 			"final_price": 40.00,
# 			"actions": ["取消订单", "支付"]
# 		},{
# 			"status": "待支付",
# 			"created_at": "今天",
# 			"final_price": 10.00,
# 			"products": [{
# 				"name": "商品1"
# 			}],
# 			"counts": 1,
# 			"final_price": 20.00,
# 			"actions": ["取消订单", "支付"]
# 		}]
# 		"""

# 	#由'全部订单'页签切换到'待发货'页签，页面标题仍为'全部订单列表'
# 	When bill浏览webapp'全部订单列表'页面的'待发货'
# 	Then bill获得webapp'全部订单列表'页面的'待发货'订单列表
# 		"""
# 		[{
# 			"status": "待发货",
# 			"created_at": "今天",
# 			"products": [{
# 				"name": "商品1"
# 			},{
# 				"name": "商品2"
# 			},{
# 				"name": "商品2",
# 				"model": "黑色 M"
# 			}],
# 			"counts": 3,
# 			"final_price": 60.00
# 		}]
# 		"""

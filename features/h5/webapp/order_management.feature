#bc
#editor 新新 2015.10.20
#editor 三香 2015.11.26
#备注：此feature与上一版本改动比较大，实现时若有问题请及时沟通

@func:webapp.modules.mall.views.list_products
Feature: 在webapp中管理订单

Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
	And jobs已添加商品:weapp
		"""
		[{
			"name": "商品1",
			"price": 10.00
		}, {
			"name": "商品2",
			"price": 20
		}, {
			"name": "商品3",
			"price": 30
		}]
		"""
	#支付方式
	Given jobs已添加支付方式:weapp
		"""
		[{
			"type": "微信支付",
			"is_active": "启用"
		}, {
			"type": "货到付款",
			"is_active": "启用"
		}]
		"""
	And bill关注jobs的公众号

@mall3 @mall2 @mall.webapp @mall.pay_order @p1 @duhao
Scenario: 1 bill在下单购买jobs的商品后，使用货到付款进行支付，支付后
	1. bill的订单中变为 待发货
	2. jobs在后台看到订单变为待发货
	3. jobs对该订单进行发货
		bill在weapp端看到订单状态为"待收货";
		jobs在后台看到的订单信息为"已发货";

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"001",
			"pay_type": "货到付款",
			"products": [{
				"name": "商品1",
				"count": 1
			},{
				"name": "商品2",
				"count": 1
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"order_no":"001",
			"status": "待发货",
			"final_price": 30.00,
			"products": [{
				"name": "商品1",
				"price": 10.00,
				"count": 1
			},{
				"name": "商品2",
				"price": 20.00,
				"count": 1
			}]
		}
		"""

	Given jobs登录系统:weapp
	Then jobs可以看到订单列表:weapp
		"""
		[{
			"order_no":"001",
			"status": "待发货",
			"price": 30.00,
			"buyer": "bill",
			"products":[{
				"product_name": "商品1",
				"count": 1,
				"total_price": "10.00"
			},{
				"product_name": "商品2",
				"count": 1,
				"total_price": "20.00"
			}]
		}]
		"""

	When jobs填写发货信息:weapp
		"""
		[{
			"order_no": "001",
			"logistics_name":"顺丰速递",
			"number":"13013013011",
			"logistics":true,
			"ship_name": "bill"
		}]
		"""
	Then jobs可以看到订单列表:weapp
		"""
		[{
			"order_no": "001",
			"status": "已发货",
			"price": 30.00,
			"buyer": "bill",
			"products":[{
				"product_name": "商品1",
				"count": 1,
				"total_price": "10.00"
			},{
				"product_name": "商品2",
				"count": 1,
				"total_price": "20.00"
			}]
		}]
		"""

	When bill访问jobs的webapp
	Then bill查看个人中心'全部'订单列表
		"""
		[{
			"status": "待收货",
			"final_price": 30.00,
			"products": [{
				"name": "商品1"
			},{
				"name": "商品2"
			}]
		}]
		"""

@mall3 @mall2 @mall.webapp @mall.pay_order @p2 @duhao
Scenario: 2 bill在下单购买jobs的商品后，又取消订单
	1. bill的订单中变为已取消
	2. jobs在后台看到订单变为已取消

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"001",
			"pay_type": "微信支付",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"order_no":"001",
			"status": "待支付",
			"final_price": 10.00,
			"products": [{
				"name": "商品1",
				"price": 10.00,
				"count": 1
			}]
		}
		"""

	Given jobs登录系统:weapp
	Then jobs可以看到订单列表:weapp
		"""
		[{
			"order_no":"001",
			"status": "待支付",
			"price": 10.00,
			"buyer": "bill",
			"products":[{
				"product_name": "商品1",
				"count": 1,
				"total_price": "10.00"
			}]
		}]
		"""

	When bill取消订单'001'
	Given jobs登录系统:weapp
	Then jobs可以看到订单列表:weapp
		"""
		[{
			"order_no":"001",
			"status": "已取消",
			"price": 10.00,
			"buyer": "bill",
			"products":[{
				"product_name": "商品1",
				"count": 1,
				"total_price": "10.00"
			}]
		}]
		"""

	When bill访问jobs的webapp
	Then bill查看个人中心'全部'订单列表
		"""
		[{
			"status": "已取消",
			"final_price": 10.00,
			"products": [{
				"name": "商品1"
			}]
		}]
		"""

@mall3 @mall2 @mall.webapp @mall.pay_order @p3 @duhao @dh
Scenario: 3 bill在下单购买jobs的商品后，jobs发货方式为"不需要物流"，bill的订单状态变为"已发货"

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"001",
			"pay_type": "货到付款",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"order_no": "001",
			"status": "待发货",
			"final_price": 10.00,
			"products": [{
				"name": "商品1",
				"price": 10.00,
				"count": 1
			}]
		}
		"""

	Given jobs登录系统:weapp
	Then jobs可以看到订单列表:weapp
		"""
		[{
			"order_no": "001",
			"status": "待发货",
			"price": 10.00,
			"buyer": "bill",
			"products":[{
				"product_name": "商品1",
				"count": 1,
				"total_price": "10.00"
			}]
		}]
		"""

	When jobs填写发货信息:weapp
		"""
		[{
			"order_no": "001"
		}]
		"""
	Then jobs可以看到订单列表:weapp
		"""
		[{
			"order_no": "001",
			"status": "已发货",
			"price": 10.00,
			"buyer": "bill",
			"products":[{
				"product_name": "商品1",
				"count": 1,
				"total_price": "10.00"
			}]
		}]
		"""

	When bill访问jobs的webapp
	Then bill查看个人中心'全部'订单列表
		"""
		[{
			"status": "待收货",
			"final_price": 10.00,
			"products":[{
				"name": "商品1"
			}]
		}]
		"""

@mall3 @mall2 @mall @mall.webapp @mall.pay_order @duhao
Scenario: 4 bill 在不同时段下订单，订单列表按下订单的时间倒序排列
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 10.00,
			"products": [{
				"name": "商品1",
				"price": 10.00,
				"count": 1
			}]
		}
		"""
	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品2",
				"count": 1
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 20.00,
			"products": [{
				"name": "商品2",
				"price": 20.00,
				"count": 1
			}]
		}
		"""
	Given jobs登录系统:weapp
	Then jobs可以看到订单列表:weapp
		"""
		[{
			"status": "待支付",
			"price": 20.00,
			"products_count": 1,
			"products":[{
				"product_name": "商品2",
				"img_url": "/standard_static/test_resource_img/hangzhou1.jpg",
				"count": 1
			}]
		},{
			"status": "待支付",
			"price": 10.00,
			"products_count": 1,
			"products":[{
				"product_name": "商品1",
				"img_url": "/standard_static/test_resource_img/hangzhou1.jpg",
				"count": 1
			}]
		}]
		"""

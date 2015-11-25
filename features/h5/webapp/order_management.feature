#bc
#editor 新新 2015.10.20

@func:webapp.modules.mall.views.list_products
Feature: 在webapp中管理订单
Background:
	Given jobs登录系统
	And jobs已添加商品
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
	Given jobs已添加支付方式
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

@mall2 @mall.webapp @mall.pay_order @p1
Scenario: 1 bill在下单购买jobs的商品后，使用货到付款进行支付，支付后
	1. bill的订单中变为 待发货
	2. jobs在后台看到订单变为待发货
	3. jobs对该订单进行发货
		bill在weapp端看到订单状态为"已发货";
		jobs在后台看到的订单信息为"已发货";

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
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
			"status": "待支付",
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
	Given jobs登录系统
	Then jobs可以看到订单列表
		"""
		[{
			"status": "待支付",
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

	When bill使用支付方式'货到付款'进行支付
	Then bill支付订单成功
		"""
		{
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
	Then jobs可以看到订单列表
		"""
		[{

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

	Given jobs已有的订单
	    """
	    [{
	        "order_no":"20150423161112",
	        "member":"bill",
	        "type":"普通订单",
	        "status":"待发货",
	        "sources":"本店",
	        "order_price":30.00,
	        "payment_price":30.00,
	        "freight":0,
	        "ship_name":"bill",
	        "ship_tel":"13013013011",
	        "ship_area":"北京市,北京市,海淀区",
	        "ship_address":"泰兴大厦",
	        "products":[{
	            "name":"商品1",
	            "price": "10.00",
	            "count": 1
	        },{
	            "name":"商品2",
	            "price": "20.00",
	            "count": 1
	        }]
	    }]
	    """

	When jobs填写发货信息
		"""
		[{
			"order_no": "20150423161112",
			"logistics_name":"顺丰速递",
			"number":"13013013011",
			"logistics":true,
			"ship_name": "bill"
		}]
		"""
	Then jobs可以看到订单列表
		"""
		[{
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
		},{
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
	When bill访问jobs的webapp
	Then bill查看个人中心全部订单
		"""
		[{
			"status": "待收货",
			"final_price": 30.00,
			"products": [{
				"name": "商品1"
			},{
				"name": "商品2"

			}]
		},{
			"status": "待发货",
			"final_price": 30.00,
			"products":[{
				"name": "商品1"
			},{
				"name": "商品2"
			}]
		}]
		"""

@mall2 @mall.webapp @mall.pay_order @p2 
Scenario: 2 bill在下单购买jobs的商品后，又取消订单
	1. bill的订单中变为已取消
	2. jobs在后台看到订单变为已取消

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
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
	Then jobs可以看到订单列表
		"""
		[{
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

	Given jobs已有的订单
	    """
	    [{
	        "order_no":"20150423161112",
	        "member":"bill",
	        "type":"普通订单",
	        "status":"已取消",
	        "sources":"本店",
	        "order_price":10.00,
	        "payment_price":10.00,
	        "freight":0,
	        "ship_name":"bill",
	        "ship_tel":"13013013011",
	        "ship_area":"北京市,北京市,海淀区",
	        "ship_address":"泰兴大厦",
	        "products":[{
	            "name":"商品1",
	            "price": "10.00",
	            "count": 1
	        }]
	    }]
	    """

	When bill取消订单'20150423161112'
	Then jobs可以看到订单列表
		"""
		[{
			"status": "已取消",
			"price": 10.00,
			"buyer": "bill",
			"products":[{
				"product_name": "商品1",
				"count": 1,
				"total_price": "10.00"
			}]
		},{
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
	When bill访问jobs的webapp
	Then bill查看个人中心全部订单
		"""
		[{
			"status": "已取消",
			"final_price": 10.00,
			"products": [{
				"name": "商品1"
			}]
		},{
			"status": "待支付",
			"final_price": 10.00,
			"products":[{
				"name": "商品1"
			}]
		}]
		"""

@mall2 @mall.webapp @mall.pay_order @p3
Scenario: 3 bill在下单购买jobs的商品后，jobs发货方式为"不需要物流"，bill的订单状态变为"已发货"

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
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
	Then jobs可以看到订单列表
		"""
		[{
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

	When bill使用支付方式'货到付款'进行支付
	Then bill支付订单成功
		"""
		{
			"status": "待发货",
			"final_price": 10.00,
			"products": [{
				"name": "商品1",
				"price": 10.00,
				"count": 1
			}]
		}
		"""
	Then jobs可以看到订单列表
		"""
		[{
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

	Given jobs已有的订单
	    """
	    [{
	        "order_no":"20150423161112",
	        "member":"bill",
	        "status":"待发货",
	        "sources":"本店",
	        "order_price":30.00,
	        "payment_price":30.00,
	        "freight":0,
	        "ship_name":"bill",
	        "ship_tel":"13013013011",
	        "ship_area":"北京市,北京市,海淀区",
	        "ship_address":"泰兴大厦",
	        "products":[{
	            "name":"商品1",
	            "price": "10.00",
	            "count": 1
	        },{
	            "name":"商品2",
	            "price": "20.00",
	            "count": 1
	        }]
	    }]
	    """
	When jobs填写发货信息
		"""
		[{
			"order_no": "20150423161112"
		}]
		"""
	Then jobs可以看到订单列表
		"""
		[{
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
		},{
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
	When bill访问jobs的webapp
	Then bill查看个人中心全部订单
		"""
		[{
			"status": "待收货",
			"final_price": 30.00,
			"products": [{
				"name": "商品1"
			},{
				"name": "商品2"

			}]
		},{
			"status": "待发货",
			"final_price": 10.00,
			"products":[{
				"name": "商品1"
			}]
		}]
		"""

@mall2 @mall @mall.webapp @mall.pay_order
Scenario: 4 bill 在不同时段下订单，订单列表按下订单的时间倒序排列
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
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
	Given jobs登录系统
	Then jobs可以看到订单列表
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

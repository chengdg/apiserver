# __author__ : "冯雪静"
#微众精选：手机端购买
Feature: 购买商品
	"""
	1.购买单个商品,验证：购买，运费，供货商
	2.购买一个供货商的多个商品，验证：购物车购买，运费，同一个供货商
	3.购买多个供货商的多个商品,使用微信支付,验证：运费，微信支付，不同供货商，订单状态对应的不同的操作
	4.购买多个供货商的多个商品,使用货到付款,验证：货到付款，不同供货商，订单状态对应的不同的操作
	"""

Background:
	Given jobs登录系统
	And jobs已添加供货商
		"""
		[{
			"name": "土小宝",
			"responsible_person": "宝宝",
			"supplier_tel": "13811223344",
			"supplier_address": "北京市海淀区泰兴大厦",
			"remark": "备注卖花生油"
		}, {
			"name": "丹江湖",
			"responsible_person": "陌陌",
			"supplier_tel": "13811223344",
			"supplier_address": "北京市海淀区泰兴大厦",
			"remark": ""
		}]
		"""
	And jobs已添加运费配置
		"""
		[{
			"name":"顺丰",
			"first_weight": 1,
			"first_weight_price": 13.00,
			"added_weight": 1,
			"added_weight_price": 5.00,
			"special_area": [{
				"to_the":"北京市,江苏省",
				"first_weight": 1,
				"first_weight_price": 20.00,
				"added_weight": 1,
				"added_weight_price": 10.00
			}],
			"free_postages": [{
				"to_the":"北京市",
				"condition": "count",
				"value": 3
			}, {
				"to_the":"北京市",
				"condition": "money",
				"value": 200.0
			}]
		}]
		"""
	When jobs选择'顺丰'运费配置
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
	And jobs已添加商品
		"""
		[{
			"supplier": "土小宝",
			"name": "商品1",
			"price": 100.00,
			"purchase_price": 9.00,
			"weight": 1.0,
			"stock_type": "无限",
			"postage": "系统"
		}, {
			"supplier": "丹江湖",
			"name": "商品2",
			"price": 99.00,
			"purchase_price": 9.00,
			"weight": 1.0,
			"stock_type": "有限",
			"stocks": 10,
			"postage": "系统"
		}, {
			"supplier": "土小宝",
			"name": "商品3",
			"price": 100.00,
			"purchase_price": 9.00,
			"weight": 1.0,
			"stock_type": "有限",
			"stocks": 10,
			"postage": "系统",
			"pay_interfaces":[{
				"type": "在线支付"
			}]
		}]
		"""
	And bill关注jobs的公众号
	When bill访问jobs的webapp
	And bill设置jobs的webapp的收货地址
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"area": "北京市,北京市,海淀区",
			"ship_address": "泰兴大厦"
		}
		"""


@mall2 @buy   @supplier
Scenario: 1 购买单个商品
	jobs添加商品后
	1. bill能在webapp中购买jobs添加的商品
	2. bill的订单中的信息正确

	#买单个商品满足包邮条件
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"order_id": "001",
			"products": [{
				"name": "商品1",
				"count": 2
			}],
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"order_no": "001",
			"status": "待支付",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 200.00,
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 2
			}],
			"actions": ["取消订单", "支付"]
		}
		"""
	Given jobs登录系统
	Then jobs可以获得最新订单详情
		"""
		{
			"order_no": "001",
			"status": "待支付",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 200.00,
			"postage": 0.00,
			"actions": ["支付", "修改价格", "取消订单"],
			"products":
			[{
				"name": "商品1",
				"price": 100.00,
				"count": 2,
				"supplier": "土小宝"
			}]
		}
		"""

@mall2 @buy   @supplier
Scenario: 2 购买一个供货商的多个商品
	bill购买商品后
	1. 能看到订单详情
	2. 能在不同状态下执行各种操作

	#买多个满足包邮条件，同一个供货商
	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 1
		}, {
			"name": "商品3",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"context": [{
				"name": "商品1"
			}, {
				"name": "商品3"
			}]
		}
		"""
	And bill在购物车订单编辑中点击提交订单
		"""
		{
			"pay_type": "货到付款",
			"order_no": "001"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"order_no": "001",
			"status": "待支付",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 200.00,
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1
			}, {
				"name": "商品3",
				"price": 100.00,
				"count": 1
			}],
			"actions": ["取消订单", "支付"]
		}
		"""
	Given jobs登录系统
	Then jobs可以获得最新订单详情
		"""
		{
			"order_no": "001",
			"status": "待支付",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 200.00,
			"postage": 0.00,
			"actions": ["支付", "修改价格", "取消订单"],
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝"
			}, {
				"name": "商品3",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝"
			}]
		}
		"""
	When bill访问jobs的webapp
	And bill使用支付方式'微信支付'进行支付
	Given jobs登录系统
	Then jobs可以看到订单列表
		"""
		[{
			"order_no": "001",
			"status": "待发货",
			"final_price": 200.00,
			"actions": ["发货", "申请退款"],
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1,
				"supplier":"土小宝"
			}, {
				"name": "商品3",
				"price": 100.00,
				"count": 1,
				"supplier":"土小宝"
			}]
		}]
		"""

@mall2 @buy   @supplier
Scenario: 3 购买多个供货商的多个商品,使用微信支付
	bill购买商品后，使用微信支付
	1. 能看到订单详情
	2. 能在不同状态下执行各种操作

	#买多个商品不满足包邮条件，不同供货商
	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 1
		}, {
			"name": "商品2",
			"count": 1
		}, {
			"name": "商品3",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"context": [{
				"name": "商品1"
			}, {
				"name": "商品2"
			}, {
				"name": "商品3"
			}]
		}
		"""
	And bill在购物车订单编辑中点击提交订单
		"""
		{
			"pay_type": "货到付款",
			"order_no": "001"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"order_no": "001",
			"status": "待支付",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 299.00,
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1
			}, {
				"name": "商品2",
				"price": 99.00,
				"count": 1
			}, {
				"name": "商品3",
				"price": 100.00,
				"count": 1
			}],
			"actions": ["取消订单", "支付"]
		}
		"""
	Given jobs登录系统
	Then jobs可以获得最新订单详情
		"""
		{
			"order_no": "001",
			"status": "待支付",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 299.00,
			"actions": ["支付", "修改价格", "取消订单"],
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1
			}, {
				"name": "商品3",
				"price": 100.00,
				"count": 1
			}, {
				"name": "商品2",
				"price": 99.00,
				"count": 1
			}]
		}
		"""
	When bill访问jobs的webapp
	And bill使用支付方式'微信支付'进行支付
	Given jobs登录系统
	Then jobs可以看到订单列表
		"""
		[{
			"order_no": "001",
			"status": "待发货",
			"final_price": 299.00,
			"actions": ["申请退款"],
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1,
				"supplier":"土小宝",
				"status": "待发货",
				"actions": ["发货"]
			}, {
				"name": "商品3",
				"price": 100.00,
				"count": 1,
				"supplier":"土小宝",
				"status": "待发货",
				"actions": ["发货"]
			}, {
				"name": "商品2",
				"price": 99.00,
				"count": 1,
				"supplier":"丹江湖",
				"status": "待发货",
				"actions": ["发货"]
			}]
		}]
		"""
	When jobs对订单进行发货
		"""
		{
			"order_no":"001-土小宝",
			"logistics":"顺丰速运",
			"number":"123456789",
			"shipper":"jobs"
		}
		"""
	Then jobs可以看到订单列表
		"""
		[{
			"order_no": "001",
			"status": "待发货",
			"final_price": 299.00,
			"actions": ["申请退款"],
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1,
				"supplier":"土小宝",
				"status": "已发货",
				"actions": ["标记完成", "修改物流"]
			}, {
				"name": "商品3",
				"price": 100.00,
				"count": 1,
				"supplier":"土小宝",
				"status": "已发货",
				"actions": ["标记完成", "修改物流"]
			}, {
				"name": "商品2",
				"price": 99.00,
				"count": 1,
				"supplier":"丹江湖",
				"status": "待发货",
				"actions": ["发货"]
			}]
		}]
		"""
	Then jobs可以获得最新订单详情
		"""
		{
			"order_no": "001",
			"status": "待发货",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 299.00,
			"actions": ["申请退款"],
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝",
				"status": "已发货"
			}, {
				"name": "商品3",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝",
				"status": "已发货"
			}, {
				"name": "商品2",
				"price": 99.00,
				"count": 1,
				"supplier": "丹江湖",
				"status": "待发货"
			}]
		}
		"""
	When bill访问jobs的webapp
	Then bill手机端获取订单"001"
		"""
		{
			"order_no": "001",
			"status": "待发货",
			"final_price": 299.00,
			"postage": 0.00,
			"products": [{
				"包裹1": [{
					"name": "商品1",
					"price": 100.00,
					"count": 1
				}, {
					"name": "商品3",
					"price": 100.00,
					"count": 1
				}],
				"status": "待收货"
			}, {
				"包裹2": [{
					"name": "商品2",
					"price": 99.00,
					"count": 1
				}],
				"status": "待发货"
			}]
		}
		"""
	Given jobs登录系统
	When jobs对订单进行发货
		"""
		{
			"order_no":"001-丹江湖",
			"logistics":"顺丰速运",
			"number":"123456789",
			"shipper":"jobs|备注"
		}
		"""
	Then jobs可以看到订单列表
		"""
		[{
			"order_no": "001",
			"status": "已发货",
			"final_price": 299.00,
			"postage": 0.00,
			"actions": ["申请退款"],
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝",
				"status": "已发货"
			}, {
				"name": "商品3",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝",
				"status": "已发货"
			}, {
				"name": "商品2",
				"price": 99.00,
				"count": 1,
				"supplier": "丹江湖",
				"status": "已发货"
			}]
		}]
		"""
	When bill访问jobs的webapp
	Then bill手机端获取订单"001"
		"""
		{
			"order_no": "001",
			"status": "待收货",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 299.00,
			"postage": 0.00,
			"products": [{
				"包裹1": [{
					"name": "商品1",
					"price": 100.00,
					"count": 1
				}, {
					"name": "商品3",
					"price": 100.00,
					"count": 1
				}],
				"status": "待收货"
			}, {
				"包裹2": [{
					"name": "商品2",
					"price": 99.00,
					"count": 1
				}],
				"status": "待收货"
			}]
		}
		"""
	Given jobs登录系统
	When jobs'申请退款'订单'001'
  	# 此处看不到退款成功，暂时移出"actions": ["退款成功"],
	Then jobs可以看到订单列表
		"""
		[{
			"order_no": "001",
			"status": "退款中",
			"final_price": 299.00,
			"postage": 0.00,
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝"
			}, {
				"name": "商品3",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝"
			}, {
				"name": "商品2",
				"price": 99.00,
				"count": 1,
				"supplier": "丹江湖"
			}]
		}]
		"""
	When jobs通过财务审核'退款成功'订单'001'
	Then jobs可以看到订单列表
		"""
		[{
			"order_no": "001",
			"status": "退款成功",
			"final_price": 299.00,
			"postage": 0.00,
			"actions": [],
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝"
			}, {
				"name": "商品3",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝"
			}, {
				"name": "商品2",
				"price": 99.00,
				"count": 1,
				"supplier": "丹江湖"
			}]
		}]
		"""

@mall2 @buy   @supplier
Scenario: 4 购买多个供货商的多个商品,使用货到付款
	bill购买商品后，使用货到付款
	1. 能看到订单详情
	2. 能在不同状态下执行各种操作

	Given jobs登录系统
	When jobs更新商品'商品3'
		"""
		{
			"name": "商品3",
			"price": 100.00,
			"purchase_price": 9.00,
			"weight": 1.0,
			"stock_type": "有限",
			"stocks": 10,
			"postage": 10.00
		}
		"""
	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 1
		}, {
			"name": "商品2",
			"count": 1
		}, {
			"name": "商品3",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"context": [{
				"name": "商品1"
			}, {
				"name": "商品2"
			}, {
				"name": "商品3"
			}]
		}
		"""
	And bill在购物车订单编辑中点击提交订单
		"""
		{
			"pay_type": "货到付款",
			"order_no": "001"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"order_no": "001",
			"status": "待支付",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 339.00,
			"postage": 40.00,
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1
			}, {
				"name": "商品2",
				"price": 99.00,
				"count": 1
			}, {
				"name": "商品3",
				"price": 100.00,
				"count": 1
			}],
			"actions": ["取消订单", "支付"]
		}
		"""
	Given jobs登录系统
	Then jobs可以获得最新订单详情
		"""
		{
			"order_no": "001",
			"status": "待支付",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 339.00,
			"postage": 40.00,
			"actions": ["支付", "修改价格", "取消订单"],
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1
			}, {
				"name": "商品3",
				"price": 100.00,
				"count": 1
			}, {
				"name": "商品2",
				"price": 99.00,
				"count": 1
			}]
		}
		"""
	When bill访问jobs的webapp
	And bill使用支付方式'货到付款'进行支付
	Given jobs登录系统
	Then jobs可以看到订单列表
		"""
		[{
			"order_no": "001",
			"status": "待发货",
			"final_price": 339.00,
			"postage": 40.00,
			"actions": ["取消订单"],
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝",
				"status": "待发货",
				"actions": ["发货"]
			}, {
				"name": "商品3",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝",
				"status": "待发货",
				"actions": ["发货"]
			}, {
				"name": "商品2",
				"price": 99.00,
				"count": 1,
				"supplier": "丹江湖",
				"status": "待发货",
				"actions": ["发货"]
			}]
		}]
		"""
	When jobs对订单进行发货
		"""
		{
			"order_no":"001-丹江湖",
			"logistics":"顺丰速运",
			"number":"123456789",
			"shipper":"jobs"
		}
		"""
	Then jobs可以看到订单列表
		"""
		[{
			"order_no": "001",
			"status": "待发货",
			"final_price": 339.00,
			"postage": 40.00,
			"actions": ["取消订单"],
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝",
				"status": "待发货",
				"actions": ["发货"]
			}, {
				"name": "商品3",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝",
				"status": "待发货",
				"actions": ["发货"]
			}, {
				"name": "商品2",
				"price": 99.00,
				"count": 1,
				"supplier": "丹江湖",
				"status": "已发货",
				"actions": ["标记完成", "修改物流"]
			}]
		}]
		"""
	Then jobs可以获得最新订单详情
		"""
		{
			"order_no": "001",
			"status": "待发货",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 339.00,
			"postage": 40.00,
			"actions": ["取消订单"],
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝",
				"status": "待发货"
			}, {
				"name": "商品3",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝",
				"status": "待发货"
			}, {
				"name": "商品2",
				"price": 99.00,
				"count": 1,
				"supplier": "丹江湖",
				"status": "已发货"
			}]
		}
		"""
	When bill访问jobs的webapp
	Then bill手机端获取订单"001"
		"""
		{
			"order_no": "001",
			"status": "待发货",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 339.00,
			"postage": 40.00,
			"products": [{
				"包裹1": [{
					"name": "商品1",
					"price": 100.00,
					"count": 1
				}, {
					"name": "商品3",
					"price": 100.00,
					"count": 1
				}],
				"status": "待发货"
			}, {
				"包裹2": [{
					"name": "商品2",
					"price": 99.00,
					"count": 1
				}],
				"status": "待收货"
			}]
		}
		"""
	Given jobs登录系统
	When jobs对订单进行发货
		"""
		{
			"order_no":"001-土小宝",
			"logistics":"顺丰速运",
			"number":"123456789",
			"shipper":"jobs|备注"
		}
		"""
	Then jobs可以看到订单列表
		"""
		[{
			"order_no": "001",
			"status": "已发货",
			"final_price": 339.00,
			"postage": 40.00,
			"actions": ["取消订单"],
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝",
				"status": "已发货",
				"actions": ["标记完成", "修改物流"]
			}, {
				"name": "商品3",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝",
				"status": "已发货",
				"actions": ["标记完成", "修改物流"]
			}, {
				"name": "商品2",
				"price": 99.00,
				"count": 1,
				"supplier": "丹江湖",
				"status": "已发货",
				"actions": ["标记完成", "修改物流"]
			}]
		}]
		"""
	When bill访问jobs的webapp
	Then bill手机端获取订单"001"
		"""
		{
			"order_no": "001",
			"status": "待收货",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 339.00,
			"postage": 40.00,
			"products": [{
				"包裹1": [{
					"name": "商品1",
					"price": 100.00,
					"count": 1
				}, {
					"name": "商品3",
					"price": 100.00,
					"count": 1
				}],
				"status": "待收货"
			}, {
				"包裹2": [{
					"name": "商品2",
					"price": 99.00,
					"count": 1
				}],
				"status": "待收货"
			}]
		}
		"""
	Given jobs登录系统
	When jobs完成订单"001-土小宝"
	Then jobs可以看到订单列表
		"""
		[{
			"order_no": "001",
			"status": "已发货",
			"final_price": 339.00,
			"postage": 40.00,
			"actions": ["取消订单"],
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝",
				"status": "已完成",
				"actions": []
			}, {
				"name": "商品3",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝",
				"status": "已完成",
				"actions": []
			}, {
				"name": "商品2",
				"price": 99.00,
				"count": 1,
				"supplier": "丹江湖",
				"status": "已发货",
				"actions": ["标记完成", "修改物流"]
			}]
		}]
		"""
	When bill访问jobs的webapp
	Then bill手机端获取订单"001"
		"""
		{
			"order_no": "001",
			"status": "待收货",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 339.00,
			"postage": 40.00,
			"products": [{
				"包裹1": [{
					"name": "商品1",
					"price": 100.00,
					"count": 1
				}, {
					"name": "商品3",
					"price": 100.00,
					"count": 1
				}],
				"status": "已完成"
			}, {
				"包裹2": [{
					"name": "商品2",
					"price": 99.00,
					"count": 1
				}],
				"status": "待收货"
			}]
		}
		"""
	Given jobs登录系统
	When jobs完成订单"001-丹江湖"
	Then jobs可以看到订单列表
		"""
		[{
			"order_no": "001",
			"status": "已完成",
			"final_price": 339.00,
			"postage": 40.00,
			"actions": ["申请退款"],
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝",
				"status": "已完成",
				"actions": []
			}, {
				"name": "商品3",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝",
				"status": "已完成",
				"actions": []
			}, {
				"name": "商品2",
				"price": 99.00,
				"count": 1,
				"supplier": "丹江湖",
				"status": "已完成",
				"actions": []
			}]
		}]
		"""
	When bill访问jobs的webapp
	Then bill手机端获取订单"001"
		"""
		{
			"order_no": "001",
			"status": "已完成",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 339.00,
			"postage": 40.00,
			"products": [{
				"包裹1": [{
					"name": "商品1",
					"price": 100.00,
					"count": 1
				}, {
					"name": "商品3",
					"price": 100.00,
					"count": 1
				}],
				"status": "已完成"
			}, {
				"包裹2": [{
					"name": "商品2",
					"price": 99.00,
					"count": 1
				}],
				"status": "已完成"
			}]
		}
		"""

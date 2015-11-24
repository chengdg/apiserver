 # __edit__ : "王丽"
 #editor 新新 2015.10.20

Feature: 购买买赠活动的商品，手机端订单可以看到买赠商品的数量
"""

	购买买赠活动的商品，在手机端的"待付款"、"待发货"、"待收货"、"待评价"中的订单，订单详情可以展示赠品的数量
"""

@mall2 @promotion @promotionPremium @order @allOrder
Scenario:1 购买买赠活动的商品，在手机端的"待付款"、"待发货"、"待收货"、"待评价"中的订单，订单详情可以展示赠品的数量

	Given jobs登录系统
  	When jobs已添加支付方式
		"""
		[{
			"type": "货到付款",
			"description": "我的货到付款",
			"is_active": "启用"
		},{
			"type": "微信支付",
			"description": "我的微信支付",
			"is_active": "启用"
		}]
		"""
	And jobs已添加商品
		"""
		[{
			"name": "商品赠品",
			"price": 10.00
		},{
			"name": "商品1",
			"price": 100.00
		}]
		"""
	When jobs创建买赠活动
		"""
		[{
			"name": "商品1买一赠二",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品1",
			"premium_products": [{
				"name": "商品赠品",
				"count": 2
			}],
			"count": 1,
			"member_grade":"全部会员",
			"is_enable_cycle_mode": true
		}]
		"""

	#创建"待付款"订单

	When bill关注jobs的公众号
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id": "001",
			"products": [{
				"name": "商品1",
				"count": 1
			}],
			"pay_type": "微信支付",
			"date":"2015-08-08 00:00:00"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 100.00,
			"products": [{
					"name": "商品1",
					"count": 1,
					"promotion": {
						"type": "premium_sale"
					}
				},{
					"name": "商品赠品",
					"count": 2,
					"promotion": {
						"type": "premium_sale:premium_product"
					}
				}]
		}
		"""
	#校验赠品数量
	#查看"待付款"订单详情
	Then bill手机端获取订单"001"
		"""
		{
			"order_no": "001",
			"order_time":"2015-08-08 00:00:00",
			"methods_of_payment":"微信支付",
			"status":"待支付",
			"final_price": 100.00,
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1
			},{
				"name": "商品赠品",
				"price": 0.00,
				"count": 2
			}]
		}
		"""

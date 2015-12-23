# __author__ : "冯雪静"

Feature: 物流完成促使订单完成返积分
	"""
	1 签收快件促使订单完成获得购物返利积分
	jobs发货后，快件被签收，促使订单完成，奖励购物返积分
	"""

Background:
	Given jobs登录系统
	And jobs设定会员积分策略
		"""
		{
			"buy_award_count_for_buyer":10,
			"order_money_percentage_for_each_buy":0.1
		}
		"""
	And jobs已添加支付方式
		"""
		[{
			"type": "货到付款",
			"is_active": "启用"
		}]
		"""
	And jobs已添加商品
		"""
		[{
			"name": "商品1",
			"price": 100.00
		}]
		"""
	And bill关注jobs的公众号


@mall2 @logistics @order
Scenario: 1 签收快件促使订单完成获得购物返利积分
	jobs发货后，快件被签收，促使订单完成

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id": "001",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	When bill使用支付方式'货到付款'进行支付
	Then bill支付订单成功
		"""
		{
			"order_id": "001",
			"methods_of_payment":"货到付款",
			"status":"待发货",
			"final_price": 100.00,
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1
			}]
		}
		"""
	Given jobs登录系统
	When jobs对订单进行发货
		"""
		{
			"order_no": "001",
			"logistics": "申通快递",
			"number": "229388967650",
			"shipper": "jobs"
		}
		"""
	When 快递100发送物流单号'229388967650'完成的信息
	Then jobs能获得订单'001'
		"""
		{
			"order_no": "001",
			"status": "已完成",
			"actions": ["申请退款"],
			"shipper": "jobs",
			"methods_of_payment": "货到付款",
			"number": "229388967650"
		}
		"""
	When bill访问jobs的webapp
	Then bill在jobs的webapp中拥有20会员积分
	Then bill在jobs的webapp中获得积分日志
		"""
		[{
			"content":"购物返利",
			"integral":10
		},{
			"content":"购物返利",
			"integral":10
		}]
		"""
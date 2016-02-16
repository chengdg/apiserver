# watcher: fengxuejing@weizoom.com,benchi@weizoom.com
@func:webapp.modules.mall.order
Feature: 测试"个人中心"有缓存的场景

Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
	And jobs已添加商品分类:weapp
		"""
		[{
			"name": "分类1"
		}, {
			"name": "分类2"
		}, {
			"name": "分类3"
		}]	
		"""
	And jobs已添加商品:weapp
		"""
		[{
			"name": "商品1",
			"model": {
				"models": {
					"standard": {
						"price": 9.9,
						"stock_type": "有限",
						"stocks": 100
					}
				}
			}
		},{
			"name": "商品2",
			"model": {
				"models": {
					"standard": {
						"price": 10,
						"stock_type": "有限",
						"stocks": 100
					}
				}
			}
		}]	
		"""

	And jobs已添加支付方式:weapp
		"""
		[{
			"type":"货到付款"
		}, {
			"type":"微信支付"
		}]
		"""
	And bill关注jobs的公众号:weapp

@mall2 @mall3 @bert
Scenario:1 bill增加订单数再访问个人中心
	bill下单(影响订单数)之后会影响订单数。检查个人中心订单数是否正确。

	When bill访问jobs的webapp
	And bill访问个人中心
	Then '个人中心'中'全部订单'数为0
	Then '个人中心'中'待支付'数为0
	Then '个人中心'中'购物车'数为0

	When bill购买jobs的商品
		"""
		{
			"pay_type": "货到付款",
			"products": [{
				"name": "商品1",
				"count": 1
			}],
			"customer_message": "bill购买'商品1'"
		}
		"""
	And bill访问个人中心
	Then '个人中心'中'全部订单'数为1
	Then '个人中心'中'待支付'数为0
	Then '个人中心'中'购物车'数为0

	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品2",
				"count": 1
			}],
			"customer_message": "bill购买'商品2'"
		}
		"""
	And bill访问个人中心
	Then '个人中心'中'全部订单'数为2
	Then '个人中心'中'待支付'数为1
	Then '个人中心'中'购物车'数为0

@mall2 @mall3 @bert
Scenario:2 添加订单
	bill下单
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"pay_type": "货到付款",
			"products": [{
				"name": "商品1",
				"count": 1
			}],
			"customer_message": "bill购买'商品1'"
		}
		"""
	Given jobs登录系统:weapp
	Then jobs可以看到订单列表:weapp
		"""
		[{
			"status": "待发货",
			"price": 9.9,
			"customer_message": "bill购买'商品1'",
			"products":[{
				"product_name": "商品1",
				"count": 1,
				"total_price": "9.90"
			}]
		}]
		"""

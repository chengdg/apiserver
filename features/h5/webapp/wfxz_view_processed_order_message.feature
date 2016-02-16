# watcher: zhangsanxiang@weizoom.com,benchi@weizoom.com
#_author_:张三香 2016.01.21

Feature: 查看手机端已处理订单详情页的提示信息
	"""
	1.修改手机端'待收货'为'已处理'，增加前台已处理下方提示。（窝夫定制，其他家不修改）
	2.用户购买开启'配送时间'的商品时，需要在编辑订单页选择配送时间
	3.'已处理'订单详情页下方提示（提示分两行显示）：
		商家已经开始处理订单
		我们将在 xxxx-xx-xx xx:xx-xx:xx 送达
	"""

Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
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
Scenario:1 购买有配送时间的商品,查看'已处理'状态订单详情页的提示信息
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"001",
			"pay_type": "货到付款",
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
			"status": "待发货",
			"final_price": 10.00,
			"products": [{
				"name": "配送商品1",
				"price": 10.00,
				"count": 1
			}]
		}
		"""
	Given jobs登录系统:weapp
	When jobs对订单进行发货:weapp
		"""
		{
			"order_no":"001",
			"logistics":"off",
			"shipper": ""
		}
		"""
	Then jobs能获得订单'001':weapp
		"""
		{
			"order_no": "001",
			"methods_of_payment":"货到付款",
			"member": "bill",
			"status":"已发货",
			"actions": ["标记完成", "取消订单"],
			"final_price": 10.00,
			"products": [{
				"name": "配送商品1",
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
			"status":"已处理",
			"distribution_time":"5天后 10:00-12:30",
			"methods_of_payment":"货到付款",
			"final_price": 10.00,
			"products": [{
				"name": "配送商品1",
				"price": 10.00,
				"count": 1
			}]
		}
		"""
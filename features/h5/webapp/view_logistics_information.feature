#_author_:张三香 2015.12.23

Feature:查看订单的物流信息

Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
	And jobs已添加支付方式:weapp
		"""
		[{
			"type": "货到付款"
		}, {
			"type": "微信支付"
		}]
		"""
	And jobs已添加商品:weapp
		"""
		[{
			"name": "商品1",
			"price":10.0
		}, {
			"name": "商品2",
			"price": 20.0
		}]
		"""
	Given bill关注jobs的公众号
	Given tom关注jobs的公众号

@order @logistics @mall3 @duhao
Scenario:1 查看'已发货'订单的物流信息,发货方式为'需要物流'
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"order_id":"001",
			"pay_type":"货到付款",
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
			"pay_type":"货到付款",
			"products": [{
				"name": "商品2",
				"count": 2
			}]
		}
		"""

	#发货001时，物流公司不选择'其他'
		Given jobs登录系统:weapp
		When jobs对订单进行发货:weapp
			"""
			{
				"order_id": "001",
				"logistics": "申通快递",
				"number": "00001",
				"shipper": "jobs"
			}
			"""
		Then bill在webapp查看'001'的物流信息
			"""
			{
				"order_id":"001",
				"logistics":"申通快递",
				"number":"00001"
			}
			"""

		#修改物流信息
		Given jobs登录系统:weapp
		When jobs通过后台管理系统对'001'的物流信息进行修改:weapp
			"""
			{
				"order_id":"001",
				"logistics":"顺丰快递",
				"number":"000011",
				"status":"已发货"
			}
			"""
		Then bill在webapp查看'001'的物流信息
			"""
			{
				"order_id":"001",
				"logistics":"顺丰快递",
				"number":"000011"
			}
			"""

	#发货002时，物流公司选择'其他'
		Given jobs登录系统:weapp
		When jobs对订单进行发货:weapp
			"""
			{
				"order_id": "002",
				"logistics": "其他",
				"name": "比尔",
				"number":"00002",
				"shipper": ""
			}
			"""
		Then bill在webapp查看'002'的物流信息
			"""
			{
				"order_id":"002",
				"logistics":"比尔",
				"number":"00002"
			}
			"""
		
		#修改物流信息
		Given jobs登录系统:weapp
		When jobs通过后台管理系统对'002'的物流信息进行修改:weapp
			"""
			{
				"order_id": "002",
				"status":"已发货",
				"logistics":"顺丰速运",
				"number":"000022",
				"shipper": "jobs"
			}
			"""
		Then bill在webapp查看'002'的物流信息
			"""
			{
				"order_id": "002",
				"logistics":"顺丰速运",
				"number":"000022"
			}
			"""

@order @logistics @mall3 @duhao
Scenario:2 查看'已发货'订单的物流信息,发货方式为'不需要物流'
	When tom访问jobs的webapp
	When tom购买jobs的商品
		"""
		{
			"order_id":"001",
			"pay_type":"货到付款",
			"products": [{
				"name": "商品1",
				"count": 1
			},{
				"name": "商品2",
				"count": 1
			}]
		}
		"""

	Given jobs登录系统:weapp
	When jobs对订单进行发货:weapp
		"""
		{
			"order_id": "001",
			"logistics": "off",
			"shipper": ""
		}
		"""
	Then bill在webapp查看'001'的物流信息
		"""
		{
			"order_id":"001",
			"logistics": "",
			"number":""
		}
		"""
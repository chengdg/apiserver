#_author_:王丽 2015-12-30

Feature:对有效订单进行统计
"""
	1 统计整个系统中的订单
	2 统计单个会员的数据
"""

Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp

	And jobs已添加支付方式:weapp
		"""
		[{
			"type": "微众卡支付"
		}, {
			"type": "货到付款"
		}, {
			"type": "微信支付"
		}]
		"""
	And jobs已添加商品:weapp
		"""
		[{
			"name": "商品1",
			"price": 100.00
		}, {
			"name": "商品2",
			"price": 200.00
		}]
		"""
	And bill关注jobs的公众号
	And tom关注jobs的公众号
	And nokia关注jobs的公众号
	And marry关注jobs的公众号

	#bill购买jobs的数据
	#待支付订单 001 100 
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"order_id": "001",
			"pay_type":"微信支付",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""

	#已取消订单 002 200
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"order_id": "002",
			"pay_type":"微信支付",
			"products": [{
				"name": "商品2",
				"count": 1
			}]
		}
		"""
	And bill取消订单'002'

	#待发货订单 003 100  ***
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"order_id": "003",
			"pay_type":"货到付款",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""

	#已发货订单 004 200  ***
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"order_id": "004",
			"pay_type":"货到付款",
			"products": [{
				"name": "商品2",
				"count": 1
			}]
		}
		"""
	Given jobs登录系统:weapp
	When jobs对订单进行发货:weapp
		"""
		{
			"order_no":"004",
			"logistics":"顺丰速运",
			"number":"123456789"
		}
		"""

	#已完成订单 005 100  ***
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"order_id": "005",
			"pay_type":"货到付款",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	Given jobs登录系统:weapp
	When jobs对订单进行发货:weapp
		"""
		{
			"order_no":"005",
			"logistics":"顺丰速运",
			"number":"123456789"
		}
		"""
	When bill访问jobs的webapp
	And bill确认收货订单'005'

	#tom购买待发货订单 006 200 ***
	When tom访问jobs的webapp
	And tom购买jobs的商品
		"""
		{
			"order_id": "006",
			"pay_type":"货到付款",
			"products": [{
				"name": "商品2",
				"count": 1
			}]
		}
		"""

	#nokia购买已发货订单 007 100  ***
	When nokia访问jobs的webapp
	And nokia购买jobs的商品
		"""
		{
			"order_id": "007",
			"pay_type":"货到付款",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	Given jobs登录系统:weapp
	When jobs对订单进行发货:weapp
		"""
		{
			"order_no":"007",
			"logistics":"顺丰速运",
			"number":"12356"
		}
		"""

	#marry购买已完成订单 008 200 ***
	When marry访问jobs的webapp
	And marry购买jobs的商品
		"""
		{
			"order_id": "008",
			"pay_type":"货到付款",
			"products": [{
				"name": "商品2",
				"count": 1
			}]
		}
		"""
	Given jobs登录系统:weapp
	When jobs对订单进行发货:weapp
		"""
		{
			"order_no":"008",
			"logistics":"顺丰速运",
			"number":"123456789"
		}
		"""
	When marry访问jobs的webapp
	And marry确认收货订单'008'

@mall3 @order @allOrder
Scenario:1 统计整个系统有订单的：消费金额、订单数、客单价
    Given jobs登录系统:weapp
    When jobs设置筛选日期:weapp
        """
        [{
            "begin_date":"今天",
            "end_date":"今天"
        }]
        """
    
    And 查询'店铺经营概况':weapp
    Then 获得店铺经营概况数据:weapp
        """
        {
            "transaction_money": "900.00",
            "vis_price": "150.00",
            "transaction_orders": 6
        }
        """

@mall3 @order @allOrder @ztq
Scenario:2 统计单个会员有订单的：消费金额、订单数、客单价
	Given jobs登录系统:weapp
	When jobs访问'bill'会员详情:weapp
	Then jobs获得'bill'的购买信息:weapp
		"""
		{
			"purchase_amount":100.00,
			"purchase_number":1,
			"customer_price":100.00
		}
		"""


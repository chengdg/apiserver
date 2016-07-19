# watcher: wangli@weizoom.com,enchi@weizoom.com
#editor:wangli 2016.07.12

Feature: 用户手机端订单列表分页

Background:
	Given 重置'weapp'的bdd环境
	Given jobs登录系统::weapp
	And jobs已添加商品::weapp
		"""
		[{
			"name": "商品1",
			"price": 10.00
		},{
			"name": "商品2",
			"price": 20.00
		},{
			"name": "商品3",
			"price": 30.00
		}]
		"""
	#支付方式
	Given jobs已添加支付方式::weapp
		"""
		[{
			"type": "微信支付",
			"is_active": "启用"
		},{
			"type": "货到付款",
			"is_active": "启用"
		},{
			"type": "支付宝",
			"is_active": "启用"
		}]
		"""
	And bill关注jobs的公众号

	#订单:2016-03-01
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"0001",
			"date":"2016-03-01 00:00:00",
			"pay_type":"微信支付",
			"products": [{
				"name": "商品1",
				"count": 2
			}]
		}
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"00011",
			"date":"2016-03-01 00:00:00",
			"pay_type":"微信支付",
			"products": [{
				"name": "商品1",
				"count": 2
			}]
		}
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"00021",
			"date":"2016-03-01 00:00:00",
			"pay_type":"微信支付",
			"products": [{
				"name": "商品1",
				"count": 2
			}]
		}
		"""

	#订单:2016-03-02
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"0002",
			"date":"2016-03-02 00:00:00",
			"pay_type":"支付宝",
			"products": [{
				"name": "商品2",
				"count": 1
			}]
		}
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"00012",
			"date":"2016-03-02 00:00:00",
			"pay_type":"支付宝",
			"products": [{
				"name": "商品2",
				"count": 1
			}]
		}
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"00022",
			"date":"2016-03-02 00:00:00",
			"pay_type":"支付宝",
			"products": [{
				"name": "商品2",
				"count": 1
			}]
		}
		"""

	#订单:2016-03-03
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"0003",
			"date":"2016-03-03 00:00:00",
			"pay_type":"支付宝",
			"products": [{
				"name": "商品1",
				"count": 1
			},{
				"name": "商品2",
				"count": 1
			}]
		}
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"00013",
			"date":"2016-03-03 00:00:00",
			"pay_type":"支付宝",
			"products": [{
				"name": "商品1",
				"count": 1
			},{
				"name": "商品2",
				"count": 1
			}]
		}
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"00023",
			"date":"2016-03-03 00:00:00",
			"pay_type":"支付宝",
			"products": [{
				"name": "商品1",
				"count": 1
			},{
				"name": "商品2",
				"count": 1
			}]
		}
		"""

	#订单:2016-03-04
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"0004",
			"date":"2016-03-04 00:00:00",
			"pay_type":"货到付款",
			"products": [{
				"name": "商品1",
				"count": 2
			},{
				"name": "商品2",
				"count": 2
			}]
		}
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"00014",
			"date":"2016-03-04 00:00:00",
			"pay_type":"货到付款",
			"products": [{
				"name": "商品1",
				"count": 2
			},{
				"name": "商品2",
				"count": 2
			}]
		}
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"00024",
			"date":"2016-03-04 00:00:00",
			"pay_type":"货到付款",
			"products": [{
				"name": "商品1",
				"count": 2
			},{
				"name": "商品2",
				"count": 2
			}]
		}
		"""

	#订单:2016-03-05
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"0005",
			"date":"2016-03-05 00:00:00",
			"pay_type":"微信支付",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"00015",
			"date":"2016-03-05 00:00:00",
			"pay_type":"微信支付",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"00025",
			"date":"2016-03-05 00:00:00",
			"pay_type":"微信支付",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""

	#订单:2016-03-06
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"0006",
			"date":"2016-03-06 00:00:00",
			"pay_type":"支付宝",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"00016",
			"date":"2016-03-06 00:00:00",
			"pay_type":"支付宝",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"00026",
			"date":"2016-03-06 00:00:00",
			"pay_type":"支付宝",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""

@mall3 @person @appallOrder @ztq
Scenario: 1 手机端“全部”订单列表
	When bill访问jobs的webapp
	And bill设置订单列表分页查询参数
		"""
		{
			"count_per_page":6,
			"cur_page":1
		}
		"""
	Then bill查看个人中心'全部'订单列表
		"""
		[{
			"order_no":"00026",
			"status": "待支付",
			"final_price": 10.00,
			"products": [{
				"name": "商品1"
			}]
		},{
			"order_no":"00016",
			"status": "待支付",
			"final_price": 10.00,
			"products": [{
				"name": "商品1"
			}]
		},{
			"order_no":"0006",
			"status": "待支付",
			"final_price": 10.00,
			"products": [{
				"name": "商品1"
			}]
		},{
			"order_no":"00025",
			"status": "待支付",
			"final_price": 10.00,
			"products": [{
				"name": "商品1"
			}]
		},{
			"order_no":"00015",
			"status": "待支付",
			"final_price": 10.00,
			"products": [{
				"name": "商品1"
			}]
		},{
			"order_no":"0005",
			"status": "待支付",
			"final_price": 10.00,
			"products": [{
				"name": "商品1"
			}]
		}]
		"""

	And bill设置订单列表分页查询参数
		"""
		{
			"count_per_page":6,
			"cur_page":2
		}
		"""
	Then bill查看个人中心'全部'订单列表
		"""
		[{
			"order_no":"00024",
			"status": "待发货",
			"final_price": 60.00,
			"products": [{
				"name": "商品1"
			},{
				"name": "商品2"
			}]
		},{
			"order_no":"00014",
			"status": "待发货",
			"final_price": 60.00,
			"products": [{
				"name": "商品1"
			},{
				"name": "商品2"
			}]
		},{
			"order_no":"0004",
			"status": "待发货",
			"final_price": 60.00,
			"products": [{
				"name": "商品1"
			},{
				"name": "商品2"
			}]
		},{
			"order_no":"00023",
			"status": "待支付",
			"final_price": 30.00,
			"products": [{
				"name": "商品1"
			},{
				"name": "商品2"
			}]
		},{
			"order_no":"00013",
			"status": "待支付",
			"final_price": 30.00,
			"products": [{
				"name": "商品1"
			},{
				"name": "商品2"
			}]
		},{
			"order_no":"0003",
			"status": "待支付",
			"final_price": 30.00,
			"products": [{
				"name": "商品1"
			},{
				"name": "商品2"
			}]
		}]
		"""

	And bill设置订单列表分页查询参数
		"""
		{
			"count_per_page":6,
			"cur_page":3
		}
		"""
	Then bill查看个人中心'全部'订单列表
		"""
		[{
			"order_no":"00022",
			"status": "待支付",
			"final_price": 20.00,
			"products": [{
				"name": "商品2"
			}]
		},{
			"order_no":"00012",
			"status": "待支付",
			"final_price": 20.00,
			"products": [{
				"name": "商品2"
			}]
		},{
			"order_no":"0002",
			"status": "待支付",
			"final_price": 20.00,
			"products": [{
				"name": "商品2"
			}]
		},{
			"order_no":"00021",
			"status": "待支付",
			"final_price": 20.00,
			"products": [{
				"name": "商品1"
			}]
		},{
			"order_no":"00011",
			"status": "待支付",
			"final_price": 20.00,
			"products": [{
				"name": "商品1"
			}]
		},{
			"order_no":"0001",
			"status": "待支付",
			"final_price": 20.00,
			"products": [{
				"name": "商品1"
			}]
		}]
		"""

@mall3 @person @appallOrder @ztq
Scenario: 2 手机端“待支付”订单列表
	When bill访问jobs的webapp
	And bill设置订单列表分页查询参数
		"""
		{
			"count_per_page":6,
			"cur_page":1
		}
		"""
	Then bill查看个人中心'待支付'订单列表
		"""
		[{
			"order_no":"00026",
			"status": "待支付",
			"final_price": 10.00,
			"products": [{
				"name": "商品1"
			}]
		},{
			"order_no":"00016",
			"status": "待支付",
			"final_price": 10.00,
			"products": [{
				"name": "商品1"
			}]
		},{
			"order_no":"0006",
			"status": "待支付",
			"final_price": 10.00,
			"products": [{
				"name": "商品1"
			}]
		},{
			"order_no":"00025",
			"status": "待支付",
			"final_price": 10.00,
			"products": [{
				"name": "商品1"
			}]
		},{
			"order_no":"00015",
			"status": "待支付",
			"final_price": 10.00,
			"products": [{
				"name": "商品1"
			}]
		},{
			"order_no":"0005",
			"status": "待支付",
			"final_price": 10.00,
			"products": [{
				"name": "商品1"
			}]
		}]
		"""

	When bill设置订单列表分页查询参数
		"""
		{
			"count_per_page":6,
			"cur_page":2
		}
		"""
	Then bill查看个人中心'待支付'订单列表
		"""
		[{
			"order_no":"00023",
			"status": "待支付",
			"final_price": 30.00,
			"products": [{
				"name": "商品1"
			},{
				"name": "商品2"
			}]
		},{
			"order_no":"00013",
			"status": "待支付",
			"final_price": 30.00,
			"products": [{
				"name": "商品1"
			},{
				"name": "商品2"
			}]
		},{
			"order_no":"0003",
			"status": "待支付",
			"final_price": 30.00,
			"products": [{
				"name": "商品1"
			},{
				"name": "商品2"
			}]
		},{
			"order_no":"00022",
			"status": "待支付",
			"final_price": 20.00,
			"products": [{
				"name": "商品2"
			}]
		},{
			"order_no":"00012",
			"status": "待支付",
			"final_price": 20.00,
			"products": [{
				"name": "商品2"
			}]
		},{
			"order_no":"0002",
			"status": "待支付",
			"final_price": 20.00,
			"products": [{
				"name": "商品2"
			}]
		}]
		"""

@mall3 @person @appallOrder
Scenario: 3 手机端“待发货”订单列表
	When bill访问jobs的webapp
	#支付订单：
	When bill使用支付方式'微信支付'进行支付订单'0001'
	When bill使用支付方式'支付宝'进行支付订单'0002'
	When bill使用支付方式'支付宝'进行支付订单'0003'
	When bill使用支付方式'微信支付'进行支付订单'0005'

	When bill设置订单列表分页查询参数
		"""
		{
			"count_per_page":6,
			"cur_page":1
		}
		"""
	Then bill查看个人中心'待发货'订单列表
		"""
		[{
			"order_no":"0005",
			"status": "待发货",
			"final_price": 10.00,
			"products": [{
				"name": "商品1"
			}]
		},{
			"order_no":"00024",
			"status": "待发货",
			"final_price": 60.00,
			"products": [{
				"name": "商品1"
			},{
				"name": "商品2"
			}]
		},{
			"order_no":"00014",
			"status": "待发货",
			"final_price": 60.00,
			"products": [{
				"name": "商品1"
			},{
				"name": "商品2"
			}]
		},{
			"order_no":"0004",
			"status": "待发货",
			"final_price": 60.00,
			"products": [{
				"name": "商品1"
			},{
				"name": "商品2"
			}]
		},{
			"order_no":"0003",
			"status": "待发货",
			"final_price": 30.00,
			"products": [{
				"name": "商品1"
			},{
				"name": "商品2"
			}]
		},{
			"order_no":"0002",
			"status": "待发货",
			"final_price": 20.00,
			"products": [{
				"name": "商品2"
			}]
		}]
		"""
	When bill设置订单列表分页查询参数
		"""
		{
			"count_per_page":6,
			"cur_page":2
		}
		"""
	Then bill查看个人中心'待发货'订单列表
		"""
		[{
			"order_no":"0001",
			"status": "待发货",
			"final_price": 20.00,
			"products": [{
				"name": "商品1"
			}]
		}]
		"""

@mall3 @person @appallOrder @ztq
Scenario: 4 手机端“待收货”订单列表
	When bill访问jobs的webapp
	#支付订单：
	When bill使用支付方式'微信支付'进行支付订单'0001'
	When bill使用支付方式'支付宝'进行支付订单'0002'
	When bill使用支付方式'支付宝'进行支付订单'0003'
	When bill使用支付方式'微信支付'进行支付订单'0005'

	#对订单进行发货
	Given jobs登录系统::weapp
	When jobs对订单进行发货::weapp
		"""
		{
			"order_no": "0005",
			"logistics": "申通快递",
			"number": "229388967650",
			"shipper": "jobs"
		}
		"""
	When jobs对订单进行发货::weapp
		"""
		{
			"order_no": "0004",
			"logistics": "圆通快递",
			"number": "229388967650",
			"shipper": "jobs"
		}
		"""
	When jobs对订单进行发货::weapp
		"""
		{
			"order_no": "0003",
			"logistics": "顺丰速运",
			"number": "229388967650",
			"shipper": "jobs"
		}
		"""
	When jobs对订单进行发货::weapp
		"""
		{
			"order_no": "0002",
			"logistics": "off",
			"shipper": ""
		}
		"""
	When jobs对订单进行发货::weapp
		"""
		{
			"order_no": "0001",
			"logistics": "off",
			"shipper": ""
		}
		"""


	When bill访问jobs的webapp
	When bill设置订单列表分页查询参数
		"""
		{
			"count_per_page":2,
			"cur_page":1
		}
		"""
	Then bill查看个人中心'待收货'订单列表
		"""
		[{
			"order_no":"0005",
			"status": "待收货",
			"final_price": 10.00,
			"products": [{
				"name": "商品1"
			}]
		},{
			"order_no":"0004",
			"status": "待收货",
			"final_price": 60.00,
			"products": [{
				"name": "商品1"
			},{
				"name": "商品2"
			}]
		}]
		"""
	When bill设置订单列表分页查询参数
		"""
		{
			"count_per_page":2,
			"cur_page":2
		}
		"""
	Then bill查看个人中心'待收货'订单列表
		"""
		[{
			"order_no":"0003",
			"status": "待收货",
			"final_price": 30.00,
			"products": [{
				"name": "商品1"
			},{
				"name": "商品2"
			}]
		},{
			"order_no":"0002",
			"status": "待收货",
			"final_price": 20.00,
			"products": [{
				"name": "商品2"
			}]
		}]
		"""
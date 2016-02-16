# __author__ : "王丽" 2016-02-02
Feature:订单筛选
"""
	Jobs能通过管理系统为管理用户订单
"""

Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
	And bill关注jobs的公众号
	And tom关注jobs的公众号
	Given jobs登录系统:weapp
	And jobs已添加支付方式:weapp
		"""
		[{
			"type": "微信支付",
			"is_active": "启用"
		}, {
			"type": "微信支付",
			"is_active": "启用"
		}, {
			"type": "货到付款",
			"is_active": "启用"
		}]
		"""
	And jobs已添加商品:weapp
		"""
		[{
			"name": "商品1",
			"price": 9.9,
			"pay_interfaces":[{
				"type": "在线支付"
			}, {
				"type": "货到付款"
			}]
		}, {
			"name": "商品2",
			"price": 9.9,
			"pay_interfaces":[{
				"type": "在线支付"
			}]
		}]
		"""
	And jobs已有的订单:weapp
		"""
		[{
			"order_no": "00003",
			"member": "tom",
			"status": "待发货",
			"order_time": "2014-10-03 12:00:00",
			"payment_time":"2014-10-03 12:00:00",
			"methods_of_payment": "货到付款",
			"sources": "商城",
			"products": [{
				"name": "商品1",
				"count": 1
			}],
			"ship_name": "tom",
			"ship_tel": "13711223344",
			"is_first_order":"true"
		},{
			"order_no": "00004",
			"member": "bill",
			"status": "已取消",
			"order_time": "2014-10-04 12:00:00",
			"payment_time":"2014-10-04 12:00:00",
			"methods_of_payment": "优惠抵扣",
			"sources": "商城",
			"products": [{
				"name": "商品1",
				"count": 1
			}],
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"is_first_order":"true"
		},{
			"order_no": "00005",
			"member": "tom",
			"status": "已完成",
			"order_time": "2014-10-05 12:00:00",
			"payment_time":"2014-10-05 13:00:00",
			"methods_of_payment": "微信支付",
			"sources": "商城",
			"products": [{
				"name": "商品2",
				"count": 1
			}],
			"ship_name": "tom",
			"ship_tel": "13711223344",
			"logistics": "顺丰",
			"number": "123",
			"shipper": "",
			"is_first_order":"false"
		},{
			"order_no": "00006",
			"member": "tom",
			"status": "已发货",
			"order_time": "2014-10-06 12:00:00",
			"payment_time":"2014-10-06 12:00:00",
			"methods_of_payment": "优惠抵扣",
			"sources": "商城",
			"products": [{
				"name": "商品2",
				"count": 1
			}],
			"ship_name": "tom",
			"ship_tel": "13711223344",
			"logistics": "顺丰",
			"number": "123",
			"shipper": "",
			"is_first_order":"false"
		},{
			"order_no": "00007",
			"member": "bill",
			"status": "待发货",
			"order_time": "2014-10-07 12:00:00",
			"payment_time":"2014-10-07 13:00:00",
			"methods_of_payment": "支付宝",
			"sources": "商城",
			"products": [{
				"name": "商品1",
				"count": 1
			}],
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"is_first_order":"false"
		},{
			"order_no": "00008",
			"member": "bill",
			"status": "待支付",
			"order_time": "2014-10-08 12:00:00",
			"payment_time":"",
			"methods_of_payment": "微信支付",
			"sources": "商城",
			"products": [{
				"name": "商品2",
				"count": 1
			}],
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"is_first_order":"false"
		}]
		"""

@mall3 @order @allOrder
Scenario:1 按照【订单类型】进行筛选
	#筛选“订单类型”内容为“全部、首单、非首单”
	#"全部":筛选出所有订单；"首单"：筛选出带有首单标记的订单；"非首单":筛选出没有首单标记的订单

	Given jobs登录系统:weapp
	#全部
	When jobs根据给定条件查询订单:weapp
		"""
		{
			"order_type": "全部"
		}
		"""
	Then jobs可以看到订单列表:weapp
		"""
		[{
			"order_no": "00008",
			"member": "bill",
			"status": "待支付",
			"order_time": "2014-10-08 12:00:00",
			"payment_time":"",
			"methods_of_payment": "微信支付",
			"sources": "商城",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"is_first_order":"false"
		},{
			"order_no": "00007",
			"member": "bill",
			"status": "待发货",
			"order_time": "2014-10-07 12:00:00",
			"payment_time":"2014-10-07 13:00:00",
			"methods_of_payment": "支付宝",
			"sources": "商城",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"is_first_order":"false"
		},{
			"order_no": "00006",
			"member": "tom",
			"status": "已发货",
			"order_time": "2014-10-06 12:00:00",
			"payment_time":"2014-10-06 12:00:00",
			"methods_of_payment": "优惠抵扣",
			"sources": "商城",
			"ship_name": "tom",
			"ship_tel": "13811223344",
			"is_first_order":"false"
		},{
			"order_no": "00005",
			"member": "tom",
			"status": "已完成",
			"order_time": "2014-10-05 12:00:00",
			"payment_time":"2014-10-05 13:00:00",
			"methods_of_payment": "微信支付",
			"sources": "商城",
			"ship_name": "tom",
			"ship_tel": "13711223344",
			"is_first_order":"false"
		},{
			"order_no": "00004",
			"member": "bill",
			"status": "已取消",
			"order_time": "2014-10-04 12:00:00",
			"payment_time":"2014-10-04 12:00:00",
			"methods_of_payment": "优惠抵扣",
			"sources": "商城",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"is_first_order":"true"
		},{
			"order_no": "00003",
			"member": "tom",
			"status": "待发货",
			"order_time": "2014-10-03 12:00:00",
			"payment_time":"2014-10-03 12:00:00",
			"methods_of_payment": "货到付款",
			"sources": "商城",
			"ship_name": "tom",
			"ship_tel": "13711223344",
			"is_first_order":"true"
		}]
		"""

	#首单
	When jobs根据给定条件查询订单:weapp
		"""
		{
			"order_type": "首单"
		}
		"""
	Then jobs可以看到订单列表:weapp
		"""
		[{
			"order_no": "00004",
			"member": "bill",
			"status": "已取消",
			"order_time": "2014-10-04 12:00:00",
			"payment_time":"2014-10-04 12:00:00",
			"methods_of_payment": "优惠抵扣",
			"sources": "商城",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"is_first_order":"true"
		},{
			"order_no": "00003",
			"member": "tom",
			"status": "待发货",
			"order_time": "2014-10-03 12:00:00",
			"payment_time":"2014-10-03 12:00:00",
			"methods_of_payment": "货到付款",
			"sources": "商城",
			"ship_name": "tom",
			"ship_tel": "13711223344",
			"is_first_order":"true"
		}]
		"""

	#非首单
	When jobs根据给定条件查询订单:weapp
		"""
		{
			"order_type": "非首单"
		}
		"""
	Then jobs可以看到订单列表:weapp
		"""
		[{
			"order_no": "00008",
			"member": "bill",
			"status": "待支付",
			"order_time": "2014-10-08 12:00:00",
			"payment_time":"",
			"methods_of_payment": "微信支付",
			"sources": "商城",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"is_first_order":"false"
		},{
			"order_no": "00007",
			"member": "bill",
			"status": "待发货",
			"order_time": "2014-10-07 12:00:00",
			"payment_time":"2014-10-07 13:00:00",
			"methods_of_payment": "支付宝",
			"sources": "商城",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"is_first_order":"false"
		},{
			"order_no": "00006",
			"member": "tom",
			"status": "已发货",
			"order_time": "2014-10-06 12:00:00",
			"payment_time":"2014-10-06 12:00:00",
			"methods_of_payment": "优惠抵扣",
			"sources": "商城",
			"ship_name": "tom",
			"ship_tel": "13711223344",
			"is_first_order":"false"
		},{
			"order_no": "00005",
			"member": "tom",
			"status": "已完成",
			"order_time": "2014-10-05 12:00:00",
			"payment_time":"2014-10-05 13:00:00",
			"methods_of_payment": "微信支付",
			"sources": "商城",
			"ship_name": "tom",
			"ship_tel": "13711223344",
			"is_first_order":"false"
		}]
		"""

@mall3 @order @allOrder
Scenario:2 混合条件进行筛选
	Given jobs登录系统:weapp
	When jobs根据给定条件查询订单:weapp
		"""
		{
			"order_no": "00003",
			"ship_name": "tom",
			"ship_tel": "13711223344",
			"product_name": "商品",
			"date_interval": "2014-10-03|2014-10-04",
			"date_interval_type": "付款时间",
			"pay_type": "货到付款",
			"express_number": "",
			"order_source": "商城",
			"order_status": "待发货",
			"isUseWeizoomCard": "false",
			"order_type": "首单"
		}
		"""
	Then jobs可以看到订单列表:weapp
		"""
		[{
			"order_no": "00003",
			"member": "tom",
			"status": "待发货",
			"order_time": "2014-10-03 12:00:00",
			"payment_time":"2014-10-03 12:00:00",
			"methods_of_payment": "货到付款",
			"sources": "商城",
			"ship_name": "tom",
			"ship_tel": "13711223344",
			"is_first_order":"true"
		}]
		"""

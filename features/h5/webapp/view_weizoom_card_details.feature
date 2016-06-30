#_author_:张三香 2016.06.30

Feature:我的卡包-查看微众卡详情
	"""
		1、微众卡包列表点击微众卡的【详情】，页面跳转到微众卡使用详情页面,页面title为'微众卡'
		2、页面字段信息:
			'微众卡号':显示微众卡的卡号
			'密码':*****[查看]
			'余额'：显示当前卡内余额（保留两位小数，数字前显示钱的符号）
			'有效期至xxxx-xx-xx'（显示卡的截止日期）
			使用详情：
				'时间':微众卡扣款或退款的时间（xxxx/xx/xx xx:xx:xx）
				'明细':-20.00或+10.00（微众卡扣款或退款的数额）
				'订单来源'：公众号名称，最多显示12个字，订单号:xxxxx
		3、'使用详情'显示规则：
			排序为倒序
			每条明细的时间是微众卡扣款或回款的时间
			微众卡的每笔交易都显示在明细当中，当同一订单出现两条明细时均要显示出来
	"""

Background:
	Given 重置'weapp'的bdd环境
	Given 重置'weizoom_card'的bdd环境
	#自营平台jobs的数据
	Given 设置jobs为自营平台账号::weapp
	Given 添加jobs店铺名称为'jobs商家'::weapp
	Given jobs登录系统::weapp
	And jobs已添加供货商::weapp
		"""
		[{
			"name": "供货商 a",
			"responsible_person": "张大众",
			"supplier_tel": "15211223344",
			"supplier_address": "北京市海淀区海淀科技大厦",
			"remark": "备注"
		}]
		"""
	And jobs已添加支付方式::weapp
		"""
		[{
			"type": "货到付款",
			"is_active": "启用"
		},{
			"type": "微信支付",
			"is_active": "启用"
		},{
			"type": "支付宝",
			"is_active": "启用"
		}]
		"""
	When jobs开通使用微众卡权限::weapp
	When jobs添加支付方式::weapp
		"""
		[{
			"type": "微众卡支付",
			"description": "我的微众卡支付",
			"is_active": "启用"
		}]
		"""
	Given jobs已添加商品::weapp
		"""
		[{
			"name":"jobs商品1",
			"product_type":"普通商品",
			"supplier": "供货商a",
			"purchase_price": 9.99,
			"price": 10.00,
			"weight": 1.0,
			"stock_type": "无限",
			"pay_interfaces":
				[{
					"type": "在线支付"
				},{
					"type": "货到付款"
				}],
			"detail":"普通商品1的详情",
			"status":"在售"
		}]
		"""
	#普通商家nokia
	Given 添加nokia店铺名称为'nokia商家'::weapp
	Given nokia登录系统::weapp
	And nokia已添加支付方式::weapp
		"""
		[{
			"type": "货到付款",
			"is_active": "启用"
		},{
			"type": "微信支付",
			"is_active": "启用"
		},{
			"type": "支付宝",
			"is_active": "启用"
		}]
		"""
	When nokia开通使用微众卡权限::weapp
	Given nokia已添加商品::weapp
		"""
		[{
			"name":"nokia商品1",
			"price": 10.00
		}]
		"""

	When bill关注jobs的公众号
	When bill关注nokia的公众号
	When tom关注jobs的公众号

	#创建微众卡
	Given test登录管理系统::weizoom_card
	When test新建通用卡::weizoom_card
		"""
		[{
			"name":"15元微众卡",
			"prefix_value":"101",
			"type":"virtual",
			"money":"15.00",
			"num":"3",
			"comments":"微众卡"
		}]
		"""

	#微众卡审批出库
	When test下订单::weizoom_card
		"""
		[{
			"card_info":[{
				"name":"15元微众卡",
				"order_num":"3",
				"start_date":"2016-06-16 00:00",
				"end_date":"2026-06-16 00:00"
			}],
			"order_info":{
				"order_id":"0001"
				}
		}]
		"""

	#激活微众卡
	When test批量激活订单'0001'的卡::weizoom_card

	#绑定微众卡101000001
	When bill访问jobs的webapp
	When bill绑定微众卡
		"""
		{
			"binding_date":"2016-06-16",
			"binding_shop":"jobs",
			"weizoom_card_info":
				{
					"id":"101000001",
					"password":"1234567"
				}
		}
		"""
	When bill访问nokia的webapp
	When bill绑定微众卡
		"""
		{
			"binding_date":"2016-06-16",
			"binding_shop":"nokia",
			"weizoom_card_info":
				{
					"id":"101000001",
					"password":"1234567"
				}
		}
		"""
	When tom访问jobs的webapp
	When tom绑定微众卡
		"""
		{
			"binding_date":"2016-06-16",
			"binding_shop":"jobs",
			"weizoom_card_info":
				{
					"id":"101000001",
					"password":"1234567"
				}
		}
		"""

@weizoom_card @weizoon_card_detail 
Scenario:1 查看微众卡详情,使用详情记录为空
	When bill访问jobs的webapp
	Then bill能获得微众卡'101000001'的详情信息
		"""
		{
			"id":"101000001",
			"password":"1234567",
			"card_end_date":"2026-06-16",
			"card_remain_value":10.00,
			"use_info":[]
		}
		"""

	When bill访问nokia的webapp
	Then bill能获得微众卡'101000001'的详情信息
		"""
		{
			"id":"101000001",
			"password":"1234567",
			"card_end_date":"2026-06-16",
			"card_remain_value":10.00,
			"use_info":[]
		}
		"""

	When tom访问jobs的webapp
	Then tom能获得微众卡'101000001'的详情信息
		"""
		{
			"id":"101000001",
			"password":"1234567",
			"card_end_date":"2026-06-16",
			"card_remain_value":10.00,
			"use_info":[]
		}
		"""

@weizoom_card @weizoon_card_detail 
Scenario:2 查看微众卡详情,使用详情记录非空
	#微众卡消费记录
	#001-下单（-10.00）-取消（+10.00）
		When bill访问jobs的webapp
		When bill购买jobs的商品
			"""
			{
				"order_id":"001",
				"date":"2016-06-11 00:00:00",
				"pay_type": "微信支付",
				"products":[{
					"name":"jobs商品1",
					"price":10.00,
					"count":1
				}],
				"weizoom_card":[{
					"card_name":"101000001",
					"card_pass":"1234567"
				}]
			}
			"""
		Given jobs登录系统
		When jobs'取消'订单'001'于'2016-06-11 10:00:00'
	#002-下单（-10.00）
		When tom访问jobs的webapp
		When tom购买jobs的商品
			"""
			{
				"order_id":"002",
				"date":"2016-06-12 00:00:00",
				"pay_type": "微信支付",
				"products":[{
					"name":"jobs商品1",
					"price":10.00,
					"count":1
				}],
				"weizoom_card":[{
					"card_name":"101000001",
					"card_pass":"1234567"
				}]
			}
			"""
	#003-下单（-5.00）-退款完成（+5.00）
		When bill访问nokia的webapp
		When bill购买nokia的商品
			"""
			{
				"order_id":"003",
				"date":"2016-06-13 00:00:00",
				"pay_type": "微信支付",
				"products":[{
					"name":"nokia商品1",
					"price":10.00,
					"count":1
				}],
				"weizoom_card":[{
					"card_name":"101000001",
					"card_pass":"1234567"
				}]
			}
			"""
		When bill使用支付方式'微信支付'进行支付订单'003'于'2016-06-13 10:00:00'
		Given nokia登录系统
		When nokia'申请退款'订单'003'于'2016-06-13 10:10:00'
		When nokia通过财务审核'退款成功'订单'003'于'2016-06-13 10:20:00'

	#查看微众卡101000001的详情
	When bill访问jobs的webapp
	Then bill能获得微众卡'101000001'的详情信息
		"""
		{
			"id":"101000001",
			"password":"1234567",
			"card_end_date":"2026-06-16",
			"card_remain_value":5.00,
			"use_details":
				[{
					"time":"2016-06-13 10:20:00",
					"detail":"+5.00",
					"order_info":"nokia商家,003"
				},{
					"time":"2016-06-13 10:00:00",
					"detail":"-5.00",
					"order_info":"nokia商家,003"
				},{
					"time":"2016-06-12 10:00:00",
					"detail":"-10.00",
					"order_info":"jobs商家,002"
				},{
					"time":"2016-06-11 10:00:00",
					"detail":"+10.00",
					"order_info":"jobs商家,001"
				},{
					"time":"2016-06-11 00:00:00",
					"detail":"-10.00",
					"order_info":"jobs商家,001"
				}]
		}
		"""

	When tom访问jobs的webapp
	Then tom能获得微众卡'101000001'的详情信息
		"""
		{
			"id":"101000001",
			"password":"1234567",
			"card_end_date":"2026-06-16",
			"card_remain_value":5.00,
			"use_details":
				[{
					"time":"2016-06-13 10:20:00",
					"detail":"+5.00",
					"order_info":"nokia商家,003"
				},{
					"time":"2016-06-13 10:00:00",
					"detail":"-5.00",
					"order_info":"nokia商家,003"
				},{
					"time":"2016-06-12 10:00:00",
					"detail":"-10.00",
					"order_info":"jobs商家,002"
				},{
					"time":"2016-06-11 10:00:00",
					"detail":"+10.00",
					"order_info":"jobs商家,001"
				},{
					"time":"2016-06-11 00:00:00",
					"detail":"-10.00",
					"order_info":"jobs商家,001"
				}]
		}
		"""

	When bill访问nokia的webapp
	Then bill能获得微众卡'101000001'的详情信息
		"""
		{
			"id":"101000001",
			"password":"1234567",
			"card_end_date":"2026-06-16",
			"card_remain_value":5.00,
			"use_details":
				[{
					"time":"2016-06-13 10:20:00",
					"detail":"+5.00",
					"order_info":"nokia商家,003"
				},{
					"time":"2016-06-13 10:00:00",
					"detail":"-5.00",
					"order_info":"nokia商家,003"
				},{
					"time":"2016-06-12 10:00:00",
					"detail":"-10.00",
					"order_info":"jobs商家,002"
				},{
					"time":"2016-06-11 10:00:00",
					"detail":"+10.00",
					"order_info":"jobs商家,001"
				},{
					"time":"2016-06-11 00:00:00",
					"detail":"-10.00",
					"order_info":"jobs商家,001"
				}]
		}
		"""



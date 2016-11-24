# __author__ : "田丰敏"

Feature:会员使用会员钱包支付订单
	"""
	会员使用会员钱包购买商品流程：
		微众卡管理系统：
			1、创建VIP会员套餐
			2、创建会员卡，关联VIP会员套餐
			3、审批发卡，选择会员卡
			4、获得出库列表，激活？

		会员：
			1、会员进入个人中心
			2、点击开通VIP会员
			3、绑定手机号，购买VIP会员卡，支付成功，获得返现次数
			4、会员查看会员钱包，购买后首月自动充值（100）
			5、会员购买商品，编辑订单页面，优先使用积分和优惠券，然后是会员钱包、微众卡、现金
			6、VIP会员默认勾选会员钱包，订单下方显示会员钱包抵扣金额
			7、使用会员钱包支付订单，订单详情页下方显示会员钱包抵扣金额

		场景：
			1、会员使用会员钱包支付全部金额
			2、会员使用积分+会员钱包支付全部金额
			3、会员使用优惠券+会员钱包支付全部金额
			4、会员使用微众卡+会员钱包支付全部金额
			5、会员使用现金+会员钱包支付全部金额
			6、会员使用积分+会员钱包+微众卡+现金支付全部金额
			7、会员使用优惠券+会员钱包+微众卡+现金支付全部金额

		商品：有运费，无运费

		备注：
			1、会员提交订单，判断该会员是否开通VIP年卡或半年卡，如果没有开通则不显示会员钱包支付，开通显示会员钱包支付，默认勾选抵扣最高金额
			2、编辑订单页面，如果选择积分或优惠券抵扣，会员钱包支付金额自动变化，优先使用积分或优惠券
			3、如果会员钱包余额为0时，默认不勾选，显示0.00元可用
	"""
Background:
	Given 重置'weapp'的bdd环境
	Given 设置jobs为自营平台账号::weapp
	Given jobs登录系统::weapp

	#说明：以微众商城自建商品的形式创建供货商和商品的
	And jobs已添加供货商::weapp
		"""
		[{
			"name": "微众商城",
			"responsible_person": "张大众",
			"supplier_tel": "15211223344",
			"supplier_address": "北京市海淀区海淀科技大厦",
			"remark": "备注"
		}]
		"""
	When jobs已添加支付方式::weapp
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
	When jobs设定会员积分策略
		"""
		{
			"integral_each_yuan": 1,
			"use_ceiling": 50
		}
		"""
	#此处创建商品相当于微众商城自建商品（同步商品还需要从panda同步）
	And jobs已添加商品
		"""
		[{
			"name": "普通商品1",
			"price": 10.00,
			"supplier": "微众商城"
		},{
			"name": "普通商品2",
			"price": 100.00,
			"postage": 10.00,
			"supplier": "微众商城"
		},{
			"name": "普通商品3",
			"price": 300.00,
			"supplier": "微众商城"
		}]
		"""
	When jobs添加优惠券规则
		"""
		[{
			"name": "全体券1",
			"money": 5.00,
			"start_date": "1天前",
			"end_date": "10天后",
			"coupon_id_prefix": "coupon1_id_"
		}]
		"""

	#添加会员卡套餐
	Given test登录管理系统::weizoom_card
	When test添加会员卡套餐::weizoom_card
		"""
		{
			"package_name": "年卡1",
			"package_type": "年卡",
			"package_refund_number": "12",
			"open_pay_cost": "365.00",
			"first_purchase_amount": "100.00",
			"VIP_member_refund": {
				"every_other_days": "30",
				"refund_amount": "100.00"
			},
			"package_value": "1200.00"
		}
		"""
	When test新建会员卡::weizoom_card
		"""
		{
			"name": "年卡会员卡",
			"prefix_value": "777",
			"card_package": "年卡1",
			"exclusive_stores": ["jobs"],
			"num":"100",
			"remark":"会员卡"
		}
		"""
	When test下订单::weizoom_card
			"""
			[{
				"card_info":[{
					"name":"年卡会员卡",
					"order_num":"10",
					"start_date":"2016-11-23 00:00",
					"end_date":"2020-11-23 00:00"
				}],
				"order_info":{
					"order_id":"0001"
				}
			}]
			"""
	And test批量激活订单'0001'的卡::weizoom_card

#创建微众卡
	When test新建通用卡::weizoom_card
		"""
		[{
			"name":"微众卡1",
			"prefix_value":"220",
			"type":"virtual",
			"money":"100.00",
			"num":"5",
			"comments":"微众卡1"
		}]
		"""
#微众卡审批出库
	When test下订单::weizoom_card
		"""
		[{
			"card_info":[{
				"name":"微众卡1",
				"order_num":"1",
				"start_date":"2016-11-23 00:00",
				"end_date":"2019-11-23 00:00"
			}],
			"order_info":{
				"order_id":"0002"
				}
		}]
		"""
	And test批量激活订单'0002'的卡::weizoom_card

	Given bill关注jobs的公众号
	When bill访问jobs的webapp
	When bill绑定微众卡
		"""
		{
			"binding_date":"2016-11-23",
			"binding_shop":"jobs",
			"weizoom_card_info":
				{
					"id":"220000001",
					"password":"1234567"
				}
		}
		"""

#会员购买VIP年卡，首次充值100元，会员钱包月100元
	When bill访问jobs的webapp
	When bill获取手机绑定验证码'15194857825'
	When bill使用验证码绑定手机
		"""
		{
			"phone": 15194857825
		}
		"""
	When bill开通会员卡
		"""
		{
			"pay_type":"微信支付",
			"name": "年卡会员卡",
			"id": "777000001"
		}
		"""


Scenario:1 会员使用会员钱包支付全部金额
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"0000001",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "微信支付",
			"products": [{
				"name": "普通商品1",
				"price":10.00,
				"count": 1
			}],
			"member_purse":10.00
		}
		"""
	Then bill成功创建订单
		"""
		{
			"order_no":"0000001",
			"status": "待发货",
			"final_price": 0.00,
			"product_price": 10.00,
			"member_purse":10.00,
			"products": [{
				"name": "普通商品1",
				"price":10.00,
				"count": 1
			}]
		}
		"""

#会员访问会员钱包，剩余金额是90.00元
	When bill浏览jobs的webapp的会员卡
	Then bill获得会员卡
		"""
		{
			"name": "年卡会员卡",
			"id": "777000001",
			"refund_surplus_number": "11",
			"member_purse": "90.00"
		}
		"""


Scenario:2 会员使用积分和会员钱包支付全部金额
	When bill访问jobs的webapp
	When bill获得jobs的5会员积分
	When bill购买jobs的商品
		"""
		{
			"order_id":"0000002",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "微信支付",
			"integral_money":5.00,
			"integral":5.00,
			"products": [{
				"name": "普通商品1",
				"price":10.00,
				"count": 1
			}],
			"member_purse":5.00
		}
		"""
	Then bill成功创建订单
		"""
		{
			"order_no":"0000002",
			"status": "待发货",
			"final_price": 0.00,
			"product_price": 10.00,
			"integral_money":5.00,
			"integral":5.00,
			"member_purse":5.00,
			"products": [{
				"name": "普通商品1",
				"price":10.00,
				"count": 1
			}]
		}
		"""
#会员访问会员钱包，剩余金额是95.00元
	When bill浏览jobs的webapp的会员卡
	Then bill获得会员卡
		"""
		{
			"name": "年卡会员卡",
			"id": "777000001",
			"refund_surplus_number": "11",
			"member_purse": "95.00"
		}
		"""

Scenario:3 会员使用优惠券和会员钱包支付全部金额
	Given jobs登录系统
	When jobs为会员发放优惠券
		"""
		{
			"name": "全体券1",
			"count": 1,
			"members": ["bill"]
		}
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"0000003",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "微信支付",
			"products": [{
				"name": "普通商品1",
				"price":10.00,
				"count": 1
			}],
			"coupon": "coupon1_id_1",
			"member_purse":5.00
		}
		"""
	Then tom成功创建订单
		"""
		{
			"order_no":"0000003",
			"status": "待发货",
			"final_price": 0.00,
			"product_price": 10.00,
			"coupon_money": 5.00,
			"member_purse":5.00
			"products": [{
				"name": "普通商品1",
				"price":10.00,
				"count": 1
			}]
		}
		"""
#会员访问会员钱包，剩余金额是90.00元
	When bill浏览jobs的webapp的会员卡
	Then bill获得会员卡
		"""
		{
			"name": "年卡会员卡",
			"id": "777000001",
			"refund_surplus_number": "11",
			"member_purse": "90.00"
		}
		"""

Scenario:4 会员使用微众卡和会员钱包支付全部金额
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"0000004",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "微信支付",
			"products":[{
				"name":"普通商品2",
				"price":100.00,
				"count":1
			}],
			"member_purse":100.00,
			"weizoom_card":[{
				"card_name":"220000001",
				"card_pass":"1234567"
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"order_no":"0000004",
			"status": "待发货",
			"final_price": 0.00,
			"product_price": 100.00,
			"weizoom_card_money":10.00,
			"products":[{
				"name":"普通商品2",
				"price":100.00,
				"count":1
			}],
			"postage":10.00,
			"member_purse":100.00,
		}
		"""
#会员访问会员钱包，剩余金额是0.00元
	When bill浏览jobs的webapp的会员卡
	Then bill获得会员卡
		"""
		{
			"name": "年卡会员卡",
			"id": "777000001",
			"refund_surplus_number": "11",
			"member_purse": "0.00"
		}
		"""

Scenario:5 会员使用现金支付和会员钱包全部金额
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"0000005",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "微信支付",
			"products": [{
				"name": "普通商品2",
				"price":100.00,
				"count": 1
			}],
			"member_purse":100.00
		}
		"""
	Then bill成功创建订单
		"""
		{
			"order_no":"0000005",
			"status": "待支付",
			"final_price": 10.00,
			"product_price": 100.00,
			"products": [{
				"name": "普通商品2",
				"price":100.00,
				"count": 1
			}],
			"postage":10.00,
			"member_purse":100.00
		}
		"""
#会员访问会员钱包，剩余金额是0.00元
	When bill浏览jobs的webapp的会员卡
	Then bill获得会员卡
		"""
		{
			"name": "年卡会员卡",
			"id": "777000001",
			"refund_surplus_number": "11",
			"member_purse": "0.00"
		}
		"""

Scenario:6 会员使用积分+会员钱包+微众卡+现金支付全部金额
	When bill访问jobs的webapp
	When bill获得jobs的10会员积分
	When bill购买jobs的商品
		"""
		{
			"order_id":"0000006",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "微信支付",
			"integral_money":10.00,
			"integral":10.00,
			"products": [{
				"name": "普通商品3",
				"price":300.00,
				"count": 1
			}],
			"member_purse":100.00,
			"weizoom_card":[{
				"card_name":"220000002",
				"card_pass":"1234567"
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"order_no":"0000006",
			"status": "待支付",
			"final_price": 90.00,
			"product_price": 300.00,
			"integral_money":10.00,
			"integral":10.00,
			"weizoom_card_money":100.00,
			"member_purse":100.00
			"products": [{
				"name": "普通商品3",
				"price":300.00,
				"count": 1
			}]
		}
		"""
#会员访问会员钱包，剩余金额是0.00元
	When bill浏览jobs的webapp的会员卡
	Then bill获得会员卡
		"""
		{
			"name": "年卡会员卡",
			"id": "777000001",
			"refund_surplus_number": "11",
			"member_purse": "0.00"
		}
		"""


Scenario:7 会员使用优惠券+会员钱包+微众卡+现金支付全部金额
	Given jobs登录系统
	When jobs为会员发放优惠券
		"""
		{
			"name": "全体券1",
			"count": 1,
			"members": ["bill"]
		}
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"0000006",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "微信支付",
			"products": [{
				"name": "普通商品3",
				"price":300.00,
				"count": 1
			}],
			"coupon": "coupon1_id_1",
			"member_purse":100.00,
			"weizoom_card":[{
				"card_name":"220000002",
				"card_pass":"1234567"
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"order_no":"0000006",
			"status": "待支付",
			"final_price": 95.00,
			"product_price": 300.00,
			"coupon_money": 5.00,
			"weizoom_card_money":100.00,
			"member_purse":100.00
			"products": [{
				"name": "普通商品3",
				"price":300.00,
				"count": 1
			}]
		}
		"""
#会员访问会员钱包，剩余金额是0.00元
	When bill浏览jobs的webapp的会员卡
	Then bill获得会员卡
		"""
		{
			"name": "年卡会员卡",
			"id": "777000001",
			"refund_surplus_number": "11",
			"member_purse": "0.00"
		}
		"""
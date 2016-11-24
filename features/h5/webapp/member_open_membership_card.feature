# __author__ : "冯雪静"

Feature: 在webapp中开通会员卡
	"""
	手机端开通会员卡
		流程：
			微众卡系统->微众卡系统添加会员卡套餐-创建会员卡(选择会员卡套餐，专属商家自营平台)-审批发卡(会员卡出库)
			没有开通会员卡的会员webapp个人中心->进入个人中心页面显示引导开通会员卡页面-点击VIP会员进入购买VIP会员的页面
			已出库的会员卡关联了此自营平台几种就显示几种，会员只能选择一种进行开通-会员选择(学生卡/家庭卡/年卡)进行开通(如会员没有关联手机号，进入关联手机号页面)
			如已关联手机号，直接显示选择支付方式页面(一期只支持微信支付)-支付成功后显示交易成功页面(显示可返现n次)-自动激活会员卡、绑定
			再次进入个人中心页面不再显示引导页面-点击VIP会员-显示VIP会员卡(显示卡号，余额)
			1.此商户关联的所有的会员卡被激活后，都会在会员的个人中心-VIP会员-未开通的会员列表显示
			2.开通会员卡后会员卡被停用，访问VIP会员显示会员卡详情会有“停用中”的状态

		开通会员卡的场景：
			一期
				获得未开通会员卡列表
				开通学生卡
				开通家庭卡
				开通年卡
				开卡支付失败
				开通会员卡后，停用会员卡
				验证没有关联会员卡的自营平台看不到VIP会员小模块（页面验证）

			二期
				开通会员卡时，会员卡库存不足
				开通会员卡时，会员卡被停用
				全部会员卡被停用
				开通会员卡后，没有返完会员卡次数就已经过期
	"""

Background:
	Given 重置'weapp'的bdd环境
	Given 设置jobs为自营平台账号::weapp
	Given 设置nokia为自营平台账号::weapp
	Given jobs登录系统::weapp
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
	#添加会员卡套餐
	Given test登录管理系统::weizoom_card
	#套餐名称 套餐类型 套餐返款次数
	#开通支付费用 首次购卡金额 VIP会员返款每隔几天返多少钱 套餐总价值
	When test添加会员卡套餐::weizoom_card
		"""
		{
			"package_name": "半年学生卡1",
			"package_type": "学生卡",
			"package_refund_number": "6",
			"open_pay_cost": "99.00",
			"first_purchase_amount": "100.00",
			"VIP_member_refund": {
				"every_other_days": "30",
				"refund_amount": "30.00"
			},
			"package_value": "250.00"
		}
		"""
	When test添加会员卡套餐::weizoom_card
		"""
		{
			"package_name": "半年家庭卡1",
			"package_type": "家庭卡",
			"package_refund_number": "6",
			"open_pay_cost": "99.00",
			"first_purchase_amount": "100.00",
			"VIP_member_refund": {
				"every_other_days": "30",
				"refund_amount": "30.00"
			},
			"package_value": "250.00"
		}
		"""
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
	#新建会员卡
	When test新建会员卡::weizoom_card
		"""
		{
			"name": "学生会员卡",
			"prefix_value": "999",
			"card_package": "半年学生卡1",
			"exclusive_stores": ["jobs"],
			"num":"100",
			"remark":"会员卡"
		}
		"""
	When test新建会员卡::weizoom_card
		"""
		{
			"name": "家庭会员卡",
			"prefix_value": "888",
			"card_package": "半年家庭卡1",
			"exclusive_stores": ["jobs"],
			"num":"100",
			"remark":"会员卡"
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
					"name":"学生会员卡",
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
	When test下订单::weizoom_card
			"""
			[{
				"card_info":[{
					"name":"家庭会员卡",
					"order_num":"10",
					"start_date":"2016-11-23 00:00",
					"end_date":"2020-11-23 00:00"
				}],
				"order_info":{
					"order_id":"0002"
				}
			}]
			"""
	And test批量激活订单'0002'的卡::weizoom_card
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
					"order_id":"0003"
				}
			}]
			"""
	And test批量激活订单'0003'的卡::weizoom_card

	When bill关注jobs的公众号
	When bill关注nokia的公众号



Scenario: 1 会员查看VIP会员会员卡列表

	When bill访问jobs的webapp
	And bill浏览jobs的webapp的会员卡
	Then bill获得未开通会员卡列表
		"""
		[{
			"name": "年卡会员卡",
			"months": "12",
			"open_pay_cost": "365.00"
		}, {
			"name": "家庭会员卡",
			"months": "6",
			"open_pay_cost": "99.00"
		}, {
			"name": "学生会员卡",
			"months": "6",
			"open_pay_cost": "99.00"
		}]
		"""



Scenario: 2 会员开通学生卡

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
			"name": "学生会员卡",
			"id": "999000001"
		}
		"""
	Then bill成功开通会员卡
		"""
		{
			"payment_amount": "99.00",
			"refund_number": "6"
		}
		"""
	When bill浏览jobs的webapp的会员卡
	Then bill获得会员卡
		"""
		{
			"name": "学生会员卡",
			"id": "999000001",
			"refund_surplus_number": "5",
			"member_purse": "100.00"
		}
		"""


Scenario: 3 会员开通家庭卡

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
			"name": "家庭会员卡",
			"id": "888000001"
		}
		"""
	Then bill成功开通会员卡
		"""
		{
			"payment_amount": "99.00",
			"refund_number": "6"
		}
		"""
	When bill浏览jobs的webapp的会员卡
	Then bill获得会员卡
		"""
		{
			"name": "家庭会员卡",
			"id": "888000001",
			"refund_surplus_number": "5",
			"member_purse": "100.00"
		}
		"""


Scenario: 4 会员开通年卡

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
	Then bill成功开通会员卡
		"""
		{
			"payment_amount": "365.00",
			"refund_number": "12"
		}
		"""
	When bill浏览jobs的webapp的会员卡
	Then bill获得会员卡
		"""
		{
			"name": "年卡会员卡",
			"id": "777000001",
			"refund_surplus_number": "11",
			"member_purse": "100.00"
		}
		"""



Scenario: 5 会员开通会员卡支付失败

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
	Then bill支付失败获得提示信息'支付失败,请重试！'
	When bill浏览jobs的webapp的会员卡
	Then bill获得未开通会员卡列表
		"""
		[{
			"name": "年卡会员卡",
			"months": "12",
			"open_pay_cost": "365.00"
		}, {
			"name": "家庭会员卡",
			"months": "6",
			"open_pay_cost": "99.00"
		}, {
			"name": "学生会员卡",
			"months": "6",
			"open_pay_cost": "99.00"
		}]
		"""



Scenario: 6 会员开通会员卡后，会员卡被停用

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
	Then bill成功开通会员卡
		"""
		{
			"payment_amount": "365.00",
			"refund_number": "12"
		}
		"""
	Given test登录管理系统::weizoom_card
	When test停用卡号'777000001'的卡::weizoom_card
	When bill浏览jobs的webapp的会员卡
	Then bill获得会员卡
		"""
		{
			"name": "年卡会员卡",
			"id": "777000001",
			"refund_surplus_number": "11",
			"member_purse": "100.00",
			"status": "停用中"
		}
		"""
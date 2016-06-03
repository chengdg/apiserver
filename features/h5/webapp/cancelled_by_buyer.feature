# watcher: fengxuejing@weizoom.com,benchi@weizoom.com
#author: 冯雪静

Feature:jobs管理系统里待支付的订单，用户可以在手机端直接取消
	"""
	手机端能取消订单
		1.手机端能取消待支付订单，验证库存
		2.手机端不能取消使用积分待发货的订单
		3.手机端不能取消使用全体待发货的订单
		4.手机端能取消使用积分待支付的订单，验证库存，积分
		5.手机端能取消使用单品券待支付的订单，验证库存，单品券
		6.手机端能取消使用全体券待支付的订单，验证库存，全体券
		7.手机端不能取消使用微众卡待发货的订单
		8.手机端能取消使用微众卡待支付的订单，验证库存，微众卡
		9.
	"""
Background:
	Given 重置'weapp'的bdd环境
	Given 重置'weizoom_card'的bdd环境
	Given jobs登录系统::weapp
	And jobs已有微众卡支付权限::weapp
	And jobs已添加支付方式::weapp
		"""
		[{
			"type":"货到付款"
		},{
			"type":"微信支付"
		},{
			"type":"微众卡支付"
		}]
		"""

	#创建微众卡
	Given test登录管理系统::weizoom_card
	When test新建通用卡::weizoom_card
		"""
		[{
			"name":"100元微众卡",
			"prefix_value":"100",
			"type":"virtual",
			"money":"100.00",
			"num":"2",
			"comments":"微众卡"
		}]
		"""

	#微众卡审批出库
	When test下订单::weizoom_card
		"""
		[{
			"card_info":[{
				"name":"100元微众卡",
				"order_num":"2",
				"start_date":"2016-04-07 00:00",
				"end_date":"2019-10-07 00:00"
			}],
			"order_info":{
				"order_id":"0001"
			}
		}]
		"""
	And test批量激活订单'0001'的卡::weizoom_card

	Given jobs登录系统::weapp
	And jobs已添加商品::weapp
		"""
		[{
			"name": "商品1",
			"price": 100.00,
			"stocks": 8
		}, {
			"name": "商品2",
			"price": 100.00,
			"stocks": 8
		}]
		"""
	And bill关注jobs的公众号
	When bill访问jobs的webapp
	When bill获得jobs的150会员积分
	Then bill在jobs的webapp中拥有150会员积分

	Given jobs登录系统::weapp
	Given jobs已添加了优惠券规则::weapp
		"""
		[{
			"name": "全体券1",
			"money": 100.00,
			"start_date": "今天",
			"end_date": "1天后",
			"coupon_id_prefix": "coupon1_id_"
		}, {
			"name": "单品券2",
			"money": 50.00,
			"start_date": "今天",
			"end_date": "1天后",
			"coupon_id_prefix": "coupon2_id_",
			"coupon_product": "商品2"
		}]
		"""
	And jobs设定会员积分策略::weapp
		"""
		{
			"use_ceiling": 100,
			"use_condition": "on",
			"integral_each_yuan": 1
		}
		"""
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"order_id": "001",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	And bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"order_id":"002",
			"products": [{
				"name": "商品1",
				"count": 1
			}],
			"coupon": "coupon1_id_1"
		}
		"""
	And bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"order_id":"003",
			"products": [{
				"name": "商品1",
				"count": 1
			}],
			"integral": 100,
			"integral_money": 100.00
		}
		"""
	And bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"order_id":"004",
			"products": [{
				"name": "商品1",
				"count": 1
			}],
			"integral": 50,
			"integral_money": 50.00
		}
		"""
	And bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"order_id":"005",
			"products": [{
				"name": "商品2",
				"count": 1
			}],
			"coupon": "coupon2_id_1"
		}
		"""
	And bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"order_id":"006",
			"products": [{
				"name": "商品2",
				"count": 2
			}],
			"coupon": "coupon1_id_2"
		}
		"""
	And bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"order_id":"007",
			"products": [{
				"name": "商品2",
				"count": 1
			}],
			"weizoom_card":[{
				"card_name":"100000001",
				"card_pass":"1234567"
			}]
		}
		"""
	And bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"order_id":"008",
			"products": [{
				"name": "商品2",
				"count": 2
			}],
			"weizoom_card":[{
				"card_name":"100000002",
				"card_pass":"1234567"
			}]
		}
		"""

@mall3 @mall2 @order @allOrder @mall.order_cancel_status @mall.order_cancel_status.member @wip.cbb1 @wip.cbb
Scenario:1 bill能取消待支付订单
	bill取消订单'001'
	1. bill手机端订单状态改变为'已取消'
	2. jobs后端订单状态改变为'已取消'
	3. '商品1'库存更新加1

	When bill访问jobs的webapp
	Then bill'能'取消订单'001'
	When bill取消订单'001'
	Then bill手机端获取订单'001'
		"""
		{
			"order_no": "001",
			"status": "已取消"
		}
		"""
	Given jobs登录系统::weapp
	Then jobs能获得订单'001'::weapp
		"""
		{
			"order_no": "001",
			"status": "已取消"
		}
		"""
	Then jobs能获取商品'商品1'::weapp
		"""
		{
			"name": "商品1",
			"stocks": 5
		}
		"""

@mall3 @mall2 @order @allOrder   @mall.order_cancel_status @mall.order_cancel_status.coupon_member @pyliu @wip.cbb2 @dd2 @wip.cbb
Scenario:2 bill不能取消使用了优惠券的待发货订单
	bill不能取消订单'002'
	1. bill手机端订单状态为'待发货'
	2. jobs后端订单状态为'待发货'
	3. '商品1'库存不变
	4. 优惠券'coupon1_id_1'状态改变为'已使用'

	When bill访问jobs的webapp
	Then bill'不能'取消订单'002'
	Then bill手机端获取订单'002'
		"""
		{
			"order_no": "002",
			"status": "待发货"
		}
		"""
	Given jobs登录系统::weapp
	Then jobs能获得订单'002'::weapp
		"""
		{
			"order_no": "002",
			"status": "待发货"
		}
		"""
	Then jobs能获取商品'商品1'::weapp
		"""
		{
			"name": "商品1",
			"stocks": 4
		}
		"""
	Then jobs获取优惠券'coupon1_id_1'状态::weapp
		"""
		{
			"coupon_code": "coupon1_id_1",
			"coupon_status": "已使用"
		}
		"""

@mall3 @mall2 @order @allOrder   @mall.order_cancel_status @mall.order_cancel_status.integral_member @pyliu02 @wip.cbb3 @wip.cbb
Scenario:3 bill不能取消使用了积分的待发货订单
	bill不能取消订单'003'
	1. bill手机端订单状态为'待发货'
	2. jobs后端订单状态为'待发货'
	3. '商品1'库存不变
	4. 积分数值为：'0'

	When bill访问jobs的webapp
	Then bill'不能'取消订单'003'
	Then bill手机端获取订单'003'
		"""
		{
			"order_no": "003",
			"status": "待发货"
		}
		"""
	Then bill在jobs的webapp中拥有0会员积分

	Given jobs登录系统::weapp
	Then jobs能获得订单'003'::weapp
		"""
		{
			"order_no": "003",
			"status": "待发货"
		}
		"""
	Then jobs能获取商品'商品1'::weapp
		"""
		{
			"name": "商品1",
			"stocks": 4
		}
		"""

@mall3 @mall2 @order @allOrder @mall.order_cancel_status @mall.order_cancel_status.integral_and_coupon_member @pyliu @wip.cbb4 @wip.cbb
Scenario:4 bill能取消使用积分的待支付订单
	bill取消订单'004'
	1. bill手机端订单状态改变为'已取消'
	2. jobs后端订单状态改变为'已取消'
	3. '商品1'库存更新加1
	4. 积分数值改变为：'50'

	When bill访问jobs的webapp
	#Then bill在jobs的webapp中拥有150会员积分
	Then bill'能'取消订单'004'
	When bill取消订单'004'
	Then bill手机端获取订单'004'
		"""
		{
			"order_no": "004",
			"status": "已取消"
		}
		"""
	Then bill在jobs的webapp中拥有50会员积分
	Given jobs登录系统::weapp
	Then jobs能获得订单'004'::weapp
		"""
		{
			"order_no": "004",
			"status": "已取消"
		}
		"""
	Then jobs能获取商品'商品1'::weapp
		"""
		{
			"name": "商品1",
			"stocks": 5
		}
		"""

@mall3 @wip.cbb5 @wip.cbb
Scenario:5 bill能取消使用了单品券的待支付订单
	bill能取消订单'005'
		1. bill手机端订单状态为'待支付'
		2. jobs后端订单状态为'待支付'
		3. '商品2'库存更新加1
		4. 单品券'coupon2_id_1'状态改变为'未领取'

	When bill访问jobs的webapp
	Then bill'能'取消订单'005'
	When bill取消订单'005'
	Then bill手机端获取订单'005'
		"""
		{
			"order_no": "005",
			"status": "已取消"
		}
		"""
	Given jobs登录系统::weapp
	Then jobs能获得订单'005'::weapp
		"""
		{
			"order_no": "005",
			"status": "已取消"
		}
		"""
	Then jobs能获取商品'商品2'::weapp
		"""
		{
			"name": "商品2",
			"stocks": 3
		}
		"""
	Then jobs获取优惠券'coupon2_id_1'状态::weapp
		"""
		{
			"coupon_code": "coupon2_id_1",
			"coupon_status": "未领取"
		}
		"""

@mall3 @wip.cbb @wip.cbb6
Scenario:6 bill能取消使用了优惠券的待支付订单
	bill能取消订单'006'
		1. bill手机端订单状态为'待支付'
		2. jobs后端订单状态为'待支付'
		3. '商品2'库存更新加2
		4. 优惠券'coupon1_id_2'状态改变为'未领取'

	When bill访问jobs的webapp
	Then bill'能'取消订单'006'
	When bill取消订单'006'
	Then bill手机端获取订单'006'
		"""
		{
			"order_no": "006",
			"status": "已取消"
		}
		"""
	Given jobs登录系统::weapp
	Then jobs能获得订单'006'::weapp
		"""
		{
			"order_no": "006",
			"status": "已取消"
		}
		"""
	Then jobs能获取商品'商品2'::weapp
		"""
		{
			"name": "商品2",
			"stocks": 4
		}
		"""
	Then jobs获取优惠券'coupon1_id_2'状态::weapp
		"""
		{
			"coupon_code": "coupon1_id_2",
			"coupon_status": "未领取"
		}
		"""

@mall3 @wip.cbb @wip.cbb7
Scenario:7 bill不能取消使用了微众卡的待发货订单
	bill不能取消订单'007'
	1. bill手机端订单状态为'待发货'
	2. jobs后端订单状态为'待发货'
	3. '商品2'库存不变
	4. 微众卡状态为'已用完'

	When bill访问jobs的webapp
	Then bill'不能'取消订单'007'
	Then bill手机端获取订单'007'
		"""
		{
			"order_no": "007",
			"status": "待发货"
		}
		"""
	Given jobs登录系统::weapp
	Then jobs能获得订单'007'::weapp
		"""
		{
			"order_no": "007",
			"status": "待发货"
		}
		"""
	Then jobs能获取商品'商品2'::weapp
		"""
		{
			"name": "商品2",
			"stocks": 2
		}
		"""

	When bill进行微众卡余额查询
		"""
		{
			"id":"100000001",
			"password":"1234567"
		}
		"""
	Then bill获得微众卡余额查询结果
		"""
		{
			"card_remaining":0.00
		}
		"""

@mall3 @wip.cbb @wip.cbb8
Scenario:8 bill能取消使用了微众卡的待支付订单
	bill能取消订单'008'
	1. bill手机端订单状态为'待支付'
	2. jobs后端订单状态为'待支付'
	3. '商品2'库存更新加2
	4. 微众卡状态为'已使用'

	When bill访问jobs的webapp
	Then bill'能'取消订单'008'
	When bill取消订单'008'
	Then bill手机端获取订单'008'
		"""
		{
			"order_no": "008",
			"status": "已取消"
		}
		"""
	Given jobs登录系统::weapp
	Then jobs能获得订单'008'::weapp
		"""
		{
			"order_no": "008",
			"status": "已取消"
		}
		"""
	Then jobs能获取商品'商品2'::weapp
		"""
		{
			"name": "商品2",
			"stocks": 4
		}
		"""

	When bill访问jobs的webapp
	When bill进行微众卡余额查询
		"""
		{
			"id":"100000002",
			"password":"1234567"
		}
		"""
	Then bill获得微众卡余额查询结果
		"""
		{
			"card_remaining":100.00
		}
		"""

@mall3 @mall2 @order @allOrder @mall.order_cancel_status @ztq
Scenario:9 bill能取买赠订单，主商品和赠品库存正常
	bill能取消买赠订单'009'
	1. bill手机端订单状态为'待支付'
	2. jobs后端订单状态为'待支付'
	3. '商品2'库存更新加2
	4. 微众卡状态为'已使用'

	Given jobs登录系统::weapp
	When jobs创建买赠活动::weapp
		"""
		[{
			"name": "商品1买一赠二",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品1",
			"premium_products": [{
				"name": "商品1",
				"count": 1
			}, {
				"name": "商品2",
				"count": 1
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"pay_type":"微信支付",
			"order_id":"009",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	Given jobs登录系统::weapp
	Then jobs能获取商品'商品1'::weapp
		"""
		{
			"name": "商品1",
			"stocks": 2
		}
		"""
	Then jobs能获取商品'商品2'::weapp
		"""
		{
			"name": "商品2",
			"stocks": 1
		}
		"""
	When bill访问jobs的webapp
	Then bill'能'取消订单'009'
	When bill取消订单'009'
	Then bill手机端获取订单'009'
		"""
		{
			"order_no": "009",
			"status": "已取消"
		}
		"""
	Given jobs登录系统::weapp
	Then jobs能获得订单'009'::weapp
		"""
		{
			"order_no": "009",
			"status": "已取消"
		}
		"""
	Then jobs能获取商品'商品1'::weapp
		"""
		{
			"name": "商品1",
			"stocks": 4
		}
		"""
	Then jobs能获取商品'商品2'::weapp
		"""
		{
			"name": "商品2",
			"stocks": 2
		}
		"""


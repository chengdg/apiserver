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
	"""
Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
	And jobs已有微众卡支付权限:weapp
	And jobs已添加支付方式:weapp
		"""
		[{
			"type":"货到付款"
		},{
			"type":"微信支付"
		},{
			"type":"微众卡支付"
		}]
		"""
	And jobs已创建微众卡:weapp
		"""
		{
			"cards":[{
				"id":"0000001",
				"password":"1234567",
				"status":"未使用",
				"price":100.00
			}, {
				"id":"0000002",
				"password":"1234567",
				"status":"未使用",
				"price":100.00
			}]
		}
		"""
	And jobs已添加商品:weapp
		"""
		[{
			"name": "商品1",
			"price": 100,
			"stocks": 8
		}, {
			"name": "商品2",
			"price": 100,
			"stocks": 8
		}]
		"""
	And bill关注jobs的公众号
	And jobs已有的会员:weapp
		"""
		[{
			"name": "bill",
			"integral":"150"
		}]
		"""
	And jobs已添加了优惠券规则:weapp
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
	And jobs设定会员积分策略:weapp
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
			"integral": 100
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
			"integral": 50
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
				"card_name":"0000001",
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
				"card_name":"0000002",
				"card_pass":"1234567"
			}]
		}
		"""

@mall3 @mall2 @order @allOrder @mall.order_cancel_status @mall.order_cancel_status.member @wip.cbb1
Scenario:1 bill能取消待支付订单
	bill取消订单'001'
	1. bill手机端订单状态改变为'已取消'
	2. jobs后端订单状态改变为'已取消'
	3. '商品1'库存更新加1

	When bill访问jobs的webapp
	When bill'能'取消订单'001'
	Then bill手机端获取订单'001'
		"""
		{
			"order_no": "001",
			"status": "已取消"
		}
		"""
	Given jobs登录系统:weapp
	Then jobs能获得订单'001':weapp
		"""
		{
			"order_no": "001",
			"status": "已取消"
		}
		"""
	Then jobs能获取商品'商品1':weapp
		"""
		{
			"name": "商品1",
			"stocks": 5
		}
		"""

@mall2 @order @allOrder   @mall.order_cancel_status @mall.order_cancel_status.coupon_member @pyliu
Scenario:2 bill不能取消使用了优惠券的待发货订单
	bill不能取消订单'002'
	1. bill手机端订单状态为'待发货'
	2. jobs后端订单状态为'待发货'
	3. '商品1'库存不变
	4. 优惠券'coupon1_id_1'状态改变为'已使用'

	When bill访问jobs的webapp
	When bill'不能'取消订单'002'
	Then bill手机端获取订单'002'
		"""
		{
			"order_no": "002",
			"status": "待发货"
		}
		"""
	Given jobs登录系统:weapp
	Then jobs能获得订单'002':weapp
		"""
		{
			"order_no": "002",
			"status": "待发货"
		}
		"""
	Then jobs能获取商品'商品1':weapp
		"""
		{
			"name": "商品1",
			"stocks": 4
		}
		"""
	Then jobs获取优惠券'coupon1_id_1'状态:weapp
		"""
		{
			"coupon_code": "coupon1_id_1",
			"coupon_status": "已使用"
		}
		"""

@mall2 @order @allOrder   @mall.order_cancel_status @mall.order_cancel_status.integral_member @pyliu02
Scenario:3 bill不能取消使用了积分的待发货订单
	bill不能取消订单'003'
	1. bill手机端订单状态为'待发货'
	2. jobs后端订单状态为'待发货'
	3. '商品1'库存不变
	4. 积分数值为：'0'

	When bill访问jobs的webapp
	When bill'不能'取消订单'003'
	Then bill手机端获取订单'003'
		"""
		{
			"order_no": "003",
			"status": "待发货"
		}
		"""
	Then bill获取积分数值
		"""
		{
			"integral":"0"
		}
		"""
	Given jobs登录系统:weapp
	Then jobs能获得订单'003':weapp
		"""
		{
			"order_no": "003",
			"status": "待发货"
		}
		"""
	Then jobs能获取商品'商品1':weapp
		"""
		{
			"name": "商品1",
			"stocks": 4
		}
		"""

@mall2 @order @allOrder   @mall.order_cancel_status @mall.order_cancel_status.integral_and_coupon_member @pyliu
Scenario:4 bill能取消使用积分的待支付订单
	bill取消订单'004'
	1. bill手机端订单状态改变为'已取消'
	2. jobs后端订单状态改变为'已取消'
	3. '商品1'库存更新加1
	4. 积分数值改变为：'50'

	When bill访问jobs的webapp
	When bill'能'取消订单'004'
	Then bill手机端获取订单'004'
		"""
		{
			"order_no": "004",
			"status": "已取消"
		}
		"""
	Then bill获取积分数值
		"""
		{
			"integral": "50"
		}
		"""
	Given jobs登录系统:weapp
	Then jobs能获得订单'004':weapp
		"""
		{
			"order_no": "004",
			"status": "已取消"
		}
		"""
	Then jobs能获取商品'商品1':weapp
		"""
		{
			"name": "商品1",
			"stocks": 5
		}
		"""

Scenario:5 bill能取消使用了单品券的待支付订单
bill能取消订单'005'
	1. bill手机端订单状态为'待支付'
	2. jobs后端订单状态为'待支付'
	3. '商品2'库存更新加1
	4. 单品券'coupon2_id_1'状态改变为'未使用'

	When bill访问jobs的webapp
	When bill'能'取消订单'005'
	Then bill手机端获取订单'005'
		"""
		{
			"order_no": "005",
			"status": "已取消"
		}
		"""
	Given jobs登录系统:weapp
	Then jobs能获得订单'005':weapp
		"""
		{
			"order_no": "001",
			"status": "已取消"
		}
		"""
	Then jobs能获取商品'商品2':weapp
		"""
		{
			"name": "商品2",
			"stocks": 3
		}
		"""
	Then jobs获取优惠券'coupon2_id_1'状态:weapp
		"""
		{
			"coupon_code": "coupon2_id_1",
			"coupon_status": "未使用"
		}
		"""


Scenario:6 bill能取消使用了优惠券的待支付订单
bill能取消订单'006'
	1. bill手机端订单状态为'待支付'
	2. jobs后端订单状态为'待支付'
	3. '商品2'库存更新加2
	4. 优惠券'coupon1_id_2'状态改变为'未使用'

	When bill访问jobs的webapp
	When bill'能'取消订单'006'
	Then bill手机端获取订单'006'
		"""
		{
			"order_no": "006",
			"status": "已取消"
		}
		"""
	Given jobs登录系统:weapp
	Then jobs能获得订单'006':weapp
		"""
		{
			"order_no": "006",
			"status": "已取消"
		}
		"""
	Then jobs能获取商品'商品2':weapp
		"""
		{
			"name": "商品2",
			"stocks": 4
		}
		"""
	Then jobs获取优惠券'coupon1_id_2'状态:weapp
		"""
		{
			"coupon_code": "coupon1_id_2",
			"coupon_status": "未使用"
		}
		"""


Scenario:7 bill不能取消使用了微众卡的待发货订单
	bill不能取消订单'007'
	1. bill手机端订单状态为'待发货'
	2. jobs后端订单状态为'待发货'
	3. '商品2'库存不变
	4. 微众卡状态为'已用完'

	When bill访问jobs的webapp
	When bill'不能'取消订单'007'
	Then bill手机端获取订单'007'
		"""
		{
			"order_no": "007",
			"status": "待发货"
		}
		"""
	Given jobs登录系统:weapp
	Then jobs能获得订单'007':weapp
		"""
		{
			"order_no": "007",
			"status": "待发货"
		}
		"""
	Then jobs能获取商品'商品2':weapp
		"""
		{
			"name": "商品2",
			"stocks": 2
		}
		"""
	Then jobs能获取微众卡'0000001':weapp
		"""
		{
			"status":"已用完",
			"price":0.00
		}
		"""



Scenario:8 bill能取消使用了微众卡的待支付订单
	bill能取消订单'008'
	1. bill手机端订单状态为'待支付'
	2. jobs后端订单状态为'待支付'
	3. '商品2'库存更新加2
	4. 微众卡状态为'已使用'

	When bill访问jobs的webapp
	When bill'能'取消订单'008'
	Then bill手机端获取订单'008'
		"""
		{
			"order_no": "008",
			"status": "已取消"
		}
		"""
	Given jobs登录系统:weapp
	Then jobs能获得订单'008':weapp
		"""
		{
			"order_no": "008",
			"status": "已取消"
		}
		"""
	Then jobs能获取商品'商品2':weapp
		"""
		{
			"name": "商品2",
			"stocks": 4
		}
		"""
	Then jobs能获取微众卡'0000002':weapp
		"""
		{
			"status":"已使用",
			"price":100.00
		}
		"""

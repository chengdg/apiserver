# watcher: zhangsanxiang@weizoom.com,benchi@weizoom.com
#_author_:张三香 2015.12.25

Feature:下单失败后校验库存、积分、优惠券和微众卡信息
	"""
		下单失败后：
		1、商品库存不会减少
		2、下单过程中使用的积分，下单失败后积分将会恢复
		3、下单过程中若使用优惠券，下单失败后优惠券将会恢复（不被使用）
		4、下单过程中若使用微众卡，下单失败后微众卡余额将恢复（不减少）
	"""

Background:
	Given 重置'weapp'的bdd环境
	Given 重置'weizoom_card'的bdd环境
	Given jobs登录系统::weapp
	Given jobs设定会员积分策略::weapp
		"""
		{
			"integral_each_yuan": 2
		}
		"""
	And jobs已有微众卡支付权限::weapp
	And jobs已添加支付方式::weapp
		"""
		[{
			"type":"货到付款"
		},{
			"type":"微信支付"
		},{
			"type":"支付宝"
		},{
			"type":"微众卡支付"
		}]
		"""
	And jobs已添加商品::weapp
		"""
		[{
			"name": "商品1",
			"model": {
				"models": {
					"standard": {
						"user_code": "10",
						"stock_type": "有限",
						"stocks": 1,
						"price": 10.00
					}
				}
			}
		},{
			"name": "商品2",
			"model": {
				"models": {
					"standard": {
						"user_code": "20",
						"stock_type": "有限",
						"stocks": 2,
						"price": 20.00
					}
				}
			}
		},{
			"name": "商品3",
			"model": {
				"models": {
					"standard": {
						"user_code": "30",
						"stock_type": "有限",
						"stocks": 3,
						"price": 30.00
					}
				}
			}
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
			"num":"1",
			"comments":"微众卡"
		}]
		"""

	#微众卡审批出库
	When test下订单::weizoom_card
			"""
			[{
				"card_info":[{
					"name":"100元微众卡",
					"order_num":"1",
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
	Given jobs已添加了优惠券规则::weapp
		"""
		[{
			"name": "优惠券1",
			"money": 20.00,
			"start_date": "今天",
			"end_date": "1天后",
			"coupon_id_prefix": "coupon1_id_"
		}]
		"""
	Given bill关注jobs的公众号
	When bill访问jobs的webapp
	When bill领取jobs的优惠券::weapp
		"""
		[{
			"name": "优惠券1",
			"coupon_ids": ["coupon1_id_2", "coupon1_id_1"]
		}]
		"""

@mall3 @duhao @order
Scenario:1 下单失败后，校验商品的库存变化
	bill加入1个'商品1'和2个'商品2'到购物车
	jobs后台下架'商品1'和'商品2'
	bill从购物车提交订单
	bill获得订单失败信息
	jobs后台查看商品1和商品2的库存

	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 1
		}, {
			"name": "商品2",
			"count": 2
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"context": [{
				"name": "商品1"
			}, {
				"name": "商品2"
			}]
		}
		"""

	Given jobs登录系统::weapp
	When jobs'下架'商品'商品1'::weapp
	When jobs'下架'商品'商品2'::weapp

	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "微信支付"
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
			"detail": 
			[{
				"id": "商品1",
				"short_msg": "商品已下架"
			},{
				"id": "商品2",
				"short_msg": "商品已下架"
			}]
		}
		"""
	#校验商品的库存
	Given jobs登录系统::weapp
	Then jobs能获取商品'商品1'
		"""
		{
			"name": "商品1",
			"status": "待售",
			"model": {
				"models": {
					"standard": {
						"stock_type": "有限",
						"stocks": 1,
						"price": 10.00
					}
				}
			}
		}
		"""
	Then jobs能获取商品'商品2'
		"""
		{
			"name": "商品2",
			"status": "待售",
			"model": {
				"models": {
					"standard": {
						"stock_type": "有限",
						"stocks": 2,
						"price": 20.00
					}
				}
			}
		}
		"""

@mall3 @duhao @order
Scenario:2 下单失败后，校验会员的积分变化
	#bill购买商品2，消耗积分
	#jobs结积分活动
	#bill提交订单，获得订单失败信息
	#校验bill的积分

	Given jobs登录系统::weapp
	When jobs创建积分应用活动::weapp
		"""
		[{
			"name": "商品2积分应用",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品2",
			"is_permanant_active": false,
			"rules": [{
				"member_grade": "全部",
				"discount": 100,
				"discount_money": 20.00
			}]
		}]
		"""
	When jobs'结束'促销活动'商品2积分应用'::weapp

	When bill访问jobs的webapp
	When bill获得jobs的50会员积分
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品2",
				"count": 1,
				"integral": 40,
				"integral_money": 20.00
			}]
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
			"detail": [{
				"id": "商品2",
				"msg": "积分折扣已经过期",
				"short_msg": "已经过期"
			}]
		}
		"""
	#下单失败，校验会员的积分
	Then bill在jobs的webapp中拥有50会员积分
	#下单失败，校验商品的库存
	Given jobs登录系统::weapp
	Then jobs能获取商品'商品2'
		"""
		{
			"name": "商品2",
			"status": "在售",
			"model": {
				"models": {
					"standard": {
						"stock_type": "有限",
						"stocks": 2,
						"price": 20.00
					}
				}
			}
		}
		"""

@mall3 @duhao @order @weizoom_card
Scenario:3 下单失败后，校验优惠券和微众卡的变化
	When bill访问jobs的webapp
	When bill绑定微众卡
		"""
		{
			"binding_date":"今天",
			"binding_shop":"jobs",
			"weizoom_card_info":
				{
					"id":"100000001",
					"password":"1234567"
				}
		}
		"""
	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products":[{
				"name":"商品3",
				"price":30.00,
				"count":4
			}],
			"coupon": "coupon1_id_1",
			"weizoom_card":[{
				"card_name":"100000001",
				"card_pass":"1234567"
			}]
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
			"detail": [{
				"id": "商品3",
				"msg": "有商品库存不足，请重新下单",
				"short_msg": "库存不足"
			}]
		}
		"""

	Given jobs登录系统::weapp
	Then jobs能获取商品'商品3'
		"""
		{
			"name": "商品3",
			"status": "在售",
			"model": {
				"models": {
					"standard": {
						"stock_type": "有限",
						"stocks": 3,
						"price": 30.00
					}
				}
			}
		}
		"""
	Then jobs能获得优惠券'优惠券1'的码库
		"""
		{
			"coupon1_id_1": {
				"money": 20.00,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			},
			"coupon1_id_2": {
				"money": 20.00,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""

	When bill访问jobs的webapp
	Then bill能获得微众卡'100000001'的详情信息
		"""
		{
			"card_remain_value":100.00
		}
		"""


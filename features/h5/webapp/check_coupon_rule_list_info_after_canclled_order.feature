# watcher: zhangsanxiang@weizoom.com,benchi@weizoom.com
#_author_:张三香 2016.01.13
#针对bug7125-使用优惠券购买商品，然后再取消订单，优惠券的已使用变成-1补充feature

Feature: 取消订单后，校验后台优惠券规则列表信息

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
			"type":"支付宝"
		},{
			"type":"微众卡支付"
		}]
		"""

	And jobs已添加商品::weapp
		"""
		[{
			"name": "商品1",
			"price": 200.00
		}]
		"""
	And bill关注jobs的公众号

@mall3
Scenario:1 后台取消使用优惠券的'待支付'状态的订单
	Given jobs登录系统::weapp
	When jobs添加优惠券规则::weapp
		"""
		[{
			"name": "单品券1",
			"money": 50.00,
			"count": 4,
			"limit_counts": 1,
			"start_date": "今天",
			"end_date": "1天后",
			"coupon_id_prefix": "coupon1_id_",
			"coupon_product": "商品1"
		}]
		"""
	When jobs为会员发放优惠券::weapp
		"""
		{
			"name": "单品券1",
			"count": 1,
			"members": ["bill"],
			"coupon_ids": ["coupon1_id_1"]
		}
		"""
	Then jobs能获得优惠券规则列表::weapp
		"""
		[{
			"name": "单品券1",
			"remained_count": 3,
			"use_count": 0,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id": "001",
			"pay_type": "微信支付",
			"products":[{
				"name":"商品1",
				"price":100.00,
				"count":1
			}],
			"coupon":"coupon1_id_1"
		}
		"""

	Given jobs登录系统::weapp
	Then jobs能获得优惠券规则列表::weapp
		"""
		[{
			"name": "单品券1",
			"remained_count": 3,
			"use_count": 1,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""
	When jobs'取消'订单'001'::weapp
	Then jobs能获得优惠券规则列表::weapp
		"""
		[{
			"name": "单品券1",
			"remained_count": 3,
			"use_count": 0,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""

@mall3
Scenario:2 手机端取消使用优惠券的'待支付'状态的订单
	Given jobs登录系统::weapp
	When jobs添加优惠券规则::weapp
		"""
		[{
			"name": "全体券2",
			"money": 50.00,
			"count": 4,
			"limit_counts": "无限",
			"start_date": "今天",
			"end_date": "1天后",
			"coupon_id_prefix": "coupon2_id_"
		}]
		"""
	When jobs为会员发放优惠券::weapp
		"""
		{
			"name": "全体券2",
			"count": 1,
			"members": ["bill"],
			"coupon_ids": ["coupon2_id_1"]
		}
		"""
	Then jobs能获得优惠券规则列表::weapp
		"""
		[{
			"name": "全体券2",
			"remained_count": 3,
			"use_count": 0,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id": "001",
			"pay_type": "微信支付",
			"products":[{
				"name":"商品1",
				"price":100.00,
				"count":1
			}],
			"coupon":"coupon2_id_1"
		}
		"""

	Given jobs登录系统::weapp
	Then jobs能获得优惠券规则列表::weapp
		"""
		[{
			"name": "全体券2",
			"remained_count": 3,
			"use_count": 1,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""

	When bill取消订单'001'
	Given jobs登录系统::weapp
	Then jobs能获得优惠券规则列表::weapp
		"""
		[{
			"name": "全体券2",
			"remained_count": 3,
			"use_count": 0,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""

@mall3
Scenario:3 后台取消只使用优惠券支付的'待发货'状态的订单
	Given jobs登录系统::weapp
	When jobs添加优惠券规则::weapp
		"""
		[{
			"name": "单品券3",
			"money": 100.00,
			"count": 4,
			"limit_counts": 1,
			"start_date": "今天",
			"end_date": "1天后",
			"coupon_id_prefix": "coupon3_id_",
			"coupon_product": "商品1"
		}]
		"""
	When jobs为会员发放优惠券::weapp
		"""
		{
			"name": "单品券3",
			"count": 1,
			"members": ["bill"],
			"coupon_ids": ["coupon3_id_1"]
		}
		"""
	Then jobs能获得优惠券规则列表::weapp
		"""
		[{
			"name": "单品券3",
			"remained_count": 3,
			"use_count": 0,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id": "001",
			"pay_type": "微信支付",
			"products":[{
				"name":"商品1",
				"price":100.00,
				"count":1
			}],
			"coupon":"coupon3_id_1"
		}
		"""

	Given jobs登录系统::weapp
	Then jobs能获得优惠券规则列表::weapp
		"""
		[{
			"name": "单品券3",
			"remained_count": 3,
			"use_count": 1,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""
	When jobs'取消'订单'001'::weapp
	Then jobs能获得优惠券规则列表::weapp
		"""
		[{
			"name": "单品券3",
			"remained_count": 3,
			"use_count": 0,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""

@mall3
Scenario:4 后台取消使用微众卡和优惠券支付的'待发货'状态的订单
	#创建微众卡
	Given test登录管理系统::weizoom_card
	When test新建通用卡::weizoom_card
		"""
		[{
			"name":"50元微众卡",
			"prefix_value":"050",
			"type":"virtual",
			"money":"50.00",
			"num":"1",
			"comments":"微众卡"
		}]
		"""

	#微众卡审批出库
	When test下订单::weizoom_card
			"""
			[{
				"card_info":[{
					"name":"50元微众卡",
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
	When jobs添加优惠券规则::weapp
		"""
		[{
			"name": "全体券4",
			"money": 50.00,
			"count": 4,
			"limit_counts": 1,
			"start_date": "今天",
			"end_date": "1天后",
			"coupon_id_prefix": "coupon4_id_"
		}]
		"""
	When jobs为会员发放优惠券::weapp
		"""
		{
			"name": "全体券4",
			"count": 1,
			"members": ["bill"],
			"coupon_ids": ["coupon4_id_1"]
		}
		"""
	Then jobs能获得优惠券规则列表::weapp
		"""
		[{
			"name": "全体券4",
			"remained_count": 3,
			"use_count": 0,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id": "001",
			"pay_type": "微信支付",
			"products":[{
				"name":"商品1",
				"price":100.00,
				"count":1
			}],
			"coupon":"coupon4_id_1",
			"weizoom_card":[{
				"card_name":"050000001",
				"card_pass":"1234567"
			}]
		}
		"""

	Given jobs登录系统::weapp
	Then jobs能获得优惠券规则列表::weapp
		"""
		[{
			"name": "全体券4",
			"remained_count": 3,
			"use_count": 1,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""
	When jobs'取消'订单'001'::weapp
	Then jobs能获得优惠券规则列表::weapp
		"""
		[{
			"name": "全体券4",
			"remained_count": 3,
			"use_count": 0,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""
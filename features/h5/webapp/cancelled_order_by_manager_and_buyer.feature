# watcher: zhangsanxiang@weizoom.com,benchi@weizoom.com
#_author_:张三香 2016.01.13
#针对bug-使用优惠券购买商品，然后再取消订单，优惠券的已使用变成-1

Feature: 后台和手机端对同一订单进行取消订单操作

Background:
	Given 重置'weapp'的bdd环境
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

@mall3 @ztq
Scenario:1 后台先取消,手机端再取消
	bill购买商品，使用优惠券金额小于商品金额
	生成'待支付'订单
	jobs在后台进行取消订单操作
	手机端再进行取消订单操作

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

	Given jobs登录系统::weapp
	When jobs'取消'订单'001'::weapp
	When bill访问jobs的webapp
	Then bill'不能'取消订单'001'
	Given jobs登录系统::weapp
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

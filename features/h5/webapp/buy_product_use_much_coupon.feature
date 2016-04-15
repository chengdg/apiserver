# watcher: fengxuejing@weizoom.com,benchi@weizoom.com
# __author__ : "冯雪静"

Feature: 在webapp中使用优惠券购买商品（使用多商品券购买）

Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
	And jobs已添加商品规格:weapp
		"""
		[{
			"name": "尺寸",
			"type": "文字",
			"values": [{
				"name": "M"
			}, {
				"name": "S"
			}]
		}]
		"""
	And jobs已添加商品:weapp
		"""
		[ {
			"name": "商品1",
			"price": 10.00
		},{
			"name": "商品2",
			"price": 10.00
		},{
			"name": "商品3",
			"price": 20.00
		}, {
			"name": "商品5",
			"is_enable_model": "启用规格",
			"model": {
				"models":{
					"M": {
						"price": 15.00,
						"stock_type": "无限"
					},
					"S": {
						"price": 20.00,
						"stock_type": "无限"
					}
				}
			}
		}, {
			"name": "商品6",
			"price": 20.00,
			"weight": 1,
			"postage": 10.00
		}]
		"""
	#支付方式
	Given jobs已添加支付方式:weapp
		"""
		[{
			"type": "微信支付",
			"is_active": "启用"
		}, {
			"type": "货到付款",
			"is_active": "启用"
		}]
		"""
	Given jobs已添加了优惠券规则:weapp
		"""
		[{
			"name": "优惠券1",
			"money": 1,
			"start_date": "今天",
			"end_date": "1天后",
			"coupon_id_prefix": "coupon1_id_",
			"coupon_product": "商品1,商品2,商品3"
		}, {
			"name": "优惠券2",
			"money": 10,
			"start_date": "今天",
			"end_date": "2天后",
			"using_limit": "满50元可以使用",
			"coupon_id_prefix": "coupon2_id_",
			"coupon_product": "商品1,商品2,商品3,商品5"
		}, {
			"name": "优惠券5",
			"money": 10,
			"start_date": "今天",
			"end_date": "2天后",
			"using_limit": "满50元可以使用",
			"coupon_id_prefix": "coupon5_id_",
			"coupon_product": "商品3,商品5"
		}, {
			"name": "优惠券6",
			"money": 100,
			"start_date": "今天",
			"end_date": "2天后",
			"coupon_id_prefix": "coupon6_id_",
			"coupon_product": "商品6"
		}]
		"""
	When bill关注jobs的公众号
	When bill访问jobs的webapp
	When bill领取jobs的优惠券:weapp
		"""
		[{
			"name": "优惠券1",
			"coupon_ids": ["coupon1_id_2", "coupon1_id_1"]
		},{
			"name": "优惠券2",
			"coupon_ids": ["coupon2_id_2", "coupon2_id_1"]
		}, {
			"name": "优惠券5",
			"coupon_ids": ["coupon5_id_2", "coupon5_id_1"]
		}]
		"""
	When tom关注jobs的公众号
	When tom访问jobs的webapp
	When tom领取jobs的优惠券:weapp
		"""
		[{
			"name": "优惠券1",
			"coupon_ids": ["coupon1_id_3", "coupon1_id_4"]
		}, {
			"name": "优惠券6",
			"coupon_ids": ["coupon6_id_2", "coupon6_id_1"]
		}]
		"""


Scenario:1 使用多商品优惠劵进行购买
	1.该多商品适用于商品1，商品2，商品3
	2.如果商品6使用，则购买失败

	Given jobs登录系统:weapp
	Then jobs能获得优惠券'优惠券1'的码库:weapp
		"""
		{
			"coupon1_id_1": {
				"money": 1.0,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			},
			"coupon1_id_2": {
				"money": 1.0,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""
	When bill访问jobs的webapp
	#第一次使用 购买商品1，商品3成功
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1
			},{
				"name": "商品3",
				"count": 1
			}],
			"coupon": "coupon1_id_1"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 29.0,
			"product_price": 30.0,
			"coupon_money": 1.0
		}
		"""
	#第二次使用 购买商品2 购买失败
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品6",
				"count": 1
			}],
			"coupon": "coupon1_id_2"
		}
		"""
	Then bill获得创建订单失败的信息'该优惠券不能购买订单中的商品'
	Given jobs登录系统:weapp
	Then jobs能获得优惠券'优惠券1'的码库:weapp
		"""
		{
			"coupon1_id_1": {
				"money": 1.0,
				"status": "已使用",
				"consumer": "bill",
				"target": "bill"
			},
			"coupon1_id_2": {
				"money": 1.0,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""


Scenario:2 使用多商品优惠劵进行购买，该多商品券适用于并且商品3满50元才可以使用，而不是订单满50可用
	1 买3件商品3，共60元，满足条件，可用单品劵；
	2 买1件商品3，买一件商品2，订单满50，但单品不满50，不可以使用该单品卷

	Given jobs登录系统:weapp
	Then jobs能获得优惠券'优惠券2'的码库:weapp
		"""
		{
			"coupon2_id_1": {
				"money": 10.0,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			},
			"coupon2_id_2": {
				"money": 10.0,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""
	When bill访问jobs的webapp
	#第一次使用 购买3个商品3，满足使用条件，成功
	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品3",
				"count": 3
			}],
			"coupon": "coupon2_id_1"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 50.0,
			"product_price": 60.0,
			"coupon_money": 10.0
		}
		"""
	#第二次使用 购买商品3+商品2 订单购买失败
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品3",
				"count": 1
			},{
				"name": "商品2",
				"count": 1
			}],
			"coupon": "coupon2_id_2"
		}
		"""
	Then bill获得创建订单失败的信息'该优惠券指定商品金额不满足使用条件'
	Given jobs登录系统:weapp
	Then jobs能获得优惠券'优惠券2'的码库:weapp
		"""
		{
			"coupon2_id_1": {
				"money": 10.0,
				"status": "已使用",
				"consumer": "bill",
				"target": "bill"
			},
			"coupon2_id_2": {
				"money": 10.0,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""
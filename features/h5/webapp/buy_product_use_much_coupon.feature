# watcher: fengxuejing@weizoom.com,benchi@weizoom.com
# __author__ : "冯雪静"

Feature: 在webapp中使用优惠券购买商品（使用多商品券购买）
	"""
	多商品优惠券
		1.使用多商品券购买其中一个关联的商品，购买成功
		2.使用多商品券购买没有关联的商品，提示不能使用
		3.使用多商品券购买多个关联的商品，满足条件购买成功
		4.使用多商品券购买多个关联的商品，不满足条件提示不能使用
		5.使用多商品券购买多个关联的商品金额小于优惠券，满足条件购买成功
		6.使用多商品券购买1个关联的商品和一个没有关联的商品金额小于优惠券，不满足条件提示不能使用
		7.使用多商品券购买多个关联的商品金额小于优惠券，满足条件购买成功，优惠券不抵扣运费
		8.修改关联的部分商品名称和价格后，使用多商品券购买关联的商品，满足条件购买成功
		9.下架关联的部分商品后，使用多商品券购买关联的商品，满足条件购买成功
		10.删除关联的部分商品后，使用多商品券购买关联的商品，满足条件购买成功
		【跳转页面】
		11.从个人中心点击多商品券/点击立即使用，跳转到所关联优惠券的商品列表，title显示优惠券名称
		12.多商品券关联一个商品，商品下架后，跳转到无商品页面，显示去逛逛
		13.多商品券关联一个商品，商品删除后，跳转到无商品页面，显示去逛逛
		14.多商品券关联多个商品，商品全部下架后，跳转到无商品页面，显示去逛逛
		15.多商品券关联多个商品，商品全部删除后，跳转到无商品页面，显示去逛逛
	"""

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
		[{
			"name": "商品1",
			"price": 10.00
		},{
			"name": "商品2",
			"price": 10.00
		},{
			"name": "商品3",
			"price": 20.00,
			"weight": 1,
			"postage": 10.00
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
			"money": 100,
			"start_date": "今天",
			"end_date": "2天后",
			"using_limit": "满50元可以使用",
			"coupon_id_prefix": "coupon5_id_",
			"coupon_product": "商品3,商品5"
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

@mall3 @ztq
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
			}],
			"coupon": "coupon1_id_1"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 9.0,
			"product_price": 10.0,
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

@mall3 @ztq
Scenario:2 使用多商品优惠劵进行购买，该多商品券有使用限制
	1.该多品券适用于商品1,商品2,商品3,商品5
	2.满足条件，可使用优惠券
	3.不满足条件，不能使用优惠券


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
	#第一次使用，满足使用条件，成功
	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品1",
				"count": 1
			}, {
				"name": "商品2",
				"count": 1
			}, {
				"name": "商品5",
				"count": 1,
				"model": "S"
			}, {
				"name": "商品5",
				"count": 1,
				"model": "M"
			}],
			"coupon": "coupon2_id_1"
		}
		"""

	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 45.0,
			"product_price": 55.0,
			"coupon_money": 10.0
		}
		"""
	#第二次使用 购买商品1+商品2 订单购买失败
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
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

@mall3 @ztq
Scenario:3 使用多商品优惠券进行购买，优惠券金额大于商品金额
	1.优惠券金额大于商品金额，满足条件，可使用
	2.优惠券金额大于商品金额，不满足条件的商品，不可使用
	3.优惠券金额大于商品金额，不会抵扣运费

	Given jobs登录系统:weapp
	Then jobs能获得优惠券'优惠券5'的码库:weapp
		"""
		{
			"coupon5_id_1": {
				"money": 100.0,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			},
			"coupon5_id_2": {
				"money": 100.0,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""
	#满足条件，可以使用优惠券
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品5",
				"count": 2,
				"model": "M"
			},{
				"name": "商品5",
				"count": 1,
				"model": "S"
			}],
			"coupon": "coupon5_id_1"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待发货",
			"final_price": 0.0,
			"product_price": 50.0,
			"coupon_money": 50.0
		}
		"""
	#不满足条件，不可使用优惠券
	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品5",
				"count": 2,
				"model": "M"
			},{
				"name": "商品6",
				"count": 1
			}],
			"coupon": "coupon5_id_3"
		}
		"""
	Then bill获得创建订单失败的信息'该优惠券指定商品金额不满足使用条件'
	#满足条件可使用优惠券，但是不能抵扣运费
	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品3",
				"count": 1
			},{
				"name": "商品5",
				"count": 2,
				"model": "M"
			}],
			"coupon": "coupon5_id_2"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 10.0,
			"product_price": 50.0,
			"coupon_money": 50.0,
			"postage":10.0
		}
		"""
	Given jobs登录系统:weapp
	Then jobs能获得优惠券'优惠券5'的码库:weapp
		"""
		{
			"coupon5_id_1": {
				"money": 100.0,
				"status": "已使用",
				"consumer": "bill",
				"target": "bill"
			},
			"coupon5_id_2": {
				"money": 100.0,
				"status": "已使用",
				"consumer": "bill",
				"target": "bill"
			}
		}
		"""

@mall3 @ztq
Scenario:4 修改多商品优惠券关联的商品后，使用多商品优惠券进行购买
	1.修改部分商品价格后，进行购买
	2.下架部分商品后，进行购买
	3.删除部分商品后，进行购买

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
	When jobs更新商品'商品1':weapp
		"""
		{
			"name": "商品11",
			"price": 20.00
		}
		"""
	When bill访问jobs的webapp
	#修改商品后，使用优惠券
	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品11",
				"count": 1
			}, {
				"name": "商品2",
				"count": 1
			}, {
				"name": "商品5",
				"count": 1,
				"model": "S"
			}],
			"coupon": "coupon2_id_1"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 40.0,
			"product_price": 50.0,
			"coupon_money": 10.0
		}
		"""
	Given jobs登录系统:weapp
	When jobs'下架'商品'商品3':weapp
	When bill访问jobs的webapp
	#下架部分商品后，使用优惠券
	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品11",
				"count": 1
			}, {
				"name": "商品2",
				"count": 1
			}, {
				"name": "商品5",
				"count": 1,
				"model": "S"
			}],
			"coupon": "coupon2_id_2"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 40.0,
			"product_price": 50.0,
			"coupon_money": 10.0
		}
		"""
	Given jobs登录系统:weapp
	When jobs'永久删除'商品'商品2':weapp
	When bill访问jobs的webapp
	#删除部分商品后，使用优惠券
	#直接使用优惠券，没有先领取，直接输入优惠券吗
	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品11",
				"count": 2
			}, {
				"name": "商品5",
				"count": 1,
				"model": "S"
			}],
			"coupon": "coupon2_id_3"
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
				"status": "已使用",
				"consumer": "bill",
				"target": "bill"
			},
			"coupon2_id_3": {
				"money": 10.0,
				"status": "已使用",
				"consumer": "bill",
				"target": ""
			}
		}
		"""

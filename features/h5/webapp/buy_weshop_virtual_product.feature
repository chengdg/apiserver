# watcher: benchi@weizoom.com, zhangsanxiang@weizoom.com
#_author_:张三香 2016.05.23

Feature:购买虚拟产品
	"""
		0、特别备注：此功能只开放给微众商城
		1、微众卡类型的商品，只能单独下单，不能和其他商品一起下单（购物车点击【去结算】时会进行校验）
		2、微众卡类型的商品，不能使用微众卡进行支付
		3、微众卡和虚拟类型的商品，和其他商品一样均可参与促销活动
	"""

Background:
	Given 重置weapp的bdd环境
	Given 设置jobs为自营平台账号
	Given jobs登录系统:weapp
	And jobs已添加商品分类:weapp
		"""
		[{
			"name": "分类1"
		},{
			"name": "分类2"
		}]
		"""
	And jobs已添加供货商:weapp
		"""
		[{
			"name": "微众",
			"responsible_person": "张大众",
			"supplier_tel": "15211223344",
			"supplier_address": "北京市海淀区海淀科技大厦",
			"remark": "备注"
		}, {
			"name": "稻香村",
			"responsible_person": "许稻香",
			"supplier_tel": "15311223344",
			"supplier_address": "北京市朝阳区稻香大厦",
			"remark": ""
		}]
		"""
	And jobs已添加支付方式:weapp
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
	When jobs开通使用微众卡权限:weapp
	When jobs添加支付方式:weapp
		"""
		[{
			"type": "微众卡支付",
			"description": "我的微众卡支付",
			"is_active": "启用"
		}]
		"""
	Given jobs已添加商品:weapp
		"""
		[{
			"name": "微众虚拟商品1",
			"product_type":"微众卡",
			"supplier": "微众",
			"purchase_price": 9.00,
			"promotion_title": "10元通用卡",
			"categories": "分类1,分类2",
			"bar_code":"112233",
			"min_limit":1,
			"is_member_product":"off",
			"price": 10.00,
			"weight": 1.0,
			"stock_type": "有限",
			"stocks": 0,
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou1.jpg"
			},{
				"url": "/standard_static/test_resource_img/hangzhou2.jpg"
			}],
			"postage":0.00,
			"pay_interfaces":
				[{
					"type": "在线支付"
				},{
					"type": "货到付款"
				}],
			"detail":"微众虚拟商品1的详情",
			"status":"在售"
		},{
			"name": "微众虚拟商品2",
			"product_type":"微众卡",
			"supplier": "微众",
			"purchase_price": 19.00,
			"promotion_title": "20元通用卡",
			"categories": "",
			"bar_code":"212233",
			"min_limit":2,
			"is_member_product":"off",
			"price": 20.00,
			"weight": 1.0,
			"stock_type": "有限",
			"stocks": 0,
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou1.jpg"
			}],
			"postage":0.00,
			"pay_interfaces":
				[{
					"type": "在线支付"
				},{
					"type": "货到付款"
				}],
			"detail": "微众虚拟商品2的详情",
			"status": "在售"
		},{
			"name": "稻香村虚拟商品3",
			"product_type":"虚拟商品",
			"supplier": "稻香村",
			"purchase_price": 30.00,
			"promotion_title": "稻香村代金券",
			"categories": "分类2",
			"bar_code":"312233",
			"min_limit":1,
			"is_member_product":"off",
			"price": 30.00,
			"weight": 1.0,
			"stock_type": "有限",
			"stocks": 0,
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou1.jpg"
			}],
			"postage":0.00,
			"pay_interfaces":
				[{
					"type": "在线支付"
				}],
			"detail":"稻香村虚拟商品3的详情",
			"status":"在售"
		},{
			"name": "微众普通商品4",
			"product_type":"普通商品",
			"supplier": "微众",
			"purchase_price": 40.00,
			"promotion_title": "非虚拟商品",
			"categories": "分类2",
			"bar_code":"412233",
			"min_limit":1,
			"is_member_product":"off",
			"price": 40.00,
			"weight": 1.0,
			"stock_type": "有限",
			"stocks": 40,
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou1.jpg"
			}],
			"postage":0.00,
			"pay_interfaces":
				[{
					"type": "在线支付"
				},{
					"type": "货到付款"
				}],
			"detail":"微众普通商品4的详情",
			"status":"在售"
		}]
		"""
	And jobs已创建微众卡:weapp
		"""
		{
			"cards":[{
				"id":"0000001",
				"password":"1234567",
				"status":"未使用",
				"price":10.00
			},{
				"id":"0000002",
				"password":"2234567",
				"status":"未使用",
				"price":10.00
			},{
				"id":"0000011",
				"password":"1234567",
				"status":"未使用",
				"price":20.00
			},{
				"id":"0000012",
				"password":"2234567",
				"status":"未使用",
				"price":20.00
			}]
		}
		"""
	When jobs新建福利卡券活动:weapp
		"""
		[{
			"product":
				{
					"name":"微众虚拟商品1",
					"bar_code":"112233",
					"price":10.00
				},
			"activity_name":"10元通用卡",
			"card_start_date":"今天",
			"card_end_date":"30天后",
			"cards":
				[{
					"id":"0000001",
					"password":"1234567"
				},{
					"id":"0000002",
					"password":"2234567"
				}],
			"create_time":"今天"
		},{
			"product":
				{
					"name":"微众虚拟商品2",
					"bar_code":"212233",
					"price":20.00
				},
			"activity_name":"20元通用卡",
			"card_start_date":"今天",
			"card_end_date":"35天后",
			"cards":
				[{
					"id":"0000011",
					"password":"1234567"
				},{
					"id":"0000012",
					"password":"2234567"
				}],
			"create_time":"今天"
		}]
		"""
	Given jobs设定会员积分策略:weapp
		"""
		{
			"be_member_increase_count":20,
			"integral_each_yuan":2
		}
		"""
	When bill关注jobs的公众号

#Scenario:0 购买虚拟商品，不能使用微众卡支付

Scenario:1 '微众卡'类型的商品不能和其他商品一起下单
	When bill访问jobs的webapp
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "微众虚拟商品1",
			"count": 1
		},{
			"name": "微众普通商品4",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"context": [{
				"name": "微众虚拟商品1"
			}, {
				"name": "微众普通商品4"
			}]
		}
		"""
	Then bill获得提示信息'微众卡商品不能与其他商品一起下单'

Scenario:2 购买单个虚拟商品，不参与任何促销活动
	#购买单个虚拟商品，待支付，不会获得福利卡券
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"order_id": "001",
			"date":"今天",
			"products": [{
				"name": "微众虚拟商品1",
				"count": 1
			}],
			"pay_type":"微信支付",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦"
		}
		"""
	Then bill获得我的卡包信息
		"""
		{
			"weizoom_card":[],
			"other_card":[]
		}
		"""
	#付款后，获得福利卡券
	When bill使用支付方式'微信支付'进行支付订单'001'
	Given jobs登录系统:weapp
	When jobs自动发放卡券给订单'001':weapp
		"""
		[{
			"id":"0000001",
			"password":"1234567"
		}]
		"""
	When bill访问jobs的webapp
	Then bill获得我的卡包信息
		"""
		{
			"weizoom_card":
				[{
					"card_start_date":"今天",
					"card_end_date":"30天后",
					"card_remain_value":10.00,
					"card_total_value":10.00,
					"id":"0000001",
					"password":"1234567",
					"order_date":"今天",
					"source":"商城下单",
					"actions":["查看详情"]
				}],
			"other_card":[]
		}
		"""

Scenario:3 购买多个虚拟商品，不参与任何促销活动
	#购买同一供货商的多个虚拟商品
	When bill访问jobs的webapp
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "微众虚拟商品1",
			"count": 1
		},{
			"name": "微众虚拟商品2",
			"count": 2
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"context": [{
				"name": "微众虚拟商品1"
			}, {
				"name": "微众虚拟商品2"
			}]
		}
		"""
	And bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款",
			"order_id": "001",
			"date":"今天"
		}
		"""
	Given jobs登录系统:weapp
	When jobs自动发放卡券给订单'001':weapp
		"""
		[{
			"id":"0000001",
			"password":"1234567"
		},{
			"id":"0000011",
			"password":"1234567"
		},{
			"id":"0000012",
			"password":"2234567"
		}]
		"""
	When bill访问jobs的webapp
	Then bill获得我的卡包信息
		"""
		{
			"weizoom_card":
				[{
					"card_start_date":"今天",
					"card_end_date":"35天后",
					"card_remain_value":20.00,
					"card_total_value":20.00,
					"id":"0000012",
					"password":"2234567",
					"order_date":"今天",
					"source":"商城下单",
					"actions":["查看详情"]
				},{
					"card_start_date":"今天",
					"card_end_date":"35天后",
					"card_remain_value":20.00,
					"card_total_value":20.00,
					"id":"0000011",
					"password":"1234567",
					"order_date":"今天",
					"source":"商城下单",
					"actions":["查看详情"]
				},{
					"card_start_date":"今天",
					"card_end_date":"30天后",
					"card_remain_value":10.00,
					"card_total_value":10.00,
					"id":"0000001",
					"password":"1234567",
					"order_date":"今天",
					"source":"商城下单",
					"actions":["查看详情"]
				}],
			"other_card":[]
		}
		"""

Scenario:4 购买虚拟商品，参与促销活动
	#微众虚拟商品1-参加积分抵扣
	Given jobs登录系统:weapp
	When jobs创建积分应用活动:weapp
		"""
		[{
			"name": "积分应用1",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "微众虚拟商品1",
			"is_permanant_active": false,
			"discount": 50,
			"discount_money": 5.00
		}]
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id": "001",
			"date":"今天",
			"products": [{
				"name": "微众虚拟商品1",
				"count": 1,
				"integral":10,
				"integral_money":5.00
			}],
			"pay_type":"微信支付",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦"
		}
		"""
	When bill使用支付方式'微信支付'进行支付订单'001'
	Given jobs登录系统:weapp
	When jobs自动发放卡券给订单'001':weapp
		"""
		[{
			"id":"0000001",
			"password":"1234567"
		}]
		"""
	When bill访问jobs的webapp
	Then bill获得我的卡包信息
		"""
		{
			"weizoom_card":
				[{
					"card_start_date":"今天",
					"card_end_date":"30天后",
					"card_remain_value":10.00,
					"card_total_value":10.00,
					"id":"0000001",
					"password":"1234567",
					"order_date":"今天",
					"source":"商城下单",
					"actions":["查看详情"]
				}],
			"other_card":[]
		}
		"""
	#微众虚拟商品2-多商品券
	Given jobs登录系统:weapp
	When jobs添加优惠券规则:weapp
		"""
		[{
			"name": "多商品券1",
			"money": 100.00,
			"start_date": "今天",
			"end_date": "1天后",
			"description":"使用说明",
			"coupon_product": "微众虚拟商品2",
			"coupon_id_prefix": "coupon1_id_"
		}]
		"""
	When tom关注jobs的公众号
	When tom访问jobs的webapp
	When tom领取jobs的优惠券:weapp
		"""
		[{
			"name": "多商品券1",
			"coupon_ids": ["coupon1_id_1"]
		}]
		"""
	When tom访问jobs的webapp
	When tom购买jobs的商品
		"""
		{
			"order_id": "002",
			"date":"今天",
			"products": [{
				"name": "微众虚拟商品2",
				"count": 1,
			}],
			"coupon": "coupon1_id_1",
			"pay_type":"微信支付",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦"
		}
		"""
	Given jobs登录系统:weapp
	When jobs自动发放卡券给订单'002':weapp
		"""
		[{
			"id":"0000011",
			"password":"1234567"
		}]
		"""
	When tom访问jobs的webapp
	Then tom获得我的卡包信息
		"""
		{
			"weizoom_card":
				[{
					"card_start_date":"今天",
					"card_end_date":"35天后",
					"card_remain_value":20.00,
					"card_total_value":20.00,
					"id":"0000011",
					"password":"1234567",
					"order_date":"今天",
					"source":"商城下单",
					"actions":["查看详情"]
				}],
			"other_card":[]
		}
		"""
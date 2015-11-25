# __author__ : "冯雪静"
#editor:王丽 2015.10.20

#微众精选：购买促销商品
Feature: 购买促销商品
	"""
	1.不同供货商的商品进行促销,限时抢购，买赠，使用优惠券（全体券）
	2.不同供货商的商品进行会员价购买，会员价，单品券
	3.使用积分购买不同供货商的商品，使用积分，管理员修改金额
	"""


Background:
	Given jobs登录系统
	And jobs已添加供货商
		"""
		[{
			"name": "土小宝",
			"responsible_person": "宝宝",
			"supplier_tel": "13811223344",
			"supplier_address": "北京市海淀区泰兴大厦",
			"remark": "备注卖花生油"
		}, {
			"name": "丹江湖",
			"responsible_person": "陌陌",
			"supplier_tel": "13811223344",
			"supplier_address": "北京市海淀区泰兴大厦",
			"remark": ""
		}]
		"""
	And jobs已添加支付方式
		"""
		[{
			"type": "微信支付",
			"is_active": "启用"
		}, {
			"type": "货到付款",
			"is_active": "启用"
		}]
		"""
	And jobs已添加商品
		"""
		[{
			"supplier": ["土小宝"],
			"name": "商品1",
			"price": 100.00
		}, {
			"supplier": ["丹江湖"],
			"name": "商品2",
			"price": 100.00
		}, {
			"supplier": ["土小宝"],
			"name": "商品3",
			"price": 100.00
		}]
		"""
	And jobs已添加了优惠券规则
		"""
		[{
			"name": "优惠券1",
			"money": 50.00,
			"count": 2,
			"coupon_id_prefix": "coupon1_id_"
		}]
		"""
	When jobs添加会员等级
		"""
		[{
			"name": "铜牌会员",
			"upgrade": "手动升级",
			"discount": "9"
		}, {
			"name": "银牌会员",
			"upgrade": "手动升级",
			"discount": "8"
		}, {
			"name": "金牌会员",
			"upgrade": "手动升级",
			"discount": "7"
		}]
		"""
	Given bill关注jobs的公众号
	When bill访问jobs的webapp
	And bill设置jobs的webapp的收货地址
		"""
		{
			"area": "北京市,北京市,海淀区",
			"ship_address": "泰兴大厦"
		}
		"""


@mall2 @buy   @supplier 
Scenario: 1 不同供货商的商品进行促销
	设置促销活动进行购买

	#同时购买限时抢购，买赠，使用优惠券，不同供货商
	Given jobs登录系统
	When jobs创建限时抢购活动
		"""
		{
			"name": "商品1限时抢购",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品1",
			"member_grade": "全部",
			"count_per_purchase": 2,
			"promotion_price": 50.00
		}
		"""
	When jobs创建买赠活动
		"""
		[{
			"name": "商品2买一赠一",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品2",
			"premium_products": [{
				"name": "商品3",
				"count": 1
			}],
			"count": 1,
			"member_grade":"全部",
			"is_enable_cycle_mode": true
		}]
		"""
	When bill访问jobs的webapp
	When bill领取jobs的优惠券
		"""
		[{
			"name": "优惠券1",
			"coupon_ids": ["coupon1_id_1"]
		}]
		"""
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 1
		}, {
			"name": "商品2",
			"count": 1
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
			}],
			"coupon": "coupon1_id_1"
		}
		"""
	And bill在购物车订单编辑中点击提交订单
		"""
		{
			"pay_type": "货到付款",
			"order_no": "001"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"order_no": "001",
			"status": "待支付",
			"final_price": 100.00,
			"coupon_money": 50.00,
			"products": [{
				"name": "商品1",
				"price": 50.00,
				"count": 1
			}, {
				"name": "商品2",
				"price": 100.00,
				"count": 1,
				"promotion": {
					"type": "premium_sale"
				}
			}, {
				"name": "商品3",
				"count": 1,
				"promotion": {
					"type": "premium_sale:premium_product"
				}
			}],
			"actions": ["取消订单", "支付"]
		}
		"""
	Given jobs登录系统
	Then jobs可以获得最新订单详情
		"""
		{
			"order_no": "001",
			"status": "待支付",
			"final_price": 100.00,
			"save_money": 100.00,
			"product_price": 150.00,
			"coupon_money": 50.00,
			"promotion_saved_money": 50.00,
			"actions": ["支付", "修改价格", "取消订单"],
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1
			}, {
				"name": "商品2",
				"price": 100.00,
				"count": 1,
				"promotion": {
					"type": "premium_sale"
				}
			}, {
				"name": "商品3",
				"count": 1,
				"price": 100.00,
				"promotion": {
					"type": "premium_sale:premium_product"
				}
			}]
		}
		"""
		# 订单详情里不显示member	"member": "bill",
	When bill访问jobs的webapp
	When bill使用支付方式'微信支付'进行支付
	Given jobs登录系统
	Then jobs可以看到订单列表
		"""
		[{
			"order_no": "001",
			"status": "待发货",
			"final_price": 100.00,
			"save_money": 100.00,
			"actions": ["申请退款"],
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝",
				"status": "待发货",
				"actions": ["发货"]
			}, {
				"name": "商品2",
				"price": 100.00,
				"count": 1,
				"promotion": {
					"type": "premium_sale"
				},
				"supplier": "丹江湖",
				"status": "待发货",
				"actions": ["发货"]
			}, {
				"name": "商品3",
				"count": 1,
				"price": 100.00,
				"promotion": {
					"type": "premium_sale:premium_product"
				},
				"supplier": "丹江湖",
				"status": "待发货",
				"actions": ["发货"]
			}]
		}]
		"""

@mall2 @buy   @supplier
Scenario: 2 不同供货商的商品进行会员价购买
	设置会员等级价的商品进行购买

	Given jobs登录系统
	When jobs更新商品'商品1'
		"""
		{
			"name": "商品1",
			"price": 100.00,
			"is_member_product": "on"
		}
		"""
	And jobs更新"bill"的会员等级
		"""
		{
			"name": "bill",
			"member_rank": "银牌会员"
		}
		"""
	When bill访问jobs的webapp
	When bill领取jobs的优惠券
		"""
		[{
			"name": "优惠券1",
			"coupon_ids": ["coupon1_id_1"]
		}]
		"""
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 1
		}, {
			"name": "商品2",
			"count": 1
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
			}],
			"coupon": "coupon1_id_1"
		}
		"""
	And bill在购物车订单编辑中点击提交订单
		"""
		{
			"pay_type": "货到付款",
			"order_no": "001"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"order_no": "001",
			"status": "待支付",
			"final_price": 130.00,
			"coupon_money": 50.00,
			"products": [{
				"name": "商品1",
				"price": 80.00,
				"count": 1
			}, {
				"name": "商品2",
				"price": 100.00,
				"count": 1
			}],
			"actions": ["取消订单", "支付"]
		}
		"""
	Given jobs登录系统
	Then jobs可以获得最新订单详情
		"""
		{
			"order_no": "001",
			"status": "待支付",
			"final_price": 130.00,
			"save_money": 70.00,
			"product_price": 180.00,
			"coupon_money": 50.00,
			"actions": ["支付", "修改价格", "取消订单"],
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"grade_discounted_money": 20.00,
				"count": 1
			}, {
				"name": "商品2",
				"price": 100.00,
				"count": 1
			}]
		}
		"""
	When bill访问jobs的webapp
	And bill使用支付方式'货到付款'进行支付
	Given jobs登录系统
	Then jobs可以看到订单列表
		"""
		[{
			"order_no": "001",
			"status": "待发货",
			"final_price": 130.00,
			"save_money": 70.00,
			"actions": ["取消订单"],
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝",
				"status": "待发货",
				"actions": ["发货"]
			}, {
				"name": "商品2",
				"price": 100.00,
				"count": 1,
				"supplier": "丹江湖",
				"status": "待发货",
				"actions": ["发货"]
			}]
		}]
		"""

@mall2 @buy   @supplier
Scenario: 3 使用积分购买不同供货商的商品
	使用积分进行购买

	Given jobs登录系统
	And jobs设定会员积分策略
		"""
		{
			"use_ceiling": 50,
			"use_condition": "on",
			"integral_each_yuan": 1
		}
		"""
	When tom关注jobs的公众号
	When tom访问jobs的webapp
	And tom设置jobs的webapp的收货地址
		"""
		{
			"area": "北京市,北京市,海淀区",
			"ship_address": "泰兴大厦"
		}
		"""
	Given jobs已有的会员
		"""
		[{
			"name": "tom",
			"integral":"50"
		}]
		"""
	When tom访问jobs的webapp
	When tom加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 1
		}, {
			"name": "商品2",
			"count": 1
		}]
		"""
	When tom从购物车发起购买操作
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
	And tom在购物车订单编辑中点击提交订单
		"""
		{
			"pay_type": "货到付款",
			"order_no": "001",
			"integral": 50,
			"integral_money": 50
		}
		"""
	Then tom成功创建订单
		"""
		{
			"order_no": "001",
			"status": "待支付",
			"final_price": 150.00,
			"integral_money": 50.00,
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1
			}, {
				"name": "商品2",
				"price": 100.00,
				"count": 1
			}],
			"actions": ["取消订单", "支付"]
		}
		"""
	Given jobs登录系统
	Then jobs可以获得最新订单详情
		"""
		{
			"order_no": "001",
			"status": "待支付",
			"final_price": 150.00,
			"save_money": 50.00,
			"product_price": 200.00,
			"integral_money": 50.00,
			"integral": 50,
			"actions": ["支付", "修改价格", "取消订单"],
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1
			}, {
				"name": "商品2",
				"price": 100.00,
				"count": 1
			}]
		}
		"""
		# "member": "tom",
	When jobs修改订单'001'的价格
		"""
		{
			"order_no": "001",
			"final_price": 100.00
		}
		"""
	When bill访问jobs的webapp
	And bill使用支付方式'货到付款'进行支付
	Given jobs登录系统
	Then jobs可以看到订单列表
		"""
		[{
			"order_no": "001-500",
			"status": "待发货",
			"final_price": 100.00,
			"save_money": 100.00,
			"actions": ["取消订单"],
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1,
				"supplier": "土小宝",
				"status": "待发货",
				"actions": ["发货"]
			}, {
				"name": "商品2",
				"price": 100.00,
				"count": 1,
				"supplier": "丹江湖",
				"status": "待发货",
				"actions": ["发货"]
			}]
		}]
		"""


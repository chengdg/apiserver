#author: 冯雪静
#editor: 师帅 2015.10.19

Feature: 在webapp中购买有会员折扣的商品
	bill能在webapp中购买jobs添加的"会员价的商品"
	"""
	列表页、详情页、购物车页、下单页、订单页，全显示会员价
	1.购买单个会员价商品：直接下单
	2.购买多个会员价商品：从购物车下单
	3.购买多个商品包括会员价商品：从购物车下单，购买的商品有原价和会员价
	4.订单完成后，达到自动升级的条件：会员的订单完成后，满足自动升级的条件，自动升级
	5.使用积分购买商品后，取消订单，积分返回不增加经验值
	"""

Background:
	Given jobs登录系统
	And jobs已添加商品规格
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
	When jobs已添加支付方式
		"""
		[{
			"type": "货到付款",
			"description": "我的货到付款",
			"is_active": "启用"
		},{
			"type": "微信支付",
			"description": "我的微信支付",
			"is_active": "启用",
			"weixin_appid": "12345",
			"weixin_partner_id": "22345",
			"weixin_partner_key": "32345",
			"weixin_sign": "42345"
		}]
		"""
	And jobs已添加商品
		"""
		[{
			"name": "商品1",
			"price": 100.00,
			"is_member_product": "on",
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"stock_type": "有限",
						"stocks": 2
					}
				}
			}
		}, {
			"name": "商品2",
			"is_member_product": "on",
			"is_enable_model": "启用规格",
			"model": {
				"models":{
					"M": {
						"price": 300.00,
						"stock_type": "无限"
					},
					"S": {
						"price": 300.00,
						"stock_type": "无限"
					}
				}
			}
		}, {
			"name": "商品3",
			"price": 200.00
		}]
		"""
	#10积分是一元等于10积分，20积分是首次关注的奖励，30积分是购买商品基础奖励,50积分是订单抵扣上限50%
	Given jobs设定会员积分策略
		"""
		{
			"integral_each_yuan": 10,
			"be_member_increase_count": 20,
			"buy_award_count_for_buyer": 30,
			"use_ceiling": 50
		}
		"""
	And bill关注jobs的公众号
	And tom关注jobs的公众号
	Given jobs登录系统
	Then jobs能获得bill的积分日志
		"""
		[{
			"content": "首次关注",
			"integral": 20
		}]
		"""
	And jobs能获得tom的积分日志
		"""
		[{
			"content": "首次关注",
			"integral": 20
		}]
		"""
	When jobs更新"bill"的会员等级
		"""
		{
			"name": "bill",
			"member_rank": "铜牌会员"
		}
		"""

@mall2 @member_product
Scenario:1 购买单个会员价商品
	jobs添加商品后
	1. tom能在webapp中购买jobs添加的会员价商品
	2. tom是普通会员没有会员折扣
	3. bill能在webapp中购买jobs添加的会员价商品
	4. bill是铜牌会员有会员折扣

	#无会员折扣的购买
	When tom访问jobs的webapp
	And tom购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	Then tom成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 100.00,
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1
			}]
		}
		"""
	#有会员折扣的购买
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 90.00,
			"products": [{
				"name": "商品1",
				"price": 90.00,
				"count": 1
			}]
		}
		"""

@mall2 @member_product
Scenario:2 购买多个会员价商品
	jobs添加商品后
	1. bill能在webapp中把jobs添加的会员价商品添加到购物车
	2. bill能获取购物车的商品
	3. bill能从购物车进行购买jobs的商品

	When bill访问jobs的webapp
	And bill设置jobs的webapp的收货地址
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"area": "北京市,北京市,海淀区",
			"ship_address": "泰兴大厦"
		}
		"""
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 1
		}, {
			"name": "商品2",
			"model": {
				"models":{
					"M": {
						"count": 1
					}
				}
			}
		}, {
			"name": "商品2",
			"model": {
				"models":{
					"S": {
						"count": 1
					}
				}
			}
		}]
		"""
	Then bill能获得购物车
		"""
		{
			"product_groups": [{
				"products": [{
					"name": "商品1",
					"price": 90.00,
					"count": 1
				}, {
					"name": "商品2",
					"price": 270.00,
					"count": 1,
					"model": "M"
				}, {
					"name": "商品2",
					"price": 270.00,
					"count": 1,
					"model": "S"
				}]
			}],
			"invalid_products": []
		}
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"context": [{
				"name": "商品1"
			}, {
				"name": "商品2",
				"model": "M"
			}, {
				"name": "商品2",
				"model": "S"
			}]
		}
		"""
	And bill在购物车订单编辑中点击提交订单
		"""
		{
			"pay_type": "货到付款"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 630.00,
			"products": [{
				"name": "商品1",
				"price": 90.00,
				"count": 1
			}, {
				"name": "商品2",
				"price": 270.00,
				"count": 1,
				"model": "M"
			}, {
				"name": "商品2",
				"price": 270.00,
				"count": 1,
				"model": "S"
			}]
		}
		"""

@mall2 @member_product
Scenario:3 购买多个商品包括会员价商品
	jobs添加商品后
	1. bill能在webapp中购买jobs的商品
	2. bill购买的商品中有普通商品和会员价商品
	
	When bill访问jobs的webapp
	And bill设置jobs的webapp的收货地址
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"area": "北京市,北京市,海淀区",
			"ship_address": "泰兴大厦"
		}
		"""
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 1
		}, {
			"name": "商品3",
			"count": 1
		}]
		"""
	Then bill能获得购物车
		"""
		{
			"product_groups": [{
				"products": [{
					"name": "商品1",
					"price": 90.00,
					"count": 1
				}, {
					"name": "商品3",
					"price": 200.00,
					"count": 1
				}]
			}],
			"invalid_products": []
		}
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"context": [{
				"name": "商品1"
			}, {
				"name": "商品3"
			}]
		}
		"""
	And bill在购物车订单编辑中点击提交订单
		"""
		{
			"pay_type": "货到付款"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 290.00,
			"products": [{
				"name": "商品1",
				"price": 90.00,
				"count": 1
			}, {
				"name": "商品3",
				"price": 200.00,
				"count": 1
			}]
		}
		"""

@mall2 @meberGrade
Scenario:4 订单完成后，达到自动升级的条件
	jobs添加商品后
	1. tom能在webapp中购买jobs的商品后，完成订单后
	2. tom达到自动升级的条件，并升级
	
	Given jobs登录系统
	When jobs开启自动升级
		"""
		{
			"upgrade": "自动升级",
			"condition": ["满足一个条件即可"]
		}
		"""
	When jobs更新会员等级'铜牌会员'
		"""
		{
			"name": "铜牌会员",
			"upgrade": "自动升级",
			"pay_money": 500.00,
			"pay_times": 20,
			"upgrade_lower_bound": 10000,
			"discount": "9"
		}
		"""
	And jobs更新会员等级'银牌会员'
		"""
		{
			"name": "银牌会员",
			"upgrade": "自动升级",
			"pay_money": 1000.00,
			"pay_times": 30,
			"upgrade_lower_bound": 30000,
			"discount": "8"
		}
		"""
	Then jobs能获取会员等级列表
		"""
		[{
			"name": "普通会员",
			"upgrade": "自动升级",
			"discount": "10"
		}, {
			"name": "铜牌会员",
			"upgrade": "自动升级",
			"pay_money": 500.00,
			"pay_times": 20,
			"upgrade_lower_bound": 10000,
			"discount": "9"
		}, {
			"name": "银牌会员",
			"upgrade": "自动升级",
			"pay_money": 1000.00,
			"pay_times": 30,
			"upgrade_lower_bound": 30000,
			"discount": "8"
		}, {
			"name": "金牌会员",
			"upgrade": "手动升级",
			"discount": "7"
		}]
		"""
	When tom访问jobs的webapp
	And tom购买jobs的商品
		"""
		{
			"ship_name": "tom",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"products": [{
				"name": "商品2",
				"model": "M",
				"count": 2
			}]
		}
		"""
	When tom使用支付方式'货到付款'进行支付
	Then tom支付订单成功
		"""
		{
			"status": "待发货",
			"final_price": 600.00,
			"products": [{
				"name": "商品2",
				"price": 300.00,
				"model": "M",
				"count": 2
			}]
		}
		"""
	Given jobs登录系统
	Then jobs可以获得最新订单详情
		"""
		{
			"status": "待发货",
			"actions": ["发货", "取消订单"],
			"final_price": 600.00,
			"ship_name": "tom",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"products": [{
				"name": "商品2",
				"price": 300.00,
				"model": "M",
				"count": 2
			}]
		}
		"""
	When jobs对最新订单进行发货
	Then jobs可以获得最新订单详情
		"""
		{
			"status": "已发货",
			"actions": ["标记完成", "取消订单", "修改物流"],
			"final_price": 600.00,
			"ship_name": "tom",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"products": [{
				"name": "商品2",
				"price": 300.00,
				"model": "M",
				"count": 2
			}]
		}
		"""
	#tom已经满足一个升级条件，自动升级为铜牌会员
	When jobs'完成'最新订单
	Then jobs能获得tom的积分日志
		"""
		[{
			"content": "购物返利",
			"integral": 30
		}, {
			"content": "首次关注",
			"integral": 20
		}]
		"""
	And jobs可以获得会员列表
		"""
		[{
			"name": "tom",
			"member_rank": "铜牌会员",
			"pay_money": 600.00,
			"pay_times": 1,
			"integral": 50
		}, {
			"name": "bill",
			"member_rank": "铜牌会员",
			"pay_money": 0.00,
			"pay_times": 0,
			"integral": 20
		}]
		"""

@mall2 @integral_experience
Scenario:5 使用积分购买商品后，取消订单，积分返回
	jobs添加商品后
	1. bill能在webapp中使用积分购买jobs的商品后，创建订单后
	2. jobs取消bill的订单，bill积分返还

	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"order_id":"0000001",
			"products": [{
				"name": "商品1",
				"count": 1
			}],
			"integral": 20
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 88.00,
			"integral": 20,
			"products": [{
				"name": "商品1",
				"price": 90.00,
				"count": 1
			}]
		}
		"""
	When bill使用支付方式'货到付款'进行支付
	Then bill支付订单成功
		"""
		{
			"status": "待发货",
			"final_price": 88.00,
			"integral": 20,
			"products": [{
				"name": "商品1",
				"price": 90.00,
				"count": 1
			}]
		}
		"""
	Given jobs登录系统
	When jobs对订单进行发货
		"""
		{
			"order_no":"0000001",
			"logistics":"顺丰速运",
			"number":"123456789"
		}
		"""
	When jobs'完成'订单'0000001'
	when bill访问jobs的webapp
	Then bill在jobs的webapp中拥有30会员积分
	Then bill在jobs的webapp中获得积分日志
		"""
		[{
			"content": "购物返利",
			"integral": 30
		}, {
			"content": "购物抵扣",
			"integral": -20
		}, {
			"content": "首次关注",
			"integral": 20
		}]
		"""
	Given jobs登录系统
	Then jobs可以获得最新订单详情
		"""
		{
			"status": "已完成",
			"final_price": 88.00,
			"actions": ["申请退款"]
		}
		"""
	When jobs'申请退款'订单'0000001'
	When jobs通过财务审核'退款成功'订单'0000001'
	Then jobs可以获得最新订单详情
		"""
		{
			"status": "退款成功",
			"final_price": 88.00,
			"actions": []
		}
		"""
	And jobs能获得bill的积分日志
		"""
		[{
			"content": "取消订单 返还积分",
			"integral": 20
		}, {
			"content": "购物返利",
			"integral": 30
		}, {
			"content": "购物抵扣",
			"integral": -20
		}, {
			"content": "首次关注",
			"integral": 20
		}]
		"""
	And jobs可以获得会员列表
		"""
		[{
			"name": "tom",
			"member_rank": "普通会员",
			"pay_money": 0.00,
			"pay_times": 0,
			"integral": 20
		}, {
			"name": "bill",
			"member_rank": "铜牌会员",
			"pay_money": 88.00,
			"pay_times": 1,
			"integral": 50
		}]
		"""
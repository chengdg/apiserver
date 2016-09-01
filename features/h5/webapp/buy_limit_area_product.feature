# __author__ : "冯雪静"

Feature: 手机端购买有禁售地区和有仅售地区的商品
	"""
		商品设置禁售地区或仅售地区，手机端购买
			1.购买一个商品超出配送范围时，提示超出范围，操作“返回修改”是返回到上一个页面
			2.购买多个商品时，其中有商品超出配送范围时，提示超出范围，操作“返回修改”，“移除以上商品”是留在编辑订单页报错的商品被移除了
			3.购买多个商品时，全部商品超出配送范围时，提示超出范围，操作“返回修改”
			4.如：有商品已删除、已下架、已售罄、限制购买、库存不足、已经过期、已赠完和商品超出配送范围，不同商品并列提示
				同一个商品优先提示-已删除、已下架、已售罄、限制购买、库存不足、已经过期、已赠完
	"""

Background:
	Given 重置'weapp'的bdd环境
	Given jobs登录系统::weapp
	And jobs已添加支付方式::weapp
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
	When jobs添加限定区域配置::weapp
		"""
		{
			"name": "禁售商品地区",
			"limit_area": [{
				"area": "华北-东北",
				"province": "河北省",
				"city": ["秦皇岛市","唐山市","沧州市"]
			}, {
				"area": "西北-西南",
				"province": "西藏",
				"city": ["拉萨市"]
			}]
		}
		"""
	When jobs添加限定区域配置::weapp
		"""
		{
			"name": "仅售商品地区",
			"limit_area": [{
				"area": "直辖市",
				"province": ["北京市","天津市","上海市","重庆市"]
			}]
		}
		"""
	When jobs添加限定区域配置::weapp
		"""
		{
			"name": "仅售商品多地区",
			"limit_area": [{
				"area": "华北-东北",
				"province": "河北省",
				"city": ["石家庄市","唐山市","沧州市"]
			},{
				"area": "西北-西南",
				"province": "陕西省",
				"city": ["西安市"]
			}]
		}
		"""
	And jobs已添加商品::weapp
		"""
		[{
			"name": "商品1",
			"price": 9.90,
			"limit_zone_type": {
				"禁售地区": {
					"limit_zone": "禁售商品地区"
				}
			}
		}, {
			"name": "商品2",
			"price": 8.80,
			"limit_zone_type": {
				"仅售地区": {
					"limit_zone": "仅售商品地区"
				}
			}
		}, {
			"name": "商品3",
			"price": 10.00,
			"stock_type": "有限",
			"stocks": 2,
			"limit_zone_type": {
				"仅售地区": {
					"limit_zone": "仅售商品多地区"
				}
			}
		}, {
			"name": "商品4",
			"price": 10.00
		}]
		"""
	And bill关注jobs的公众号


Scenario:1 购买1个商品地区不支持配送，提交订单错误提示
	bill购买一个商品地区是禁售地区，不支持配送
	1.提交订单不成功，提示错误信息

	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "河北省 秦皇岛市 昌黎县",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款",
			"products": [{
				"name": "商品1",
				"count": 2
			}]
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
			"detail": {
				"msg": {
					"该订单内商品状态发生变化": [{
						"id": "商品1",
						"short_msg": "超出范围"
					}],
					"actions": ["返回修改"]
				}
			}
		}
		"""


Scenario:2 购买多个商品地区不支持配送，提交订单错误提示
	1.bill购买多个商品其中一个商品地区是禁售地区，不支持配送
	2.bill购买多个商品其中多个商品地区是禁售地区，不支持配送
	3.bill购买多个商品全部商品地区是禁售地区，不支持配送

	When bill访问jobs的webapp
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 1
		},{
			"name": "商品4",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "click",
			"context": [{
				"name": "商品1"
			},{
				"name": "商品4"
			}]
		}
		"""
	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "西藏自治区 拉萨市 城关区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款"
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
			"detail": {
				"msg": {
					"该订单内商品状态发生变化": [{
						"id": "商品1",
						"short_msg": "超出范围"
					}],
					"actions": ["返回修改", "移除以上商品"]
				}
			}
		}
		"""
	#有多个商品提示信息
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 1
		},{
			"name": "商品2",
			"count": 1
		},{
			"name": "商品3",
			"count": 1
		},{
			"name": "商品4",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "click",
			"context": [{
				"name": "商品1"
			},{
				"name": "商品2"
			},{
				"name": "商品3"
			},{
				"name": "商品4"
			}]
		}
		"""
	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "西藏自治区 拉萨市 城关区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款"
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
			"detail": {
				"msg": {
					"该订单内商品状态发生变化": [{
						"id": "商品1",
						"short_msg": "超出范围"
					}, {
						"id": "商品2",
						"short_msg": "超出范围"
					}, {
						"id": "商品3",
						"short_msg": "超出范围"
					}],
					"actions": ["返回修改", "移除以上商品"]
				}
			}
		}
		"""
	#有多个商品提示信息
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 1
		},{
			"name": "商品2",
			"count": 1
		},{
			"name": "商品3",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "click",
			"context": [{
				"name": "商品1"
			},{
				"name": "商品2"
			},{
				"name": "商品3"
			}]
		}
		"""
	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "西藏自治区 拉萨市 城关区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款"
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
			"detail": {
				"msg": {
					"该订单内商品状态发生变化": [{
						"id": "商品1",
						"short_msg": "超出范围"
					}, {
						"id": "商品2",
						"short_msg": "超出范围"
					}, {
						"id": "商品3",
						"short_msg": "超出范围"
					}],
					"actions": ["返回修改"]
				}
			}
		}
		"""


Scenario:3 购买商品配置了禁售地区，后台修改限定区域模板
	1.bill购买商品配置了禁售地区，jobs修改限定区域模板后，bill成功下单
	2.bill购买商品配置了禁售地区,jobs删除限定区域模板后，bill成功下单

	Given jobs登录系统::weapp
	When jobs修改'禁售地区'限定区域配置::weapp
		"""
		{
			"name": "禁售商品地区",
			"limit_area": [{
				"area": "西北-西南",
				"province": "西藏",
				"city": ["拉萨市"]
			}]
		}
		"""
	Then jobs能获取商品'商品1'::weapp
		"""
		{
			"name": "商品1",
			"price": 9.90,
			"limit_zone_type": {
				"禁售地区": {
					"limit_zone": "禁售商品地区"
				}
			}
		}
		"""
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "河北省 秦皇岛市 昌黎县",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待发货",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "河北省 秦皇岛市 昌黎县",
			"ship_address": "泰兴大厦",
			"final_price": 9.90
		}
		"""
	#jobs删除限定区域模板后，商品默认不限制
	Given jobs登录系统::weapp
	When jobs删除'禁售商品地区'限定区域配置::weapp
	Then jobs能获取商品'商品1'::weapp
		"""
		{
			"name": "商品1",
			"price": 9.90,
			"limit_zone_type": "无限制"
		}
		"""
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 1
		},{
			"name": "商品4",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "click",
			"context": [{
				"name": "商品1"
			},{
				"name": "商品4"
			}]
		}
		"""
	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "西藏自治区 拉萨市 城关区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待发货",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "西藏自治区 拉萨市 城关区",
			"ship_address": "泰兴大厦",
			"final_price": 19.90
		}
		"""
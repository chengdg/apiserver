# watcher: fengxuejing@weizoom.com, benchi@weizoom.com
# __author__ : "冯雪静"
#editor：王丽 2016-02-22
@func:webapp.modules.mall.views.list_products
Feature: 在webapp中购买商品
	bill能在webapp中购买jobs添加的"商品"

Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
	Given jobs已添加商品分类:weapp
		"""
		[{
			"name": "分类1"
		}, {
			"name": "分类2"
		}, {
			"name": "分类3"
		}]
		"""
	And jobs已有微众卡支付权限:weapp
	And jobs已添加支付方式:weapp
		"""
		[{
			"type": "支付宝"
		},{
			"type": "微众卡支付"
		}, {
			"type": "货到付款"
		}, {
			"type": "微信支付"
		}]
		"""
	And jobs已添加商品规格:weapp
		"""
		[{
			"name": "颜色",
			"type": "图片",
			"values": [{
				"name": "黑色",
				"image": "/standard_static/test_resource_img/hangzhou1.jpg"
			}, {
				"name": "白色",
				"image": "/standard_static/test_resource_img/hangzhou2.jpg"
			}]
		}, {
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
			"price": 9.9
		}, {
			"name": "商品2",
			"price": 8.8
		},{
			"name": "商品3",
			"is_enable_model": "启用规格",
			"model": {
				"models": {
					"黑色 M": {
						"price": 10.0
					}
				}
			}
		}, {
			"name": "商品4",
			"shelve_type": "下架",
			"model": {
				"models": {
					"standard": {
						"price": 5,
						"stock_type": "无限"
					}
				}
			}
		}, {
			"name": "商品5",
			"model": {
				"models": {
					"standard": {
						"price": 5.0,
						"stock_type": "有限",
						"stocks": 2
					}
				}
			}
		}, {
			"name": "商品6",
			"price": 9.9,
			"pay_interfaces":[{
				"type": "在线支付"
			}]
		}]
		"""
	And bill关注jobs的公众号

@mall3 @mall.webapp @zy_bp01 @ztq2
Scenario:1 购买单个商品
	jobs添加商品后
	1. bill能在webapp中购买jobs添加的商品
	1. bill的订单中的信息正确

	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type":"微信支付",
			"products": [{
				"name": "商品1",
				"count": 2
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 19.8,
			"products": [{
				"name": "商品1",
				"price": 9.9,
				"count": 2
			}]
		}
		"""

@mall3 @mall.webapp @zy_bp02
Scenario:2 购买商品时，使用订单备注
	bill在购买jobs添加的商品时
	1. 添加了"订单备注"，则jobs能在管理系统中看到该"订单备注"
	2. 不添加'订单备注', 则jobs能在管理系统中看到"订单备注"为空字符串

	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"pay_type":"微信支付",
			"products": [{
				"name": "商品1",
				"count": 2
			}],
			"ship_area": "北京市 北京市 海淀区",
			"customer_message": "bill的订单备注"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付"
		}
		"""
	Then jobs能获取订单
		"""
		{
			"customer_message": "bill的订单备注"
		}
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 2
			}],
			"ship_area": "北京市 北京市 海淀区"
		}
		"""
	Then jobs能获取订单
		"""
		{
			"customer_message": ""
		}
		"""

@mall3 @mall.webapp @zy_bp03 @robert.wip
Scenario:3 购买有规格的商品
	jobs添加商品后
	1. bill能在webapp中购买jobs添加的商品
	2. bill的订单中的信息正确

	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type":"微信支付",
			"products": [{
				"name": "商品3",
				"model": "黑色 M",
				"price": 10.0,
				"count": 2
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 20.0,
			"products": [{
				"name": "商品3",
				"model": "黑色 M",
				"price": 10.0,
				"count": 2
			}]
		}
		"""

@mall3 @mall.webapp @zy_bp04 @robert.wip
Scenario:4 购买已经下架的商品
	bill可能会在以下情景下购买已下架的商品A：
	1. bill打开商品A的详情页面
	2. bill点击“购买”，进入商品A的订单编辑页面
	3. jobs在后台将商品A下架
	4. bill点击“支付”，完成订单

	这时，系统应该通知bill：商品已下架

	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品4",
				"count": 1
			}]
		}
		"""
	Then bill获得错误提示'商品已下架<br/>2秒后返回商城首页'

@mall3 @mall.webapp @zy_bp05 @robert.wip
Scenario:5 购买的商品数量等于库存数量
	jobs添加有限商品后
	1. bill能在webapp中购买jobs添加的商品
	2. bill的订单中的信息正确
	3. jobs查看库存

	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"pay_type":"微信支付",
			"products": [{
				"name": "商品5",
				"count": 2
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 10.0,
			"products": [{
				"name": "商品5",
				"price": 5.0,
				"count": 2
			}]
		}
		"""
	Given jobs登录系统:weapp
	Then jobs能获取商品'商品5':weapp
		"""
		{
			"name": "商品5",
			"model": {
				"models": {
					"standard": {
						"price": 5.0,
						"stock_type": "有限",
						"stocks": 0
					}
				}
			}
		}
		"""

@mall3 @mall.webapp @zy_bp06 @robert.wip
Scenario:6 购买库存不足的商品
	bill可能会在以下情景下购买库存不足的商品A：
	1. bill打开商品A的详情页面
	2. bill调整数量为3个点击“购买”，进入商品A的订单编辑页面
	3. jobs在后台将商品A的库存调整为2个
	4. bill点击“支付”，完成订单
	5. jobs查看库存

	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品5",
				"count": 3
			}]
		}
		"""
	Then bill获得错误提示'有商品库存不足，请重新下单'
	Given jobs登录系统:weapp
	Then jobs能获取商品'商品5':weapp
		"""
		{
			"name": "商品5",
			"model": {
				"models": {
					"standard": {
						"price": 5.0,
						"stock_type": "有限",
						"stocks": 2
					}
				}
			}
		}
		"""

@mall3 @mall.webapp @zy_bp07 @robert.wip
Scenario:7 货到付款的商品有两种支付方式
	bill购买jobs配有'货到付款'的商品时
	1.bill可以使用'在线支付'进行支付
	2.bill可以使用'微众卡支付'进行支付
	3.bill可以使用'货到付款'进行支付

	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 2
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "click",
			"context": [{
				"name": "商品1"
			}]
		}
		"""
	Then bill'能'使用支付方式'微众卡支付'进行支付
	Then bill'能'使用支付方式'货到付款'进行支付
	Then bill'能'使用支付方式'微信支付'进行支付

@mall3 @mall.webapp @zy_bp08 @robert.wip
Scenario:8 没有货到付款的商品只有一种支付方式
	bill购买jobs没有配'货到付款'的商品时
	1.bill可以使用'在线支付'进行支付
	2.bill可以使用'微众卡支付'进行支付
	3.bill不可以使用'货到付款'进行支付

	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品6",
			"count": 2
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "click",
			"context": [{
				"name": "商品6"
			}]
		}
		"""
	Then bill'能'使用支付方式'微信支付'进行支付
	Then bill'能'使用支付方式'微众卡支付'进行支付
	Then bill'不能'使用支付方式'货到付款'进行支付

@mall3 @mall.webapp @robert.wip
Scenario:9 购买多个商品配置不同的支付方式
	bill购买jobs多个商品时，分别配置不同的支付方式
	1.bill可以使用'在线支付'进行支付
	2.bill可以使用'在线支付'进行支付
	3.bill不可以使用'货到付款'进行支付

	When bill访问jobs的webapp
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品2",
			"count": 1
		}, {
			"name": "商品6",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"context": [{
				"name": "商品2"
			}, {
				"name": "商品6"
			}]
		}
		"""
	Then bill'能'使用支付方式'微信支付'进行支付
	Then bill'能'使用支付方式'微众卡支付'进行支付
	Then bill'不能'使用支付方式'货到付款'进行支付

#后续补充.雪静
@mall3 @mall.webapp @zy_bp09 @robert.wip
Scenario:10 购买库存为零的商品
	bill可能会在以下情景下购买库存不足的商品A：
	1. bill打开商品A的详情页面
	2. bill调整数量为2个点击“购买”，进入商品A的订单编辑页面
	3. bill点击“支付”，完成订单
	4. bill再次购买商品A
	5. jobs查看库存

	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"pay_type":"微信支付",
			"products": [{
				"name": "商品5",
				"count": 2
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 10.0,
			"products": [{
				"name": "商品5",
				"price": 5.0,
				"count": 2
			}]
		}
		"""
	#bill从新进入商品详情页
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品5",
				"count": 1
			}]
		}
		"""
	Then bill获得错误提示'商品已售罄'

@mall3 @allOrder @robert.wip
Scenario:11 会员购买商品后，获取订单列表
	bill成功创建订单多个订单后，获取订单列表

	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"pay_type":"微信支付",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	And bill购买jobs的商品
		"""
		{
			"pay_type":"微信支付",
			"products": [{
				"name": "商品1",
				"count": 2
			}]
		}
		"""
	And bill购买jobs的商品
		"""
		{
			"pay_type":"微信支付",
			"products": [{
				"name": "商品1",
				"count": 1
			}, {
				"name": "商品2",
				"count": 1
			}, {
				"name": "商品3",
				"model": "黑色 M",
				"count": 1
			}, {
				"name": "商品5",
				"count": 2
			}]
		}
		"""
	#备注：个人中心-全部订单列表页，最多显示三个商品，会显示这个订单商品的总数
	Then bill查看个人中心'全部'订单列表
		"""
		[{
			"status": "待支付",
			"pay_interface": "微信支付",
			"created_at": "今天",
			"products": [{
				"name": "商品1"
			}, {
				"name": "商品2"
			}, {
				"name": "商品3"
			}, {
				"name": "商品5"
			}],
			"counts": 5,
			"final_price": 38.7
		}, {
			"status": "待支付",
			"pay_interface": "微信支付",
			"created_at": "今天",
			"products": [{
				"name": "商品1"
			}],
			"counts": 2,
			"final_price": 19.8
		}, {
			"status": "待支付",
			"pay_interface": "微信支付",
			"created_at": "今天",
			"products": [{
				"name": "商品1"
			}],
			"counts": 1,
			"final_price": 9.9
		}]
		"""

#根据需求4985新增场景
@mall3 @mall.webapp @robert.wip
Scenario:12 会员购买的商品同时参加多个活动，然后下架商品
	bill购买商品时，jobs下架此商品，bill获得错误提示信息

	Given jobs登录系统:weapp
	When jobs创建限时抢购活动:weapp
		"""
		[{
			"name": "商品1限时抢购",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品1",
			"member_grade": "全部",
			"count_per_purchase": 2,
			"promotion_price": 9.00
		}, {
			"name": "商品2限时抢购",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品2",
			"member_grade": "全部",
			"count_per_purchase": 2,
			"promotion_price": 8.0
		}]
		"""
	Given jobs登录系统:weapp
	When jobs'下架'商品'商品1':weapp
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	Then bill获得'商品1'错误提示'商品已下架'
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品2",
			"count": 1
		}, {
			"name": "商品6",
			"count": 1
		}]
		"""

	Given jobs登录系统:weapp
	When jobs'下架'商品'商品2':weapp
	When bill访问jobs的webapp
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"context": [{
				"name": "商品2"
			}, {
				"name": "商品6"
			}]
		}
		"""
	And bill在购物车订单编辑中点击提交订单
		"""
		{
			"pay_type": "微信支付"
		}
		"""
	Then bill获得'商品2'错误提示'商品已下架'

@mall3 @mall.webapp @robert.wip
Scenario:13 会员购买的商品同时参加多个活动，然后删除商品
	bill购买商品时，jobs删除此商品，bill获得错误提示信息

	Given jobs登录系统:weapp
	When jobs创建限时抢购活动:weapp
		"""
		[{
			"name": "商品1限时抢购",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品1",
			"member_grade": "全部",
			"count_per_purchase": 2,
			"promotion_price": 9.00
		}, {
			"name": "商品2限时抢购",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品2",
			"member_grade": "全部",
			"count_per_purchase": 2,
			"promotion_price": 8.0
		}]
		"""
	When jobs'永久删除'商品'商品1':weapp
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""

	Then bill获得'商品1'错误提示'商品已删除'
	When bill访问jobs的webapp
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品2",
			"count": 1
		}, {
			"name": "商品6",
			"count": 1
		}]
		"""
	Given jobs登录系统:weapp
	When jobs'永久删除'商品'商品2':weapp
	When bill访问jobs的webapp
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"context": [{
				"name": "商品2"
			}, {
				"name": "商品6"
			}]
		}
		"""
	And bill在购物车订单编辑中点击提交订单
		"""
		{
			"pay_type": "微信支付"
		}
		"""
	Then bill获得'商品2'错误提示'商品已删除'

# __author__ :王丽 2016-02-22
@mall3 @mall.webapp @robert.wip
Scenario:14 会员购买的商品未支付，订单中选择的支付方式被停用，订单列表、订单详情，和订单支付的处理
	#会员购买的商品未支付，订单中选择的支付方式被停用，订单列表、订单详情可以正确浏览
	#会员购买的商品未支付，订单中选择的支付方式被停用，支付此订单时，跳转到支付方式列表

	#微信支付
		When bill访问jobs的webapp
		And bill购买jobs的商品
			"""
			{
				"order_id":"0001",
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付",
				"products": [{
					"name": "商品1",
					"count": 2
				}]
			}
			"""
		Then bill成功创建订单
			"""
			{
				"order_no":"0001",
				"status": "待支付",
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"final_price": 19.8,
				"products": [{
					"name": "商品1",
					"price": 9.9,
					"count": 2
				}]
			}
			"""

		Given jobs登录系统:weapp
		When jobs'停用'支付方式'微信支付':weapp

		When bill访问jobs的webapp
		And bill访问个人中心
		Then bill查看个人中心'待支付'订单列表
			"""
			[{
				"status": "待支付",
				"created_at": "今天",
				"products": [{
					"name": "商品1"
				}],
				"counts": 2,
				"final_price": 19.8,
				 "pay_info": {
					"is_active": false
				}
			}]
			"""
		Then bill查看个人中心'全部'订单列表
			"""
			[{
				"status": "待支付",
				"created_at": "今天",
				"products": [{
					"name": "商品1"
				}],
				"counts": 2,
				"final_price": 19.8,
				 "pay_info": {
					"is_active": false
				}
			}]
			"""

		When bill使用支付方式'货到付款'进行支付订单'0001'

		When bill访问个人中心
		Then bill查看个人中心'待发货'订单列表
			"""
			[{
				"status": "待发货",
				"created_at": "今天",
				"products": [{
					"name": "商品1"
				}],
				"counts": 2,
				"final_price": 19.8
			}]
			"""

	#支付宝
		When bill访问jobs的webapp
		And bill购买jobs的商品
			"""
			{
				"order_id":"0002",
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"支付宝",
				"products": [{
					"name": "商品1",
					"count": 2
				}]
			}
			"""
		Then bill成功创建订单
			"""
			{
				"order_no":"0002",
				"status": "待支付",
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"final_price": 19.8,
				"products": [{
					"name": "商品1",
					"price": 9.9,
					"count": 2
				}]
			}
			"""

		Given jobs登录系统:weapp
		When jobs'启用'支付方式'微信支付':weapp
		When jobs'停用'支付方式'支付宝':weapp

		When bill访问jobs的webapp
		And bill访问个人中心
		Then bill查看个人中心'待支付'订单列表
			"""
			[{
				"status": "待支付",
				"created_at": "今天",
				"products": [{
					"name": "商品1"
				}],
				"counts": 2,
				"final_price": 19.8,
				 "pay_info": {
					"is_active": false
				}
			}]
			"""
		Then bill查看个人中心'全部'订单列表
			"""
			[{
				"status": "待支付",
				"created_at": "今天",
				"products": [{
					"name": "商品1"
				}],
				"counts": 2,
				"final_price": 19.8,
				 "pay_info": {
					"is_active": false
				}
			},{
				"status": "待发货",
				"created_at": "今天",
				"products": [{
					"name": "商品1"
				}],
				"counts": 2,
				"final_price": 19.8
			}]
			"""

		When bill使用支付方式'货到付款'进行支付订单'0002'

		When bill访问个人中心
		Then bill查看个人中心'待发货'订单列表
			"""
			[{
				"status": "待发货",
				"created_at": "今天",
				"products": [{
					"name": "商品1"
				}],
				"counts": 2,
				"final_price": 19.8
			}, {
				"status": "待发货",
				"created_at": "今天",
				"products": [{
					"name": "商品1"
				}],
				"counts": 2,
				"final_price": 19.8
			}]
			"""

	#货到付款
		When 清空浏览器:weapp
		When bill访问jobs的webapp
		And bill购买jobs的商品
			"""
			{
				"order_id":"0003",
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"货到付款",
				"products": [{
					"name": "商品1",
					"count": 2
				}]
			}
			"""
		Then bill成功创建订单
			"""
			{
				"order_no":"0003",
				"status": "待发货",
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"final_price": 19.8,
				"products": [{
					"name": "商品1",
					"price": 9.9,
					"count": 2
				}]
			}
			"""

		Given jobs登录系统:weapp
		When jobs'启用'支付方式'支付宝':weapp
		When jobs'停用'支付方式'货到付款':weapp

		When bill访问jobs的webapp
		When bill访问个人中心
		Then bill查看个人中心'全部'订单列表
			"""
			[{
				"status": "待发货",
				"created_at": "今天",
				"products": [{
					"name": "商品1"
				}],
				"counts": 2,
				"final_price": 19.8
			},{
				"status": "待发货",
				"created_at": "今天",
				"products": [{
					"name": "商品1"
				}],
				"counts": 2,
				"final_price": 19.8
			},{
				"status": "待发货",
				"created_at": "今天",
				"products": [{
					"name": "商品1"
				}],
				"counts": 2,
				"final_price": 19.8
			}]
			"""

	#停用所有支付方式
		Given jobs登录系统:weapp
		When jobs'停用'支付方式'支付宝':weapp
		When jobs'停用'支付方式'微信支付':weapp
		When jobs'停用'支付方式'货到付款':weapp

		When bill访问jobs的webapp
		When bill访问个人中心
		Then bill查看个人中心'全部'订单列表
			"""
			[{
				"status": "待发货",
				"created_at": "今天",
				"products": [{
					"name": "商品1"
				}],
				"counts": 2,
				"final_price": 19.8
			},{
				"status": "待发货",
				"created_at": "今天",
				"products": [{
					"name": "商品1"
				}],
				"counts": 2,
				"final_price": 19.8
			},{
				"status": "待发货",
				"created_at": "今天",
				"products": [{
					"name": "商品1"
				}],
				"counts": 2,
				"final_price": 19.8
			}]
			"""

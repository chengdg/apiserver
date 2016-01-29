#_author_:张三香 2016.01.25

Feature:购买参与买赠活动的商品,下单失败后校验赠品的库存
"""
	1.两个买赠活动选择同一个商品作为赠品时，赠品库存不足够时：
		前提条件:买A赠B（买一赠二-1个A，2个B）；买C赠B(买一赠三-1个C，3个B)
		只有1个B时：
			加入购车商品顺序-A+C
				编辑订单页:库存不足；库存不足
				弹窗提示：库存不足；库存不足
				订单详情页：1个赠品给了商品A
			加入购车商品顺序-C+A
				编辑订单页:库存不足；库存不足
				弹窗提示:库存不足；库存不足
				订单详情页:1个赠品给了商品A ？？？这里需要确定下逻辑是否要修改
		只有2个B时：
			A+C,（点击【提交订单】后扣2个库存，继续提交后订单中不显示赠品；取消订单后赠品的库存不对）
				编辑订单页:库存不足；库存不足
				弹窗提示：不提示；已赠完
				订单详情页：赠品数均显示0
			C+A,（点击【提交订单】后扣2个库存，继续提交后订单中不显示赠品；取消订单后赠品的库存不对）
				编辑订单页:库存不足；库存不足
				弹窗提示：不提示；已赠完
				订单详情页：赠品数均显示0
		只有3个B时
			A+C,（点击【提交订单】后扣2个库存，继续提交后订单中不显示赠品；取消订单后赠品的库存不对）
				编辑订单页:库存不足；库存不足
				弹窗提示：不提示；库存不足
				订单详情页：1个赠品给了商品A
			C+A,（点击【提交订单】后扣2个库存，继续提交后订单中不显示赠品；取消订单后赠品的库存不对）
			（C-不提示；A-提示'已赠完'）
				编辑订单页:库存不足；库存不足
				弹窗提示：不提示；库存不足
				订单详情页：1个赠品给了商品A

	2.商品既是主商品，又是两个买赠活动的赠品，商品库存不足够时:
		前提条件:买A赠A（买一赠一-1个A，1个A）;买B赠A(买一赠一-1个B，1个A)

		只有1个A时
			A+B:（'已赠完' '已赠完'）-无问题
			B+A:（'库存不足' '库存不足'）-无问题(已赠完 已赠完) 线上逻辑是这样的，需确认？
		只有2个A时
			A+B（有问题，点击提交订单扣1个库存，取消订单后，库存为1）

			B+A（存在问题，点击【提交订单】后扣除了1个A的库存）


	3.两个买赠活动，其中一个活动的赠品不足或已赠完，会导致另一个活动的库存减少
		买A赠B(买1赠2,当B的库存为0时，当B的库存为1时)
		买C赠D（买1赠2，当D的库存为2时；当D的库存为3时）
		当B的库存不足或已赠完时，点击【提交订单】会扣除赠品D的库存
"""
Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
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
	And bill关注jobs的公众号

#第1种情况
@promotion @premium_sale
Scenario:1 两个买赠活动选择同一个商品作为赠品,购买A和C,赠品均提示'库存不足'
	#买A赠B（买一赠二）
	#买C赠B(买一赠三)
	#B的库存为1，加入购物车商品A+C
	Given jobs登录系统:weapp
	Given jobs已添加商品:weapp
		"""
		[{
			"name": "赠品B",
			"model": {
				"models": {
					"standard": {
						"user_code": "1",
						"price": 10.0,
						"stock_type": "有限",
						"stocks": 1
					}
				}
			}
		},{
			"name":"商品A",
			"price":100.0
		},{
			"name":"商品C",
			"price":100.0
		}]
		"""
	When jobs创建买赠活动:weapp
		"""
		[{
			"name": "商品A买一赠二",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品A",
			"premium_products": [{
				"name": "赠品B",
				"count": 2
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}, {
			"name": "商品C买一赠三",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品C",
			"premium_products": [{
				"name": "赠品B",
				"count": 3
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	#赠品B库存为1时,商品A+商品C
	When bill访问jobs的webapp
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品A",
			"count": 1
		},{
			"name": "商品C",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "click",
			"context": [{
				"name": "商品A"
			},{
				"name": "商品C"
			}]
		}
		"""

	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款"
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
			"detail": [{
				"id": "赠品B",
				"msg": "库存不足",
				"short_msg": "库存不足"
			},{
				"id": "赠品B",
				"msg": "库存不足",
				"short_msg": "库存不足"
			}]
		}
		"""

	Given jobs登录系统:weapp
	Then jobs能获取商品'赠品B'
		"""
		{
			"name": "赠品B",
			"status": "在售",
			"model": {
				"models": {
					"standard": {
						"stock_type": "有限",
						"stocks": 1,
						"price": 10.0
					}
				}
			}
		}
		"""

@mall3 @promotion @premium_sale @ztq
Scenario:2 两个买赠活动选择同一个商品作为赠品,购买C和A,赠品均提示'库存不足'
	#买A赠B（买一赠二）
	#买C赠B(买一赠三)
	#B的库存为1，加入购物车商品C+A
	Given jobs登录系统:weapp
	Given jobs已添加商品:weapp
		"""
		[{
			"name": "赠品B",
			"model": {
				"models": {
					"standard": {
						"user_code": "1",
						"price": 10.0,
						"stock_type": "有限",
						"stocks": 1
					}
				}
			}
		},{
			"name":"商品A",
			"price":100.0
		},{
			"name":"商品C",
			"price":100.0
		}]
		"""
	When jobs创建买赠活动:weapp
		"""
		[{
			"name": "商品A买一赠二",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品A",
			"premium_products": [{
				"name": "赠品B",
				"count": 2
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}, {
			"name": "商品C买一赠三",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品C",
			"premium_products": [{
				"name": "赠品B",
				"count": 3
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	#赠品B库存为1时,商品C+商品A
	When bill访问jobs的webapp
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品C",
			"count": 1
		},{
			"name": "商品A",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "click",
			"context": [{
				"name": "商品C"
			},{
				"name": "商品A"
			}]
		}
		"""

	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款"
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
			"detail": [{
				"id": "赠品B",
				"msg": "库存不足",
				"short_msg": "库存不足"
			},{
				"id": "赠品B",
				"msg": "库存不足",
				"short_msg": "库存不足"
			}]
		}
		"""

	Given jobs登录系统:weapp
	Then jobs能获取商品'赠品B'
		"""
		{
			"name": "赠品B",
			"status": "在售",
			"model": {
				"models": {
					"standard": {
						"stock_type": "有限",
						"stocks": 1,
						"price": 10.0
					}
				}
			}
		}
		"""

@promotion @premium_sale
Scenario:3 两个买赠活动选择同一个商品作为赠品,购买A和C,赠品一个不提示和一个提示'已赠完'
	#买A赠B（买一赠二）
	#买C赠B(买一赠三)
	#B的库存为2，加入购物车商品A+C
	Given jobs登录系统:weapp
	Given jobs已添加商品:weapp
		"""
		[{
			"name": "赠品B",
			"model": {
				"models": {
					"standard": {
						"user_code": "1",
						"price": 10.0,
						"stock_type": "有限",
						"stocks": 2
					}
				}
			}
		},{
			"name":"商品A",
			"price":100.0
		},{
			"name":"商品C",
			"price":100.0
		}]
		"""
	When jobs创建买赠活动:weapp
		"""
		[{
			"name": "商品A买一赠二",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品A",
			"premium_products": [{
				"name": "赠品B",
				"count": 2
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}, {
			"name": "商品C买一赠三",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品C",
			"premium_products": [{
				"name": "赠品B",
				"count": 3
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	#赠品B库存为2时,商品A+商品C
	When bill访问jobs的webapp
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品A",
			"count": 1
		},{
			"name": "商品C",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "click",
			"context": [{
				"name": "商品A"
			},{
				"name": "商品C"
			}]
		}
		"""

	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款"
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
				"detail": [{
				"id": "赠品B",
				"msg": "已赠完",
				"short_msg": "已赠完"
			}]
		}
		"""

	Given jobs登录系统:weapp
	Then jobs能获取商品'赠品B'
		"""
		{
			"name": "赠品B",
			"status": "在售",
			"model": {
				"models": {
					"standard": {
						"stock_type": "有限",
						"stocks": 2,
						"price": 10.0
					}
				}
			}
		}
		"""

@promotion @premium_sale
Scenario:4 两个买赠活动选择同一个商品作为赠品,购买C和A,赠品一个提示'库存不足'和一个提示'已赠完'
	#买A赠B（买一赠二）
	#买C赠B(买一赠三)
	#B的库存为2，加入购物车商品C+A
	Given jobs登录系统:weapp
	Given jobs已添加商品:weapp
		"""
		[{
			"name": "赠品B",
			"model": {
				"models": {
					"standard": {
						"user_code": "1",
						"price": 10.0,
						"stock_type": "有限",
						"stocks": 2
					}
				}
			}
		},{
			"name":"商品A",
			"price":100.0
		},{
			"name":"商品C",
			"price":100.0
		}]
		"""
	When jobs创建买赠活动:weapp
		"""
		[{
			"name": "商品A买一赠二",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品A",
			"premium_products": [{
				"name": "赠品B",
				"count": 2
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}, {
			"name": "商品C买一赠三",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品C",
			"premium_products": [{
				"name": "赠品B",
				"count": 3
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	#赠品B库存为2时,商品C+商品A
	When bill访问jobs的webapp
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品C",
			"count": 1
		},{
			"name": "商品A",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "click",
			"context": [{
				"name": "商品C"
			},{
				"name": "商品A"
			}]
		}
		"""

	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款"
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
			"detail":
			[{
				"id": "赠品B",
				"msg": "库存不足",
				"short_msg": "库存不足"
			}]
		}
		"""

	Given jobs登录系统:weapp
	Then jobs能获取商品'赠品B'
		"""
		{
			"name": "赠品B",
			"status": "在售",
			"model": {
				"models": {
					"standard": {
						"stock_type": "有限",
						"stocks": 2,
						"price": 10.0
					}
				}
			}
		}
		"""

@promotion @premium_sale
Scenario:5 两个买赠活动选择同一个商品作为赠品,购买A和C,赠品一个不提示和一个提示'库存不足'
	#买A赠B（买一赠二）
	#买C赠B(买一赠三)
	#B的库存为3，加入购物车商品A+C
	Given jobs登录系统:weapp
	Given jobs已添加商品:weapp
		"""
		[{
			"name": "赠品B",
			"model": {
				"models": {
					"standard": {
						"user_code": "1",
						"price": 10.0,
						"stock_type": "有限",
						"stocks": 3
					}
				}
			}
		},{
			"name":"商品A",
			"price":100.0
		},{
			"name":"商品C",
			"price":100.0
		}]
		"""
	When jobs创建买赠活动:weapp
		"""
		[{
			"name": "商品A买一赠二",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品A",
			"premium_products": [{
				"name": "赠品B",
				"count": 2
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}, {
			"name": "商品C买一赠三",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品C",
			"premium_products": [{
				"name": "赠品B",
				"count": 3
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	#赠品B库存为3时,商品A+商品C
	When bill访问jobs的webapp
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品A",
			"count": 1
		},{
			"name": "商品C",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "click",
			"context": [{
				"name": "商品A"
			},{
				"name": "商品C"
			}]
		}
		"""

	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款"
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
				"detail": [{
				"id": "赠品B",
				"msg": "库存不足",
				"short_msg": "库存不足"
			}]
		}
		"""

	Given jobs登录系统:weapp
	Then jobs能获取商品'赠品B'
		"""
		{
			"name": "赠品B",
			"status": "在售",
			"model": {
				"models": {
					"standard": {
						"stock_type": "有限",
						"stocks": 3,
						"price": 10.0
					}
				}
			}
		}
		"""

@promotion @premium_sale
Scenario:6 两个买赠活动选择同一个商品作为赠品,购买C和A,赠品一个不提示和一个提示'已赠完'
	#买A赠B（买一赠二）
	#买C赠B(买一赠三)
	#B的库存为3，加入购物车商品C+A
	Given jobs登录系统:weapp
	Given jobs已添加商品:weapp
		"""
		[{
			"name": "赠品B",
			"model": {
				"models": {
					"standard": {
						"user_code": "1",
						"price": 10.0,
						"stock_type": "有限",
						"stocks": 3
					}
				}
			}
		},{
			"name":"商品A",
			"price":100.0
		},{
			"name":"商品C",
			"price":100.0
		}]
		"""
	When jobs创建买赠活动:weapp
		"""
		[{
			"name": "商品A买一赠二",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品A",
			"premium_products": [{
				"name": "赠品B",
				"count": 2
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}, {
			"name": "商品C买一赠三",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品C",
			"premium_products": [{
				"name": "赠品B",
				"count": 3
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	#赠品B库存为3时,商品A+商品C
	When bill访问jobs的webapp
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品C",
			"count": 1
		},{
			"name": "商品A",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "click",
			"context": [{
				"name": "商品C"
			},{
				"name": "商品A"
			}]
		}
		"""

	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款"
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
				"detail": [{
				"id": "赠品B",
				"msg": "已赠完",
				"short_msg": "已赠完"
			}]
		}
		"""

	Given jobs登录系统:weapp
	Then jobs能获取商品'赠品B'
		"""
		{
			"name": "赠品B",
			"status": "在售",
			"model": {
				"models": {
					"standard": {
						"stock_type": "有限",
						"stocks": 3,
						"price": 10.0
					}
				}
			}
		}
		"""

#第2种情况
@promotion @premium_sale
Scenario:7 两个买赠活动选择同一商品作为赠品,购买A和B,赠品同时也是主商品,赠品均提示'已赠完'
	#买A赠A（买一赠一）;
	#买B赠A(买一赠一)
	#A的库存为1时，A+B
	Given jobs登录系统:weapp
	Given jobs已添加商品:weapp
		"""
		[{
			"name": "商品A",
			"model": {
				"models": {
					"standard": {
						"user_code": "1",
						"price": 100.0,
						"stock_type": "有限",
						"stocks": 1
					}
				}
			}
		},{
			"name":"商品B",
			"price":100.0
		}]
		"""
	When jobs创建买赠活动:weapp
		"""
		[{
			"name": "商品A买一赠一",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品A",
			"premium_products": [{
				"name": "商品A",
				"count": 1
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}, {
			"name": "商品B买一赠一",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品B",
			"premium_products": [{
				"name": "商品A",
				"count": 1
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	#商品A库存只有1个时，商品A+商品B
	When bill访问jobs的webapp
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品A",
			"count": 1
		},{
			"name": "商品B",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "click",
			"context": [{
				"name": "商品A"
			},{
				"name": "商品B"
			}]
		}
		"""

	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款"
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
			"detail":
			[{
				"id": "商品A",
				"msg": "已赠完",
				"short_msg": "已赠完"
			},{
				"id": "商品A",
				"msg": "已赠完",
				"short_msg": "已赠完"
			}]
		}
		"""

	Given jobs登录系统:weapp
	Then jobs能获取商品'商品A'
		"""
		{
			"name": "商品A",
			"status": "在售",
			"model": {
				"models": {
					"standard": {
						"stock_type": "有限",
						"stocks": 1,
						"price": 100.0
					}
				}
			}
		}
		"""

@promotion @premium_sale
Scenario:8 两个买赠活动选择同一商品作为赠品,购买A和B,赠品同时也是主商品,赠品均提示'已赠完'
	#买A赠A（买一赠一）;
	#买B赠A(买一赠一)
	#A的库存为1时，B+A（邮箱分配主商品，其次按照商品顺序分配赠品）
	Given jobs登录系统:weapp
	Given jobs已添加商品:weapp
		"""
		[{
			"name": "商品A",
			"model": {
				"models": {
					"standard": {
						"user_code": "1",
						"price": 100.0,
						"stock_type": "有限",
						"stocks": 1
					}
				}
			}
		},{
			"name":"商品B",
			"price":100.0
		}]
		"""
	When jobs创建买赠活动:weapp
		"""
		[{
			"name": "商品A买一赠一",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品A",
			"premium_products": [{
				"name": "商品A",
				"count": 1
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}, {
			"name": "商品B买一赠一",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品B",
			"premium_products": [{
				"name": "商品A",
				"count": 1
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	#商品A库存只有1个时，商品B+商品A
	When bill访问jobs的webapp
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品B",
			"count": 1
		},{
			"name": "商品A",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "click",
			"context": [{
				"name": "商品B"
			},{
				"name": "商品A"
			}]
		}
		"""

	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款"
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
			"detail":
			[{
				"id": "商品A",
				"msg": "已赠完",
				"short_msg": "已赠完"
			},{
				"id": "商品A",
				"msg": "已赠完",
				"short_msg": "已赠完"
			}]
		}
		"""

	Given jobs登录系统:weapp
	Then jobs能获取商品'商品A'
		"""
		{
			"name": "商品A",
			"status": "在售",
			"model": {
				"models": {
					"standard": {
						"stock_type": "有限",
						"stocks": 1,
						"price": 100.0
					}
				}
			}
		}
		"""

@promotion @premium_sale
Scenario:9 两个买赠活动选择同一商品作为赠品,购买A和B,赠品同时也是主商品
	#买A赠A（买一赠一）;
	#买B赠A(买一赠一)
	#A的库存为2时，A+B
	Given jobs登录系统:weapp
	Given jobs已添加商品:weapp
		"""
		[{
			"name": "商品A",
			"model": {
				"models": {
					"standard": {
						"user_code": "1",
						"price": 100.0,
						"stock_type": "有限",
						"stocks": 2
					}
				}
			}
		},{
			"name":"商品B",
			"price":100.0
		}]
		"""
	When jobs创建买赠活动:weapp
		"""
		[{
			"name": "商品A买一赠一",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品A",
			"premium_products": [{
				"name": "商品A",
				"count": 1
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}, {
			"name": "商品B买一赠一",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品B",
			"premium_products": [{
				"name": "商品A",
				"count": 1
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	#商品A库存只有2个时，商品A+商品B
	When bill访问jobs的webapp
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品A",
			"count": 1
		},{
			"name": "商品B",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "click",
			"context": [{
				"name": "商品A"
			},{
				"name": "商品B"
			}]
		}
		"""

	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款"
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
				"detail": [{
				"id": "商品A",
				"msg": "已赠完",
				"short_msg": "已赠完"
			}]
		}
		"""

	Given jobs登录系统:weapp
	Then jobs能获取商品'商品A'
		"""
		{
			"name": "商品A",
			"status": "在售",
			"model": {
				"models": {
					"standard": {
						"stock_type": "有限",
						"stocks": 2,
						"price": 100.0
					}
				}
			}
		}
		"""

@promotion @premium_sale
Scenario:10 两个买赠活动选择同一商品作为赠品,购买B和A,赠品同时也是主商品
	#买A赠A（买一赠一）;
	#买B赠A(买一赠一)
	#A的库存为2时，B+A
	Given jobs登录系统:weapp
	Given jobs已添加商品:weapp
		"""
		[{
			"name": "商品A",
			"model": {
				"models": {
					"standard": {
						"user_code": "1",
						"price": 100.0,
						"stock_type": "有限",
						"stocks": 2
					}
				}
			}
		},{
			"name":"商品B",
			"price":100.0
		}]
		"""
	When jobs创建买赠活动:weapp
		"""
		[{
			"name": "商品A买一赠一",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品A",
			"premium_products": [{
				"name": "商品A",
				"count": 1
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}, {
			"name": "商品B买一赠一",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品B",
			"premium_products": [{
				"name": "商品A",
				"count": 1
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	#商品A库存只有2个时，商品B+商品A
	When bill访问jobs的webapp
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品B",
			"count": 1
		},{
			"name": "商品A",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "click",
			"context": [{
				"name": "商品B"
			},{
				"name": "商品A"
			}]
		}
		"""

	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款"
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
				"detail": [{
				"id": "商品A",
				"msg": "已赠完",
				"short_msg": "已赠完"
			}]
		}
		"""

	Given jobs登录系统:weapp
	Then jobs能获取商品'商品A'
		"""
		{
			"name": "商品A",
			"status": "在售",
			"model": {
				"models": {
					"standard": {
						"stock_type": "有限",
						"stocks": 2,
						"price": 100.0
					}
				}
			}
		}
		"""

#第3种情况
@promotion @premium_sale
Scenario:11 B的库存为0,D的库存正好满足买赠活动
	#买A赠B(买1赠2,当B的库存为0时)
	#买C赠D（买1赠2，当D的库存为2时）
	Given jobs登录系统:weapp
	Given jobs已添加商品:weapp
		"""
		[{
			"name": "商品A",
			"price":100.0
		},{
			"name":"赠品B",
			"model": {
				"models": {
					"standard": {
						"user_code": "1",
						"price": 10.0,
						"stock_type": "有限",
						"stocks": 0
					}
				}
			}
		},{
			"name":"商品C",
			"price":100.0
		},{
			"name": "赠品D",
			"model": {
				"models": {
					"standard": {
						"user_code": "1",
						"price": 10.0,
						"stock_type": "有限",
						"stocks": 2
					}
				}
			}
		}]
		"""
	When jobs创建买赠活动:weapp
		"""
		[{
			"name": "商品A赠B",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品A",
			"premium_products": [{
				"name": "赠品B",
				"count": 2
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}, {
			"name": "商品C赠D",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品C",
			"premium_products": [{
				"name": "赠品D",
				"count": 2
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	When bill访问jobs的webapp
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品A",
			"count": 1
		},{
			"name": "商品C",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "click",
			"context": [{
				"name": "商品A"
			},{
				"name": "商品C"
			}]
		}
		"""

	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款"
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
				"detail": [{
				"id": "赠品B",
				"msg": "已赠完",
				"short_msg": "已赠完"
			}]
		}
		"""

	Given jobs登录系统:weapp
	Then jobs能获取商品'赠品D'
		"""
		{
			"name": "赠品D",
			"status": "在售",
			"model": {
				"models": {
					"standard": {
						"stock_type": "有限",
						"stocks": 2,
						"price": 10.0
					}
				}
			}
		}
		"""

@promotion @premium_sale
Scenario:12 B的为0,D的库存多余满足买赠活动
	#买A赠B(买1赠2,当B的库存为0时)
	#买C赠D（买1赠2，当D的库存为3时）
	Given jobs登录系统:weapp
	Given jobs已添加商品:weapp
		"""
		[{
			"name": "商品A",
			"price":100.0
		},{
			"name":"赠品B",
			"model": {
				"models": {
					"standard": {
						"user_code": "1",
						"price": 10.0,
						"stock_type": "有限",
						"stocks": 0
					}
				}
			}
		},{
			"name":"商品C",
			"price":100.0
		},{
			"name": "赠品D",
			"model": {
				"models": {
					"standard": {
						"user_code": "1",
						"price": 10.0,
						"stock_type": "有限",
						"stocks": 3
					}
				}
			}
		}]
		"""
	When jobs创建买赠活动:weapp
		"""
		[{
			"name": "商品A赠B",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品A",
			"premium_products": [{
				"name": "赠品B",
				"count": 2
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}, {
			"name": "商品C赠D",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品C",
			"premium_products": [{
				"name": "赠品D",
				"count": 2
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	When bill访问jobs的webapp
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品A",
			"count": 1
		},{
			"name": "商品C",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "click",
			"context": [{
				"name": "商品A"
			},{
				"name": "商品C"
			}]
		}
		"""

	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款"
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
				"detail": [{
				"id": "赠品B",
				"msg": "已赠完",
				"short_msg": "已赠完"
			}]
		}
		"""

	Given jobs登录系统:weapp
	Then jobs能获取商品'赠品D'
		"""
		{
			"name": "赠品D",
			"status": "在售",
			"model": {
				"models": {
					"standard": {
						"stock_type": "有限",
						"stocks": 3,
						"price": 10.0
					}
				}
			}
		}
		"""

@promotion @premium_sale
Scenario:13 B的库存不足,D的库存正好满足买赠活动
	#买A赠B(买1赠2,当B的库存为1时)
	#买C赠D（买1赠2，当D的库存为2时）
	Given jobs登录系统:weapp
	Given jobs已添加商品:weapp
		"""
		[{
			"name": "商品A",
			"price":100.0
		},{
			"name":"赠品B",
			"model": {
				"models": {
					"standard": {
						"user_code": "1",
						"price": 10.0,
						"stock_type": "有限",
						"stocks": 1
					}
				}
			}
		},{
			"name":"商品C",
			"price":100.0
		},{
			"name": "赠品D",
			"model": {
				"models": {
					"standard": {
						"user_code": "1",
						"price": 10.0,
						"stock_type": "有限",
						"stocks": 2
					}
				}
			}
		}]
		"""
	When jobs创建买赠活动:weapp
		"""
		[{
			"name": "商品A赠B",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品A",
			"premium_products": [{
				"name": "赠品B",
				"count": 2
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}, {
			"name": "商品C赠D",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品C",
			"premium_products": [{
				"name": "赠品D",
				"count": 2
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	When bill访问jobs的webapp
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品A",
			"count": 1
		},{
			"name": "商品C",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "click",
			"context": [{
				"name": "商品A"
			},{
				"name": "商品C"
			}]
		}
		"""

	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款"
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
				"detail": [{
				"id": "赠品B",
				"msg": "库存不足",
				"short_msg": "库存不足"
			}]
		}
		"""

	Given jobs登录系统:weapp
	Then jobs能获取商品'赠品B'
		"""
		{
			"name": "赠品B",
			"status": "在售",
			"model": {
				"models": {
					"standard": {
						"stock_type": "有限",
						"stocks": 1,
						"price": 10.0
					}
				}
			}
		}
		"""
	Then jobs能获取商品'赠品D'
		"""
		{
			"name": "赠品D",
			"status": "在售",
			"model": {
				"models": {
					"standard": {
						"stock_type": "有限",
						"stocks": 2,
						"price": 10.0
					}
				}
			}
		}
		"""

@promotion @premium_sale
Scenario:14 B的库存不足,D的库存多余满足买赠活动
	#买A赠B(买1赠2,当B的库存为1时)
	#买C赠D（买1赠2，当D的库存为3时）
	Given jobs登录系统:weapp
	Given jobs已添加商品:weapp
		"""
		[{
			"name": "商品A",
			"price":100.0
		},{
			"name":"赠品B",
			"model": {
				"models": {
					"standard": {
						"user_code": "1",
						"price": 10.0,
						"stock_type": "有限",
						"stocks": 1
					}
				}
			}
		},{
			"name":"商品C",
			"price":100.0
		},{
			"name": "赠品D",
			"model": {
				"models": {
					"standard": {
						"user_code": "1",
						"price": 10.0,
						"stock_type": "有限",
						"stocks": 3
					}
				}
			}
		}]
		"""
	When jobs创建买赠活动:weapp
		"""
		[{
			"name": "商品A赠B",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品A",
			"premium_products": [{
				"name": "赠品B",
				"count": 2
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}, {
			"name": "商品C赠D",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品C",
			"premium_products": [{
				"name": "赠品D",
				"count": 2
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	When bill访问jobs的webapp
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品A",
			"count": 1
		},{
			"name": "商品C",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "click",
			"context": [{
				"name": "商品A"
			},{
				"name": "商品C"
			}]
		}
		"""

	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "货到付款"
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
				"detail": [{
				"id": "赠品B",
				"msg": "库存不足",
				"short_msg": "库存不足"
			}]
		}
		"""

	Given jobs登录系统:weapp
	Then jobs能获取商品'赠品B'
		"""
		{
			"name": "赠品B",
			"status": "在售",
			"model": {
				"models": {
					"standard": {
						"stock_type": "有限",
						"stocks": 1,
						"price": 10.0
					}
				}
			}
		}
		"""
	Then jobs能获取商品'赠品D'
		"""
		{
			"name": "赠品D",
			"status": "在售",
			"model": {
				"models": {
					"standard": {
						"stock_type": "有限",
						"stocks": 3,
						"price": 10.0
					}
				}
			}
		}
		"""
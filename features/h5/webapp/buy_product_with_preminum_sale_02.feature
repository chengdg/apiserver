#_author_:张三香 2016.01.25
#_editor_:朱天琦 2016.01.29

Feature:购买参与买赠活动的商品,下单失败后校验赠品的库存
"""
	注：
		a.编辑订单页提示规则：均显示'库存不足'

		b.'以下赠品库存不足或已赠完！'弹框提示规则：按照商品分配原则提示

		c.商品分配原则：优先满足主商品，强制提交订单后按照订单中主商品的顺序来分配赠品

	特殊的三种情况：
	1.两个买赠活动选择同一个商品作为赠品时，赠品库存不足够时：
		前提条件:买A赠B（买一赠二-1个A，2个B）；买C赠B(买一赠三-1个C，3个B)
		只有1个B时：
			A+C
				编辑订单页:库存不足；库存不足
				弹窗提示：库存不足；库存不足
				订单详情页：1个赠品给了商品A
			C+A
				编辑订单页:库存不足；库存不足
				弹窗提示:库存不足；库存不足
				订单详情页:1个赠品按照订单中商品的顺序分配，给商品C
		只有2个B时：
			A+C,
				编辑订单页:A-库存不足；C-库存不足
				弹窗提示：A-不提示；C-已赠完
				订单详情页：A-2个赠品；C-0个赠品
			C+A,
				编辑订单页:C-库存不足；A-库存不足
				弹窗提示：C-库存不足；A-已赠完
				订单详情页：C-2个赠品；A-0个赠品
		只有3个B时
			A+C,
				编辑订单页:A-库存不足；C-库存不足
				弹窗提示：A-不提示；C-库存不足
				订单详情页：A-2个赠品；C-1个赠品
			C+A,
				编辑订单页:C-库存不足；A-库存不足
				弹窗提示：C-不提示；A-已赠完
				订单详情页：C-3个赠品；A-0个赠品

	2.商品既是主商品，又是两个买赠活动的赠品，商品库存不足够时:
		前提条件:买A赠A（买一赠一-1个A，1个A）;买B赠A(买一赠一-1个B，1个A)

		只有1个A时
			A+B:
				编辑订单页:A-库存不足；B-库存不足
				弹窗提示：A-已赠完；B-已赠完
				订单详情页：A-0个赠品；B-0个赠品
			B+A:（'已赠完' '已赠完'）-优先分配主商品
				编辑订单页:B-库存不足；A-库存不足
				弹窗提示：B-已赠完；A-已赠完
				订单详情页：B-0个赠品；A-0个赠品
		只有2个A时
			A+B
				编辑订单页:A-库存不足；B-库存不足
				弹窗提示：A-不提示；B-已赠完
				订单详情页：A-1个赠品；B-0个赠品
			B+A
				编辑订单页:B-库存不足；A-库存不足
				弹窗提示：B-不提示；A-已赠完
				订单详情页：B-1个赠品；A-0个赠品

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
@mall3 @promotion @premium_sale @ztq
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

@mall3 @promotion @premium_sale @ztq
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

@mall3 @promotion @premium_sale @ztq
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

@mall3 @promotion @premium_sale @ztq
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

@mall3 @promotion @premium_sale @ztq
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
@mall3 @promotion @premium_sale @ztq
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

@mall3 @promotion @premium_sale @ztq
Scenario:8 两个买赠活动选择同一商品作为赠品,购买A和B,赠品同时也是主商品,赠品均提示'已赠完'
	#买A赠A（买一赠一）;
	#买B赠A(买一赠一)
	#A的库存为1时，B+A（优先分配主商品，其次按照商品顺序分配赠品）
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

@mall3 @promotion @premium_sale @ztq
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

@mall3 @promotion @premium_sale @ztq
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
@mall3 @promotion @premium_sale @ztq
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

@mall3 @promotion @premium_sale @ztq
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

@mall3 @promotion @premium_sale @ztq
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

@mall3 @promotion @premium_sale @ztq
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
# watcher: fengxuejing@weizoom.com,wangli@weizoom.com,benchi@weizoom.com
# __author__ : "冯雪静"
#editor:王丽 2015.10.13
#editor:王丽 2015.12.29

Feature:商品销量
"""
	Jobs能通过管理系统为管理商城"商品销量"

	1.成功支付订单后，商品销量增加
	2.订单为待支付状态时，商品销量不变
	3.成功支付订单后，取消订单，商品销量不变
	4.购买买赠商品成功支付订单后，取消订单，商品销量不变

"""

Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
	And jobs已添加商品:weapp
		"""
		[{
			"name": "商品1",
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"stock_type": "有限",
						"stocks": 10
					}
				}
			}
		},{
			"name": "商品2",
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"stock_type": "有限",
						"stocks": 10
					}
				}
			}
		}]
		"""
	And jobs已添加支付方式:weapp
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

@mall3 @product @saleingProduct @ztq
Scenario: 1 成功支付订单后，商品销量增加
	bill购买商品支付成功后，jobs的商品销量增加
	1.商品库存减少

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
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1
			}]
		}
		"""
	When bill使用支付方式'货到付款'进行支付
	Then bill支付订单成功
		"""
		{
			"status": "待发货",
			"final_price": 100.00,
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1
			}]
		}
		"""
	Given jobs登录系统:weapp
	Then jobs能获取商品'商品1':weapp
		"""
		{
			"name": "商品1",
			"sales": 1,
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"stock_type": "有限",
						"stocks": 9
					}
				}
			}
		}
		"""

@mall3 @product @saleingProduct
Scenario: 2 订单为待支付状态时，商品销量不变
	bill成功创建订单待支付状态，jobs的商品销量不变
	1.商品库存减少

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
	Then bill成功创建订单
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
	Given jobs登录系统:weapp
	Then jobs能获取商品'商品1':weapp
		"""
		{
			"name": "商品1",
			"sales": 0,
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"stock_type": "有限",
						"stocks": 9
					}
				}
			}
		}
		"""

@mall3 @product @saleingProduct
Scenario: 3 购买买赠商品(赠品为主商品)成功支付订单后，主商品销量增加，赠品销量不变
	jobs创建买赠活动后
	1.bill成功下单后，主商品销量增加，赠品销量不变

	Given jobs登录系统:weapp
	#购买买赠商品，主商品和赠品都使用一个商品，赠品减库存，不增加销量
	When jobs创建买赠活动:weapp
		"""
		[{
			"name": "商品1买一赠二",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品1",
			"premium_products": [{
				"name": "商品1",
				"count": 2
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
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
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 100.00,
			"products": [{
				"name": "商品1",
				"count": 1,
				"promotion": {
					"type": "premium_sale"
				}
			}, {
				"name": "商品1",
				"count": 2,
				"promotion": {
					"type": "premium_sale:premium_product"
				}
			}]
		}
		"""
	When bill使用支付方式'货到付款'进行支付
	Then bill支付订单成功
		"""
		{
			"status": "待发货",
			"final_price": 100.00,
			"products": [{
				"name": "商品1",
				"count": 1,
				"promotion": {
					"type": "premium_sale"
				}
			},{
				"name": "商品1",
				"count": 2,
				"promotion": {
					"type": "premium_sale:premium_product"
				}
			}]
		}
		"""
	#买赠活动：赠品扣库存，但是不算销量
	Given jobs登录系统:weapp
	Then jobs能获取商品'商品1':weapp
		"""
		{
			"name": "商品1",
			"sales": 1,
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"stock_type": "有限",
						"stocks": 7
					}
				}
			}
		}
		"""

@mall3 @product @saleingProduct
Scenario: 4 购买买赠商品(赠品为非主商品)成功支付订单后，主商品销量增加，赠品销量不变
	jobs创建买赠活动后
	1.bill成功下单后，主商品销量增加，赠品销量不变

	Given jobs登录系统:weapp
	#购买买赠商品，主商品和赠品都使用一个商品，赠品减库存，不增加销量
	When jobs创建买赠活动:weapp
		"""
		[{
			"name": "商品1买一赠二",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品1",
			"premium_products": [{
				"name": "商品2",
				"count": 2
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
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
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 100.00,
			"products": [{
				"name": "商品1",
				"count": 1,
				"promotion": {
					"type": "premium_sale"
				}
			}, {
				"name": "商品2",
				"count": 2,
				"promotion": {
					"type": "premium_sale:premium_product"
				}
			}]
		}
		"""
	When bill使用支付方式'货到付款'进行支付
	Then bill支付订单成功
		"""
		{
			"status": "待发货",
			"final_price": 100.00,
			"products": [{
				"name": "商品1",
				"count": 1,
				"promotion": {
					"type": "premium_sale"
				}
			},{
				"name": "商品2",
				"count": 2,
				"promotion": {
					"type": "premium_sale:premium_product"
				}
			}]
		}
		"""
	#买赠活动：赠品扣库存，但是不算销量
	Given jobs登录系统:weapp
	Then jobs能获取商品'商品1':weapp
		"""
		{
			"name": "商品1",
			"sales": 1,
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"stock_type": "有限",
						"stocks": 9
					}
				}
			}
		}
		"""
	Then jobs能获取商品'商品2':weapp
		"""
		{
			"name": "商品2",
			"sales": 0,
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"stock_type": "有限",
						"stocks": 8
					}
				}
			}
		}
		"""
#editor:新新 2016.1.13
@mall3 @product @saleingProduct @ztq
Scenario: 5 购买买赠商品(赠品为非主商品)成功支付订单后，主商品有基础销量，赠品也有基础销量,基础上购买买赠商品销量和库存问题
	jobs创建买赠活动后
	1.bill成功下单后，主商品库存减少,销量增加;赠品库存减少,销量不变;
	Given jobs登录系统:weapp
	When jobs创建买赠活动:weapp
		"""
		[{
			"name": "商品1买一赠二",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品1",
			"premium_products": [{
				"name": "商品2",
				"count": 2
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	#bill第一次购买产生基础数据,库存和销量	
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
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 100.00,
			"products": [{
				"name": "商品1",
				"count": 1,
				"promotion": {
					"type": "premium_sale"
				}
			}, {
				"name": "商品2",
				"count": 2,
				"promotion": {
					"type": "premium_sale:premium_product"
				}
			}]
		}
		"""
	When bill使用支付方式'货到付款'进行支付
	Then bill支付订单成功
		"""
		{
			"status": "待发货",
			"final_price": 100.00,
			"products": [{
				"name": "商品1",
				"count": 1,
				"promotion": {
					"type": "premium_sale"
				}
			},{
				"name": "商品2",
				"count": 2,
				"promotion": {
					"type": "premium_sale:premium_product"
				}
			}]
		}
		"""
	#买赠活动：赠品扣库存，但是不算销量
	Given jobs登录系统:weapp
	Then jobs能获取商品'商品1':weapp
		"""
		{
			"name": "商品1",
			"sales": 1,
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"stock_type": "有限",
						"stocks": 9
					}
				}
			}
		}
		"""
	Then jobs能获取商品'商品2':weapp
		"""
		{
			"name": "商品2",
			"sales": 0,
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"stock_type": "有限",
						"stocks": 8
					}
				}
			}
		}
		"""
	#bill第二次购买
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
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 100.00,
			"products": [{
				"name": "商品1",
				"count": 1,
				"promotion": {
					"type": "premium_sale"
				}
			}, {
				"name": "商品2",
				"count": 2,
				"promotion": {
					"type": "premium_sale:premium_product"
				}
			}]
		}
		"""
	When bill使用支付方式'货到付款'进行支付
	Then bill支付订单成功
		"""
		{
			"status": "待发货",
			"final_price": 100.00,
			"products": [{
				"name": "商品1",
				"count": 1,
				"promotion": {
					"type": "premium_sale"
				}
			},{
				"name": "商品2",
				"count": 2,
				"promotion": {
					"type": "premium_sale:premium_product"
				}
			}]
		}
		"""
	#买赠活动：赠品扣库存，但是不算销量
	Given jobs登录系统:weapp
	Then jobs能获取商品'商品1':weapp
		"""
		{
			"name": "商品1",
			"sales": 2,
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"stock_type": "有限",
						"stocks": 8
					}
				}
			}
		}
		"""
	Then jobs能获取商品'商品2':weapp
		"""
		{
			"name": "商品2",
			"sales": 0,
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"stock_type": "有限",
						"stocks": 6
					}
				}
			}
		}
		"""




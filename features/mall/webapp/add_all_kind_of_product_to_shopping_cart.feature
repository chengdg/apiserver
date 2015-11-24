#author: benchi
#editor: 师帅 2015.10.19
@func:webapp.modules.mall.views.list_products

Feature: 添加普通商品，促销商品到购物车中
	bill能在webapp中将jobs添加的"普通商品，促销商品"放入购物车

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
	And jobs已添加商品
		"""
		[{
			"name": "商品1",
			"price": 100
		}, {
			"name": "商品2",
			"price": 200
		}, {
			"name": "商品3",
			"is_enable_model": "启用规格",
			"model": {
				"models":{
					"M": {
						"price": 300,
						"stock_type": "无限"
					},
					"S": {
						"price": 300,
						"stock_type": "无限"
					}
				}
			}
		}, {
			"name": "商品4",
			"price":400
		}]	
		"""

	When jobs创建限时抢购活动
		"""
		[{
			"name": "商品1限时抢购",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品1",
			"count_per_purchase": 2,
			"promotion_price": 10
		}]

		"""
	When jobs创建买赠活动
		"""
		[{
			"name": "商品2买二赠一",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品2",
			"premium_products": [{
				"name": "商品4",
				"count": 1
			}],
			"count": 2,
			"is_enable_cycle_mode": true
		}]
		"""
	And bill关注jobs的公众号
	And tom关注jobs的公众号

@mall2 @mall.webapp @mall.webapp.shopping_cart
Scenario:1 放入多个商品（商品1,2,3）到购物车，商品1是限时抢购活动，商品2是买赠活动，商品3是多规格商品，没有参加任何活动
	jobs添加商品后
	1. bill能在webapp中将jobs添加的商品放入购物车
	2. tom的购物车不受bill操作的影响
	注意：总价和总商品数量是在前台计算，对它们的测试放到ui测试中，这里无法测试

	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 1
		},{
			"name": "商品2",
			"count": 2
		},{
			"name": "商品3",
			"model": {
				"models":{
					"M": {
						"count": 1
					}
				}
			}
		}, {
			"name": "商品3",
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
				"promotion": {
					"type": "flash_sale",
					"result": {
						"saved_money": 90
					}
				},
				"can_use_promotion": true,
				"products": [{
					"name": "商品1",
					"price": 10,
					"count": 1
				}]
			}, {
				"promotion": {
					"type": "premium_sale",
					"result": {
						"premium_products": [{
							"name": "商品4",
							"premium_count": 1
						}]
					}
				},
				"can_use_promotion": true,
				"products": [{
					"name": "商品2",
					"price": 200,
					"count": 2
				}]
			}, {
				"products": [{
					"name": "商品3",
					"price": 300,
					"count": 1,
					"model": "M"
				}, {
					"name": "商品3",
					"price": 300,
					"count": 1,
					"model": "S"
				}]
			}],
			"invalid_products": []
		}
		"""

	When tom访问jobs的webapp
	Then tom能获得购物车
		"""
		{
			"product_groups": [],
			"invalid_products": []
		}
		"""


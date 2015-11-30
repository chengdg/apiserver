#author: 宋温馨
Feature:添加商品到购物车后修改商品名称和库存
Background:
	Given jobs登录系统
	And jobs已添加商品
	"""
	[{
		"name": "商品1",
		"model": {
			"models": {
				"standard": {
					"price": 100.00,
					"weight": 1,
					"stock_type": "有限",
					"stocks": 3
				}
			}
		}
	}]

	"""
	And tom关注jobs的公众号

@shopping
Scenario:1商品加入购物车后修改商品的名称
	When tom访问jobs的webapp
	And tom加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 1
		}]
		"""
	Then tom能获得购物车
		"""
		{
			"product_groups": [{
				"promotion": null,
				"can_use_promotion": false,
				"products": [{
					"name": "商品1",
					"price": 100.00,
					"count": 1
				}]
			}],
			"invalid_products": []
		}
		"""
	Given jobs登录系统
	When jobs更新商品'商品1'
		"""
		{
			"name": "商品1111",
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"weight": 1,
						"stock_type": "有限",
						"stocks": 3
					}
				}
			}
		}
		"""
	Then jobs能获取商品'商品1111'
		"""
		{
			"name":"商品1111",
			"price":100.00
		}
		"""
	When tom访问jobs的webapp
	Then tom能获得购物车
		"""
		{
			"product_groups": [{
				"promotion": null,
				"can_use_promotion": false,
				"products": [{
					"name": "商品1111",
					"price": 100,
					"count": 1
				}]
			}],
			"invalid_products": []
		}
		"""

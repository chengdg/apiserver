#author: benchi
#editor: 师帅 2015.10.19
@func:webapp.modules.mall.views.list_products

Feature: 添加商品到购物车中
	bill能在webapp中将jobs添加的"商品"放入购物车

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
			"price": 3
		}, {
			"name": "商品2",
			"price": 5
		}, {
			"name": "商品3",
			"is_enable_model": "启用规格",
			"model": {
				"models":{
					"M": {
						"price": 7,
						"stock_type": "有限",
						"stocks": 2
					},
					"S": {
						"price": 8,
						"stock_type": "无限"
					}
				}
			}
		}, {
			"name": "商品4",
			"is_enable_model": "启用规格",
			"model": {
				"models":{
					"M": {
						"price": 9,
						"stock_type": "无限"
					}
				}   
			}
		}, {
			"name": "商品5",
			"is_enable_model": "启用规格",
			"model": {
				"models":{
					"S": {
						"price": 10,
						"stock_type": "无限"
					}
				}
			}
		}]	
		"""
	And bill关注jobs的公众号
	And tom关注jobs的公众号

@mall2 @mall.webapp @mall.webapp.shopping_cart
Scenario:1 放入单个商品到购物车
	jobs添加商品后
	1. bill能在webapp中将jobs添加的商品放入购物车
	2. 每放入一次，该商品在购物车中的数量增加一个
	3. tom的购物车不受bill操作的影响
	注意：总价和总商品数量是在前台计算，对它们的测试放到ui测试中，这里无法测试

	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 1
		}]
		"""
	Then bill能获得购物车
		"""
		{
			"product_groups": [{
				"promotion": null,
				"can_use_promotion": false,
				"products": [{
					"name": "商品1",
					"price": 3,
					"count": 1
				}]
			}],
			"invalid_products": []
		}
		"""
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 2
		}]
		"""
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 3
		}]
		"""
	Then bill能获得购物车
		"""
		{
			"product_groups": [{
				"promotion": null,
				"can_use_promotion": false,
				"products": [{
					"name": "商品1",
					"price": 3,
					"count": 6
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

@mall2 @mall.webapp @mall.webapp.shopping_cart
Scenario:2 放入多个商品到购物车
	jobs添加商品后
	1. bill能在webapp中将jobs添加的商品放入购物车
	2. 多次放入不同商品会增加购物车中商品的条数

	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 1
		}]
		"""
	Then bill能获得购物车
		"""
		{
			"product_groups": [{
				"promotion": null,
				"can_use_promotion": false,
				"products": [{
					"name": "商品1",
					"price": 3,
					"count": 1
				}]
			}],
			"invalid_products": []
		}
		"""
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品2",
			"count": 2
		}]
		"""
	Then bill能获得购物车
		"""
		{
			"product_groups": [{
				"promotion": null,
				"can_use_promotion": false,
				"products": [{
					"name": "商品1",
					"price": 3,
					"count": 1
				}, {
					"name": "商品2",
					"price": 5,
					"count": 2
				}]
			}],
			"invalid_products": []
		}
		"""

@mall2 @mall.webapp @mall.webapp.shopping_cart
Scenario:3 商品添加到购物车后，后台对商品进行上下架管理
	bill在webapp中将jobs的商品加入到购物车后，jobs对此商品进行删除操作
	1.bill查看jobs的webapp购物车，此商品已无效
	2.不影响购物车的其他商品

	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 1
		}, {
			"name": "商品2",
			"count": 1
		}]
		"""
	Then bill能获得购物车
		"""
		{
			"product_groups": [{
				"products": [{
					"name": "商品1",
					"price": 3,
					"count": 1
				}, {
					"name": "商品2",
					"price": 5,
					"count": 1
				}]
			}],
			"invalid_products": []
		}
		"""
	Given jobs登录系统
	When jobs-下架商品'商品1'
	When bill访问jobs的webapp
	Then bill能获得购物车
		"""
		{
			"product_groups": [{
				"products": [{
					"name": "商品2",
					"price": 5,
					"count": 1
				}]
			}],
			"invalid_products": [{
				"name": "商品1",
				"price": 3,
				"count": 1
			}]
		}
		"""

	Given jobs登录系统
	When jobs-上架商品'商品1'
	When bill访问jobs的webapp
	Then bill能获得购物车
		"""
		{
			"product_groups": [{
				"products": [{
					"name": "商品1",
					"price": 3,
					"count": 1
				}, {
					"name": "商品2",
					"price": 5,
					"count": 1
				}]
			}],
			"invalid_products": []
		}
		"""

@mall2 @mall.webapp @mall.webapp.shopping_cart
Scenario:4 商品添加到购物车后，后台对商品规格进行修改
	bill在webapp中将jobs的商品加入到购物车后，jobs将此商品的商品规格进行修改
	1.bill查看jobs的webapp购物车，此商品已无效
	2.bill可以清空无效商品

	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
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
				"products": [{
					"name": "商品3",
					"price": 7,
					"count": 1,
					"model": "M"
				}, {
					"name": "商品3",
					"price": 8,
					"count": 1,
					"model": "S"
				}]
			}],
			"invalid_products": []
		}
		"""
	#更改规格M的库存为0
	Given jobs登录系统
	When jobs更新商品'商品3'
		"""
		{
			"name": "商品3",
			"is_enable_model": "启用规格",
			"model": {
				"models":{
					"M": {
						"price": 7,
						"stock_type": "有限",
						"stocks": 0
					},
					"S": {
						"price": 8,
						"stock_type": "无限"
					}
				}
			}
		}
		"""
	Then jobs能获取商品'商品3'
		"""
		{
			"name": "商品3",
			"is_enable_model": "启用规格",
			"model": {
				"models":{
					"M": {
						"price": 7,
						"stock_type": "有限",
						"stocks": 0
					},
					"S": {
						"price": 8,
						"stock_type": "无限"
					}
				}
			}
		}
		"""
	When bill访问jobs的webapp
	Then bill能获得购物车
		"""
		{
			"product_groups": [{
				"products": [{
					"name": "商品3",
					"price": 8,
					"count": 1,
					"model": "S"
				}]
			}],
			"invalid_products": [{
				"name": "商品3",
				"price": 7,
				"count": 1,
				"model": "M"
			}]
		}
		"""
	#删除规格S
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品5",
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
					"name": "商品3",
					"price": 8,
					"count": 1,
					"model": "S"
				}, {
					"name": "商品5",
					"price": 10,
					"count": 1,
					"model": "S"
				}]
			}],
			"invalid_products": [{
				"name": "商品3",
				"price": 7,
				"count": 1,
				"model": "M"
			}]
		}
		"""
	Given jobs登录系统
	When jobs删除商品规格'尺寸'的值'S'
	When bill访问jobs的webapp
	Then bill能获得购物车
		"""
		{
			"product_groups": [],
			"invalid_products": [{
				"name": "商品3",
				"price": 7,
				"count": 1,
				"model": "M"
			}, {
				"name": "商品3",
				"price": 8,
				"count": 1
			}, {
				"name": "商品5",
				"price": 10,
				"count": 1
			}]
		}
		"""
	#商品4的规格从custom model变为standard model
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品4",
			"model": {
				"models":{
					"M": {
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
					"name": "商品4",
					"price": 9,
					"count": 1,
					"model": "M"
				}]
			}],
			"invalid_products": [{
				"name": "商品3",
				"price": 7,
				"count": 1,
				"model": "M"
			}, {
				"name": "商品3",
				"price": 8,
				"count": 1
			}, {
				"name": "商品5",
				"price": 10,
				"count": 1
			}]
		}
		"""
	Given jobs登录系统
	When jobs更新商品'商品4'
		"""
		{
			"name": "商品4",
			"model": {
				"models":{
					"standard": {
						"price": 9.5
					}
				}
			}
		}
		"""
	When bill访问jobs的webapp
	Then bill能获得购物车
		"""
		{
			"product_groups": [],
			"invalid_products": [{
				"name": "商品3",
				"price": 7,
				"count": 1
			}, {
				"name": "商品3",
				"price": 8,
				"count": 1
			}, {
				"name": "商品5",
				"price": 10,
				"count": 1
			}, {
				"name": "商品4",
				"price": 9,
				"count": 1
			}]
		}
		"""
	When bill从购物车中删除商品
		"""
		["商品3", "商品5", "商品4"]
		"""
	Then bill能获得购物车
		"""
		{
			"product_groups": [],
			"invalid_products": []
		}
		"""
	#商品1的规格从standard model到custom model
	When bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1"
		}]
		"""
	Then bill能获得购物车
		"""
		{
			"product_groups": [{
				"products": [{
					"name": "商品1",
					"price": 3,
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
			"name": "商品1",
			"is_enable_model": "启用规格",
			"model": {
				"models":{
					"M": {
						"price": 9.5,
						"stock_type": "有限",
						"stocks": 2
					}
				}
			}
		}
		"""
	When bill访问jobs的webapp
	Then bill能获得购物车
		"""
		{
			"product_groups": [],
			"invalid_products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""

@mall2 @mall.webapp @mall.webapp.shopping_cart
Scenario: 5 商品添加到购物车后，进行删除
	bill加入jobs的商品到购物车后
	1.可以对购物车的商品进行删除

	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 1
		}, {
			"name": "商品2",
			"count": 1
		}, {
			"name": "商品4",
			"model": {
				"models":{
					"M": {
						"count": 3
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
					"name": "商品1"
				}, {
					"name": "商品2"
				}, {
					"name": "商品4"
				}]
			}],
			"invalid_products": []
		}
		"""
	When bill从购物车中删除商品
		"""
		["商品1", "商品2"]
		""" 
	Then bill能获得购物车
		"""
		{
			"product_groups": [{
				"products": [{
					"name": "商品4"
				}]
			}],
			"invalid_products": []
		}
		"""

@mall2 @mall.webapp @mall.webapp.shopping_cart @bc
Scenario:6 商品添加到购物车后，后台对商品的价格，库存进行修改（库存数量不为0）
	bill在webapp中将jobs的商品加入到购物车后，jobs将此商品的商品规格进行修改
	1.bill查看jobs的webapp购物车，此商品有效，价格与库存为更改后的值

	
	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
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
				"products": [{
					"name": "商品3",
					"price": 7,
					"count": 1,
					"model": "M"
				}, {
					"name": "商品3",
					"price": 8,
					"count": 1,
					"model": "S"
				}]
			}],
			"invalid_products": []
		}
		"""
	#更改规格M的库存为3 S的价格为10
	Given jobs登录系统
	When jobs更新商品'商品3'
		"""
		{
			"name": "商品3",
			"is_enable_model": "启用规格",
			"model": {
				"models":{
					"M": {
						"price": 7,
						"stock_type": "有限",
						"stocks": 3
					},
					"S": {
						"price": 10,
						"stock_type": "无限"
					}
				}
			}
		}
		"""
	Then jobs能获取商品'商品3'
		"""
		{
			"name": "商品3",
			"is_enable_model": "启用规格",
			"model": {
				"models":{
					"M": {
						"price": 7,
						"stock_type": "有限",
						"stocks": 3
					},
					"S": {
						"price": 10,
						"stock_type": "无限"
					}
				}
			}
		}
		"""
	When bill访问jobs的webapp
	Then bill能获得购物车
		"""
		{
			"product_groups": [{
				"products": [{
					"name": "商品3",
					"price": 7,
					"count": 1,
					"model": "M",
					"stocks": 3
				}, {
					"name": "商品3",
					"price": 10,
					"count": 1,
					"model": "S"
				}]
			}],
			"invalid_products": []
		}
		"""
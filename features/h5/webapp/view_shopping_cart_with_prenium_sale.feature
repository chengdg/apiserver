# __edit__ : "benchi"
#editor:王丽 2015.10.20

Feature: 添加参与买赠活动的商品到购物车中

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
			"price": 30
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
		}]	
		"""
	When jobs创建买赠活动
		"""
		[{
			"name": "商品1买二赠三",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品1",
			"premium_products": [{
				"name": "商品2",
				"count": 1
			}, {
				"name": "商品3",
				"count": 2
			}],
			"count": 2,
			"is_enable_cycle_mode": true
		}, {
			"name": "商品2买一赠一",
			"start_date": "今天",
			"end_date": "2天后",
			"product_name": "商品2",
			"premium_products": [{
				"name": "商品4",
				"count": 1
			}],
			"count": 1,
			"is_enable_cycle_mode": false
		}, {
			"name": "商品3买一赠一",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品3",
			"premium_products": [{
				"name": "商品4",
				"count": 1
			}],
			"count": 1,
			"is_enable_cycle_mode": false
		}, {
			"name": "商品5买一赠一",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品5",
			"premium_products": [{
				"name": "商品4",
				"count": 1
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	And bill关注jobs的公众号

@mall2 @buy @cart   @mall.webapp @mall.webapp.shopping_cart
Scenario: 1 放入1个商品到购物车，商品不满足买赠的购买基数
	bill将商品放入到购物车后
	1. bill能看到购物车中商品的详情
	
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
					"price": 30.0,
					"count": 1
				}]
			}],
			"invalid_products": []
		}
		"""

@mall2 @buy @cart   @mall.webapp @mall.webapp.shopping_cart
Scenario: 2 放入1个商品到购物车，商品数量等于买赠的购买基数
	bill将商品放入到购物车后
	1. bill能看到购物车中商品的详情
	
	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 2
		}]
		"""
	Then bill能获得购物车
		"""
		{
			"product_groups": [{
				"promotion": {
					"type": "premium_sale",
					"result": {
						"premium_products": [{
							"name": "商品2",
							"premium_count": 1
						}, {
							"name": "商品3",
							"premium_count": 2
						}]
					}
				},
				"can_use_promotion": true,
				"products": [{
					"name": "商品1",
					"price": 30.0,
					"count": 2
				}]
			}],
			"invalid_products": []
		}
		"""

@mall2 @buy @cart   @mall.webapp @mall.webapp.shopping_cart
Scenario: 3 放入多个商品到购物车，商品数量大于买赠的购买基数，并满足循环买赠
	bill将商品放入到购物车后
	1. bill能看到购物车中商品的详情
	
	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品1",
			"count": 5
		}]
		"""
	Then bill能获得购物车
		"""
		{
			"product_groups": [{
				"promotion": {
					"type": "premium_sale",
					"result": {
						"premium_products": [{
							"name": "商品2",
							"premium_count": 2
						}, {
							"name": "商品3",
							"premium_count": 4
						}]
					}
				},
				"can_use_promotion": true,
				"products": [{
					"name": "商品1",
					"price": 30.0,
					"count": 5
				}]
			}],
			"invalid_products": []
		}
		"""

@mall2 @buy @cart   @mall.webapp @mall.webapp.shopping_cart 
Scenario: 4 放入多个商品到购物车，商品数量大于买赠的购买基数，但循环买赠没启用
	bill将商品放入到购物车后
	1. bill能看到购物车中商品的详情
	
	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品2",
			"count": 3
		}]
		"""
	Then bill能获得购物车
		"""
		{
			"product_groups": [{
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
					"price": 5.0,
					"count": 3
				}]
			}],
			"invalid_products": []
		}
		"""

@mall2 @buy @cart   @mall.webapp @mall.webapp.shopping_cart 
Scenario: 5 放入多规格商品到购物车
	
	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品5",
			"model": {
				"models":{
					"M": {
						"count": 1
					}
				}
			}
		}, {
			"name": "商品5",
			"model": {
				"models":{
					"S": {
						"count": 2
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
					"type": "premium_sale",
					"result": {
						"premium_products": [{
							"name": "商品4",
							"premium_count": 3
						}]
					}
				},
				"can_use_promotion": true,
				"products": [{
					"name": "商品5",
					"model": "M",
					"price": 7.0,
					"count": 1
				}, {
					"name": "商品5",
					"model": "S",
					"price": 8.0,
					"count": 2
				}]
			}],
			"invalid_products": []
		}
		"""

@mall2 @buy @cart   @mall.webapp @mall.webapp.shopping_cart
Scenario: 6 新建买赠活动，买一赠一，买商品6赠 商品6，循环买赠
	
	Given jobs登录系统
	And jobs已添加商品
	"""
		[{
			"name": "商品6",
			"price": 100.00
		}]
	"""
	When jobs创建买赠活动
	"""
		[{
			"name": "商品6买1赠1",
			"start_date": "1天前",
			"end_date": "3天后",
			"product_name": "商品6",
			"premium_products": [{
				"name": "商品6",
				"count": 1
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
	"""
	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品6",
			"count": 3
		}]
		"""
	Then bill能获得购物车
		"""
		{
			"product_groups": [{
				"promotion": {
					"type": "premium_sale",
					"result": {
						"premium_products": [{
							"name": "商品6",
							"premium_count": 3
						}]
					}
				},
				"can_use_promotion": true,
				"products": [{
					"name": "商品6",
					"price": 100.0,
					"count": 3
				}]
			}],
			"invalid_products": []
		}
		"""

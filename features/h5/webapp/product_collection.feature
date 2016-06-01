# watcher: fengxuejing@weizoom.com,wangxinrui@weizoom.com,benchi@weizoom.com
# __author__ : "冯雪静"
#editor 新新 2015.10.20
#editor 玉成 2015.12.03
Feature: 在webapp中收藏商品
	bill能在webapp中收藏jobs添加的"商品"

Background:
	Given 重置'weapp'的bdd环境
	Given jobs登录系统::weapp
	
	And jobs已添加商品规格::weapp
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
	And jobs已添加商品::weapp
		"""
		[{
			"name": "商品1",
			"price": 100.00
		}, {
			"name": "商品2",
			"is_enable_model": "启用规格",
			"model": {
				"models":{
					"M": {
						"price": 50.00,
						"stock_type": "无限"
					},
					"S": {
						"price": 100.00,
						"stock_type": "无限"
					}
				}
			}
		}, {
			"name": "商品3",
			"price": 100.00
		}]
		"""
	And bill关注jobs的公众号::weapp
	And tom关注jobs的公众号::weapp

@mall2 @weapp.mall.collect.product @bert @mall3
Scenario:1 收藏单个无规格商品
	jobs添加商品后
	1. bill能在webapp中将jobs添加的商品收藏
	2. bill能在个人中心我的收藏，查看已收藏的商品
	3. tom的个人中心我的收藏不受bill操作的影响

	When bill访问jobs的webapp
	When bill收藏jobs的商品到我的收藏
		"""
		{
			"name": "商品1"
		}
		"""
	Then bill能获得我的收藏
		"""
		[{
			"name": "商品1",
			"price_info": {
				"min_price": 100.00
			}
		}]
		"""
	When tom访问jobs的webapp
	Then tom能获得我的收藏
		"""
		[]
		"""

@mall2 @weapp.mall.collect.product @bert @mall3
Scenario:2 收藏多个商品，包括无规格和有规格的商品
	jobs添加商品后
	1. bill能在webapp中将jobs添加的商品收藏
	2. bill能在个人中心我的收藏，查看已收藏的商品
	3. 收藏的商品按时间的倒序排列

	When bill访问jobs的webapp
	When bill收藏jobs的商品到我的收藏
		"""
		{
			"name": "商品1"
		}
		"""
	Then bill能获得我的收藏
		"""
		[{
			"name": "商品1",
			"price_info": {
				"min_price": 100.00
			}
		}]
		"""
	When bill收藏jobs的商品到我的收藏
		"""
		{
			"name": "商品2"
		}
		"""
	Then bill能获得我的收藏
		"""
		[{
			"name": "商品2",
			"price_info": {
				"min_price": 50.00
			}
		}, {
			"name": "商品1",
			"price_info": {
				"min_price": 100.00
			}
		}]
		"""

@mall2 @weapp.mall.collect.product @bert @mall3 @wip.pc2
Scenario:3 从我的收藏里面取消收藏商品
	bill在webapp收藏jobs的商品后
	1. bill能取消收藏已收藏的商品

	When bill访问jobs的webapp
	When bill收藏jobs的商品到我的收藏
		"""
		{
			"name": "商品1"
		}
		"""
	Then bill能获得我的收藏
		"""
		[{
			"name": "商品1",
			"price_info": {
				"min_price": 100.00
			}
		}]
		"""
	When bill取消收藏已收藏的商品
		"""
		{
			"name": "商品1"
		}
		"""
	Then bill能获得我的收藏
		"""
		[]
		"""
	When bill收藏jobs的商品到我的收藏
		"""
		{
			"name": "商品1"
		}
		"""
	And bill收藏jobs的商品到我的收藏
		"""
		{
			"name": "商品2"
		}
		"""
	And bill收藏jobs的商品到我的收藏
		"""
		{
			"name": "商品3"
		}
		"""

	Then bill能获得我的收藏
		"""
		[{
			"name": "商品3",
			"price_info": {
				"min_price": 100.00
			}
		}, {
			"name": "商品2",
			"price_info": {
				"min_price": 50.00
			}
		}, {
			"name": "商品1",
			"price_info": {
				"min_price": 100.00
			}
		}]
		"""
	When bill取消收藏已收藏的商品
		"""
		{
			"name": "商品2"
		}
		"""
	And bill取消收藏已收藏的商品
		"""
		{
			"name": "商品1"
		}
		"""
	Then bill能获得我的收藏
		"""
		[{
			"name": "商品3",
			"price_info": {
				"min_price": 100.00
			}
		}]
		"""

@mall2 @weapp.mall.collect.product @bert @mall3 
Scenario:4 收藏商品后，后台对此商品进行修改
	bill在webapp收藏jobs的商品后
	1. jobs对此商品进行修改价格

	When bill访问jobs的webapp
	When bill收藏jobs的商品到我的收藏
		"""
		{
			"name": "商品1"
		}
		"""
	Then bill能获得我的收藏
		"""
		[{
			"name": "商品1",
			"price_info": {
				"min_price": 100.00
			}
		}]
		"""
	Given jobs登录系统::weapp
	When  jobs更新商品'商品1'::weapp
		"""
		{
			"name": "商品1",
			"price": 50.00
		}
		"""
	When bill访问jobs的webapp
	Then bill能获得我的收藏
		"""
		[{
			"name": "商品1",
			"price_info": {
				"min_price": 50.00
			}
		}]
		"""

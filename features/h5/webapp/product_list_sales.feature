# watcher: fengxuejing@weizoom.com,benchi@weizoom.com
# __author__ : "冯雪静"

Feature: webapp商品列表页显示商品销量
	"""
	后台通用配置
		1.商品销量
		2.商品排序
		3.商品搜索框
		4.购物车
	开启商品销量功能后
		1.开启商品销量功能，商品列表页的商品上面显示销量，商品分组的商品列表也显示
		2.关闭商品销量功能，商品列表页的商品上面不显示销量，
	"""

Background:
	Given 重置'weapp'的bdd环境
	Given jobs登录系统::weapp
	When jobs'修改'通用设置::weapp
		"""
		{
			"product_sales": "开启",
			"product_sort": "关闭",
			"product_search": "关闭",
			"shopping_cart": "关闭"
		}
		"""
	Given jobs已添加支付方式::weapp
		"""
		[{
			"type": "支付宝"
		}, {
			"type": "货到付款"
		}, {
			"type": "微信支付"
		}]
		"""
	And jobs已添加商品分类::weapp
		"""
		[{
			"name": "分类1"
		}, {
			"name": "分类2"
		}, {
			"name": "分类3"
		}]
		"""
	And jobs已添加商品::weapp
		"""
		[{
			"name": "商品1",
			"categories": "分类3",
			"price": 100.00,
			"display_index": 0
		}, {
			"name": "商品2",
			"categories": "分类3",
			"price": 100.00,
			"display_index": 0
		}, {
			"name": "商品3",
			"categories": "分类3",
			"price": 100.00,
			"display_index": 0
		}, {
			"name": "苹果1",
			"categories": "分类2,分类3",
			"price": 100.00,
			"display_index": 0
		}, {
			"name": "苹果2",
			"categories": "分类2,分类3",
			"price": 100.00,
			"display_index": 0
		}, {
			"name": "苹果3",
			"categories": "分类2,分类3",
			"price": 100.00,
			"display_index": 0
		}]
		"""
	And bill关注jobs的公众号
	And tom关注jobs的公众号

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"pay_type": "货到付款",
			"products": [{
				"name": "商品1",
				"count": 6
			}, {
				"name": "商品2",
				"count": 5
			}, {
				"name": "商品3",
				"count": 4
			}]
		}
		"""
	When tom访问jobs的webapp
	When tom购买jobs的商品
		"""
		{
			"pay_type": "货到付款",
			"products": [{
				"name": "苹果1",
				"count": 6
			}, {
				"name": "苹果2",
				"count": 5
			}, {
				"name": "苹果3",
				"count": 4
			}]
		}
		"""

@mall3 @ztq
Scenario:1 后台修改通用配置(开启和关闭商品销量功能)
	1.jobs开启商品销量功能，商品列表页的商品上面显示销量
	2.jobs关闭商品销量功能，商品列表页的商品上面不显示销量

	When bill访问jobs的webapp
	When bill浏览jobs的webapp的'全部'商品列表页
	Then bill获得webapp商品列表
		"""
		[{
			"name": "苹果3",
			"price": 100.00,
			"sales": 4
		}, {
			"name": "苹果2",
			"price": 100.00,
			"sales": 5
		}, {
			"name": "苹果1",
			"price": 100.00,
			"sales": 6
		}, {
			"name": "商品3",
			"price": 100.00,
			"sales": 4
		}, {
			"name": "商品2",
			"price": 100.00,
			"sales": 5
		}, {
			"name": "商品1",
			"price": 100.00,
			"sales": 6
		}]
		"""
	When tom访问jobs的webapp
	When tom浏览jobs的webapp的'分类2'商品列表页
	Then tom获得webapp商品列表
		"""
		[{
			"name": "苹果3",
			"price": 100.00,
			"sales": 4
		}, {
			"name": "苹果2",
			"price": 100.00,
			"sales": 5
		}, {
			"name": "苹果1",
			"price": 100.00,
			"sales": 6
		}]
		"""
	Given jobs登录系统::weapp
	When jobs'修改'通用设置::weapp
		"""
		{
			"product_sales": "关闭",
			"product_sort": "关闭",
			"product_search": "关闭",
			"shopping_cart": "关闭"
		}
		"""
	When bill访问jobs的webapp
	When bill浏览jobs的webapp的'全部'商品列表页
	Then bill获得webapp商品列表
		"""
		[{
			"name": "苹果3",
			"price": 100.00
		}, {
			"name": "苹果2",
			"price": 100.00
		}, {
			"name": "苹果1",
			"price": 100.00
		}, {
			"name": "商品3",
			"price": 100.00
		}, {
			"name": "商品2",
			"price": 100.00
		}, {
			"name": "商品1",
			"price": 100.00
		}]
		"""
	When tom访问jobs的webapp
	When tom浏览jobs的webapp的'分类2'商品列表页
	Then tom获得webapp商品列表
		"""
		[{
			"name": "苹果3",
			"price": 100.00
		}, {
			"name": "苹果2",
			"price": 100.00
		}, {
			"name": "苹果1",
			"price": 100.00
		}]
		"""


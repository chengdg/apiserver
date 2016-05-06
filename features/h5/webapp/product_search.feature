# watcher: fengxuejing@weizoom.com,benchi@weizoom.com
# __author__ : "冯雪静"

Feature: webapp商品列表页搜索商品
	"""
	后台通用配置
		1.商品销量
		2.商品排序
		3.商品搜索框
		4.购物车
	开启搜索功能后
		1.开启底部导航，商品列表页顶部直接显示一个商品搜索框
		2.关闭底部导航，商品列表页顶部显示分组，商品搜索框，购物车
		3.点击搜索框，跳转到商品搜索页，

	"""

Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
	When jobs'修改'通用设置:weapp
		"""
		{
			"product_sales": "关闭",
			"product_sort": "关闭",
			"product_search": "开启",
			"shopping_cart": "关闭"
		}
		"""
	Given jobs已添加支付方式:weapp
		"""
		[{
			"type": "支付宝"
		}, {
			"type": "货到付款"
		}, {
			"type": "微信支付"
		}]
		"""
		"""
	And jobs已添加商品分类
		"""
		[{
			"name": "分类1"
		}, {
			"name": "分类2"
		}, {
			"name": "分类3"
		}]
		"""
	And jobs已添加商品:weapp
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
			"categories": "分类2",
			"price": 100.00,
			"display_index": 0
		}, {
			"name": "苹果2",
			"categories": "分类2",
			"price": 100.00,
			"display_index": 0
		}, {
			"name": "苹果3",
			"categories": "分类2",
			"price": 100.00,
			"display_index": 0
		}, {
			"name": "小米1",
			"categories": "分类2,分类3",
			"price": 100.00,
			"display_index": 0
		}, {
			"name": "小米商品2",
			"categories": "分类2,分类3",
			"price": 100.00,
			"display_index": 0
		}, {
			"name": "商品苹果3",
			"categories": "分类2,分类3",
			"price": 100.00,
			"display_index": 0
		}]
		"""
	And bill关注jobs的公众号


Scenario:1 后台修改通用配置(开启和关闭商品搜索功能)
	1.jobs开启商品搜索功能，商品列表页显示搜索框
	2.jobs关闭商品搜索功能，商品列表页不显示搜索框

	When bill访问jobs的webapp
	Then bill'能'获得商品搜索框
	#后台修改通用配置关闭商品搜索功能
	Given jobs登录系统:weapp
	When jobs'修改'通用设置:weapp
		"""
		{
			"product_sales": "关闭",
			"product_sort": "关闭",
			"product_search": "关闭",
			"shopping_cart": "关闭"
		}
		"""
	When bill访问jobs的webapp
	Then bill'不能'获得商品搜索框


Scenario:2 后台修改通用配置(开启和关闭商品搜索功能)






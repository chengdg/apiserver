# watcher: fengxuejing@weizoom.com,benchi@weizoom.com
# __author__ : "冯雪静"

Feature: webapp商品列表商品排序
	"""
	后台通用配置
		1.商品销量
		2.商品排序
		3.商品搜索框
		4.购物车
	开启商品排序功能后：默认排序，销量，价格
		1.jobs开启商品排序功能，商品列表页显示排序框
		2.jobs关闭商品排序功能，商品列表页不显示排序框
		3.(商品全部列表和分组商品列表)商品列表默认排序，上箭头变红，升序-时间倒序排列
		4.(商品全部列表和分组商品列表)bill第一次点击默认排序，下箭头变红，降序-时间正序排列
		5.(商品全部列表和分组商品列表)bill第二次点击默认排序，上箭头变红，升序-时间倒序排列
		6.(商品全部列表和分组商品列表)bill第一次点击销量排序，降序-销量由大到小，如：销量一样按照默认排序
		7.(商品全部列表和分组商品列表)bill第二次点击销量排序，和第一次点击一样不变
		8.(商品全部列表和分组商品列表)bill第一次点击价格排序，上箭头变红，升序-价格由小到大，如：价格一样按照默认排序
		9.(商品全部列表和分组商品列表)bill第二次点击价格排序，下箭头变红，升序-价格由大到小，如：价格一样按照默认排序
		10.(商品全部列表)根据商品搜索条件进行排序，默认排序，销量，价格
	"""

Background:
	Given 重置'weapp'的bdd环境
	Given jobs登录系统::weapp
	When jobs'修改'通用设置::weapp
		"""
		{
			"product_sales": "关闭",
			"product_sort": "排序",
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


Scenario:1 后台修改通用配置(开启和关闭商品排序功能)
	1.jobs开启商品排序功能，商品列表页显示排序框
	2.jobs关闭商品排序功能，商品列表页不显示排序框

	When bill访问jobs的webapp
	Then bill'能'获得商品排序框
	#后台修改通用配置关闭商品搜索功能
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
	Then bill'不能'获得商品排序框

# bdd实现不了，只能手工验证
# Scenario:2 商品列表默认排序,商品不设置序号
# 	jobs开启商品排序功能，商品不设置序号
# 	1.商品列表默认排序，升序-时间倒序排列
# 	2.bill第一次点击默认排序，下箭头变红，降序-时间正序排列
# 	3.bill第二次点击默认排序，上箭头变红，升序-时间倒序排列

# 	When bill访问jobs的webapp
# 	Then bill'能'获得商品排序框
# 	#默认排序，升序-时间倒序排列
# 	When bill浏览jobs的webapp的'全部'商品列表页
# 	Then bill获得webapp商品列表
# 		"""
# 		[{
# 			"name": "商品苹果3",
# 			"price": 100.00
# 		}, {
# 			"name": "小米商品2",
# 			"price": 100.00
# 		}, {
# 			"name": "小米1",
# 			"price": 100.00
# 		}, {
# 			"name": "苹果3",
# 			"price": 100.00
# 		}, {
# 			"name": "苹果2",
# 			"price": 100.00
# 		}, {
# 			"name": "苹果1",
# 			"price": 100.00
# 		}, {
# 			"name": "商品3",
# 			"price": 100.00
# 		}, {
# 			"name": "商品2",
# 			"price": 100.00
# 		}, {
# 			"name": "商品1",
# 			"price": 100.00
# 		}]
# 		"""
# 	#第一次点击默认排序，降序-时间正序排列
# 	When bill'点击'默认排序
# 	Then bill获得webapp商品列表
# 		"""
# 		[{
# 			"name": "商品1",
# 			"price": 100.00
# 		}, {
# 			"name": "商品2",
# 			"price": 100.00
# 		}, {
# 			"name": "商品3",
# 			"price": 100.00
# 		}, {
# 			"name": "苹果1",
# 			"price": 100.00
# 		}, {
# 			"name": "苹果2",
# 			"price": 100.00
# 		}, {
# 			"name": "苹果3",
# 			"price": 100.00
# 		}, {
# 			"name": "小米1",
# 			"price": 100.00
# 		}, {
# 			"name": "小米商品2",
# 			"price": 100.00
# 		}, {
# 			"name": "商品苹果3",
# 			"price": 100.00
# 		}]
# 		"""
# 	#第二次点击默认排序，升序-时间倒序排列
# 	When bill'点击'默认排序
# 	Then bill获得webapp商品列表
# 		"""
# 		[{
# 			"name": "商品苹果3",
# 			"price": 100.00
# 		}, {
# 			"name": "小米商品2",
# 			"price": 100.00
# 		}, {
# 			"name": "小米1",
# 			"price": 100.00
# 		}, {
# 			"name": "苹果3",
# 			"price": 100.00
# 		}, {
# 			"name": "苹果2",
# 			"price": 100.00
# 		}, {
# 			"name": "苹果1",
# 			"price": 100.00
# 		}, {
# 			"name": "商品3",
# 			"price": 100.00
# 		}, {
# 			"name": "商品2",
# 			"price": 100.00
# 		}, {
# 			"name": "商品1",
# 			"price": 100.00
# 		}]
# 		"""


# Scenario:3 商品列表默认排序,商品设置序号
# 	jobs开启商品排序功能，商品设置序号
# 	1.商品列表默认排序，升序-时间倒序排列
# 	2.bill第一次点击默认排序，下箭头变红，降序-时间正序排列
# 	3.bill第二次点击默认排序，上箭头变红，升序-时间倒序排列



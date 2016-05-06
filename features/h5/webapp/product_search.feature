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
		3.首次搜索-点击搜索框，跳转到商品搜索页，显示暂无搜索记录
		4.多次搜索商品，进入商品搜索页，显示历史搜索记录最近10条，显示“清除搜索历史”按钮
		5.在全部商品列表页和分组商品列表页的搜索一样(全局搜索)
		6.在空分组的情况下，开启底部导航，只显示商品搜索框
		7.在空分组的情况下，关闭底部导航，显示分组，商品搜索框，购物车
		8.商品搜索是模糊搜索，不会自动去除名字中间的空格，名字前后的空格会过滤掉
		9.搜索商品不存在的话，会提示“没有找到相关商品”
		10.搜索记录保留最近10条，清楚记录后，从新计算
		11.更新后台商品列表排序，搜索出的结果根据商品列表排序进行排列
		12.更新后台分组中的商品排序，搜索出的结果根据商品列表排序进行排列
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
	And jobs已添加商品分类:weapp
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

@mall3 @ztq
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


Scenario:2 首次搜索商品
	首次搜索，进入商品搜索页，暂无搜索记录

	When bill访问jobs的webapp
	Then bill'能'获得商品搜索框
	Then bill获得搜索记录
		"""
		[]
		"""
	#在全部商品列表页搜索商品
	When bill浏览jobs的webapp的'全部'商品列表页
	#商品名称完全匹配
	When bill搜索商品
		"""
		{
			"product_name": "商品苹果3"
		}
		"""
	Then bill获得webapp商品列表
		"""
		[{
			"name": "商品苹果3"
		}]
		"""


Scenario:3 多次搜索商品
	多次搜索商品，进入商品搜索页，显示历史搜索记录

	When bill访问jobs的webapp
	When bill浏览jobs的webapp的'全部'商品列表页
	#模糊搜索
	When bill搜索商品
		"""
		{
			"product_name": "苹果"
		}
		"""
	Then bill获得webapp商品列表
		"""
		[{
			"name": "商品苹果3"
		}, {
			"name": "苹果3"
		}, {
			"name": "苹果2"
		}, {
			"name": "苹果1"
		}]
		"""
	Then bill获得搜索记录
		"""
		{
			"record": [
				"苹果"
			]
		}
		"""
	#模糊搜索
	When bill搜索商品
		"""
		{
			"product_name": "3"
		}
		"""
	Then bill获得webapp商品列表
		"""
		[{
			"name": "商品苹果3"
		}, {
			"name": "苹果3"
		}, {
			"name": "商品3"
		}]
		"""
	Then bill获得搜索记录
		"""
		{
			"record": [
				"3",
				"苹果"
			]
		}
		"""
	#在分组商品列表页搜索商品
	When bill浏览jobs的webapp的'分类3'商品列表页
	When bill搜索商品
		"""
		{
			"product_name": "苹果3"
		}
		"""
	Then bill获得webapp商品列表
		"""
		[{
			"name": "商品苹果3"
		}, {
			"name": "苹果3"
		}]
		"""
	Then bill获得搜索记录
		"""
		{
			"record": [
				"苹果3",
				"3",
				"苹果"
			]
		}
		"""
	#在空分组下面可以正常搜索商品
	When bill浏览jobs的webapp的'分类1'商品列表页
	When bill搜索商品
		"""
		{
			"product_name": "苹果"
		}
		"""
	Then bill获得webapp商品列表
		"""
		[{
			"name": "商品苹果3"
		}, {
			"name": "苹果3"
		}, {
			"name": "苹果2"
		}, {
			"name": "苹果1"
		}]
		"""
	#搜索同一个商品名称，只保留一个搜索记录
	Then bill获得搜索记录
		"""
		{
			"record": [
				"苹果",
				"苹果3",
				"3"
			]
		}
		"""


Scenario:4 搜索商品名称不存在

	When bill访问jobs的webapp
	When bill浏览jobs的webapp的'全部'商品列表页
	#商品名称不存在
	When bill搜索商品
		"""
		{
			"product_name": "土豆"
		}
		"""
	Then bill获得webapp商品列表
		"""
		[]
		"""
	#商品名称中含空格
	When bill搜索商品
		"""
		{
			"product_name": "商品 3"
		}
		"""
	Then bill获得webapp商品列表
		"""
		[]
		"""
	#商品名称前面含空格
	When bill搜索商品
		"""
		{
			"product_name": "  商品3"
		}
		"""
	Then bill获得webapp商品列表
		"""
		[{
			"name": "商品3"
		}]
		"""
	#商品名称前后都含空格
	When bill搜索商品
		"""
		{
			"product_name": "  商品3  "
		}
		"""
	Then bill获得webapp商品列表
		"""
		[{
			"name": "商品3"
		}]
		"""
	Then bill获得搜索记录
		"""
		{
			"record": [
				"商品3",
				"商品 3",
				"土豆"
			]
		}
		"""


Scenario:5 搜索商品记录保留最近10条
	1.搜索记录保留最后10条
	2.清除记录后，从新计算

	When bill访问jobs的webapp
	When bill浏览jobs的webapp的'全部'商品列表页
	When bill搜索商品
		"""
		{
			"product_name": "商品1"
		}
		"""
	When bill搜索商品
		"""
		{
			"product_name": "商品2"
		}
		"""
	When bill搜索商品
		"""
		{
			"product_name": "商品3"
		}
		"""
	When bill搜索商品
		"""
		{
			"product_name": "  商品1"
		}
		"""
	When bill搜索商品
		"""
		{
			"product_name": "  商品1  "
		}
		"""
	When bill搜索商品
		"""
		{
			"product_name": "商品6"
		}
		"""
	When bill搜索商品
		"""
		{
			"product_name": "商品7"
		}
		"""
	When bill搜索商品
		"""
		{
			"product_name": "商品8"
		}
		"""
	When bill搜索商品
		"""
		{
			"product_name": "商品9"
		}
		"""
	When bill搜索商品
		"""
		{
			"product_name": "商品10"
		}
		"""
	When bill搜索商品
		"""
		{
			"product_name": "商品11"
		}
		"""
	When bill搜索商品
		"""
		{
			"product_name": "商品12"
		}
		"""
	When bill搜索商品
		"""
		{
			"product_name": "商品13"
		}
		"""
	Then bill获得搜索记录
		"""
		{
			"record": [
				"商品13",
				"商品12",
				"商品11",
				"商品10",
				"商品9",
				"商品8",
				"商品7",
				"商品6",
				"商品1",
				"商品3"
			]
		}
		"""
	When bill'清除'搜索记录
	Then bill获得搜索记录
		"""
		[]
		"""
	When bill搜索商品
		"""
		{
			"product_name": "商品1"
		}
		"""
	When bill搜索商品
		"""
		{
			"product_name": "商品2"
		}
		"""
	When bill搜索商品
		"""
		{
			"product_name": "商品3"
		}
		"""
	When bill搜索商品
		"""
		{
			"product_name": "  商品1"
		}
		"""
	When bill搜索商品
		"""
		{
			"product_name": "  商品1  "
		}
		"""
	Then bill获得搜索记录
		"""
		{
			"record": [
				"商品1",
				"商品3",
				"商品2"
			]
		}
		"""


Scenario:6 搜索商品结果按后台商品排序显示顺序
	jobs更新商品列表的商品排序
	1.搜索出的结果根据商品列表排序进行排列

	Given jobs登录系统:weapp
	When jobs更新'商品2'商品排序1:weapp
	When jobs更新'商品3'商品排序2:weapp
	When bill访问jobs的webapp
	When bill浏览jobs的webapp的'全部'商品列表页
	When bill搜索商品
		"""
		{
			"product_name": "商品"
		}
		"""
	Then bill获得webapp商品列表
		"""
		[{
			"name": "商品2"
		}, {
			"name": "商品3"
		}, {
			"name": "商品苹果3"
		}, {
			"name": "小米商品2"
		}, {
			"name": "商品1"
		}]
		"""
	Given jobs登录系统:weapp
	When jobs更新分类'分类3'中商品'小米商品2'商品排序1
	When jobs更新分类'分类3'中商品'商品苹果3'商品排序2
	#更新商品分组里面的排序后，搜索商品结果根据商品列表排序进行排列
	When bill访问jobs的webapp
	When bill浏览jobs的webapp的'分类3'商品列表页
	When bill搜索商品
		"""
		{
			"product_name": "商品"
		}
		"""
	Then bill获得webapp商品列表
		"""
		[{
			"name": "商品2"
		}, {
			"name": "商品3"
		}, {
			"name": "商品苹果3"
		}, {
			"name": "小米商品2"
		}, {
			"name": "商品1"
		}]
		"""










@func:webapp.modules.mall.views.list_products
Feature: 在webapp中浏览商品列表
	bill能在webapp中看到jobs添加的"商品列表"

Background:
	Given jobs登录系统
	And jobs已添加商品分类
		"""
		[{
			"name": "分类1"
		}, {
			"name": "分类2"
		}, {
			"name": "分类3"
		}, {
			"name": "分类4"
		}]	
		"""
	And jobs已添加商品
		"""
		[{
			"name": "商品11",
			"categories": "分类1,分类2,分类3"
		}, {
			"name": "商品12",
			"categories": "分类1,分类2"
		}, {
			"name": "商品2",
			"categories": "分类2,分类3"
		}, {
			"name": "商品3"
		}, {
			"name": "商品4",
			"shelve_type": "下架"
		}]
		"""
	And bill关注jobs的公众号

@mall2 @buy @productList   @mall @mall.webapp
Scenario:1 浏览全部商品列表
	jobs添加商品后
	1. bill能在webapp中看到jobs添加的商品列表
	2. 商品按添加顺序倒序排序
	3. bill看不到被下架的商品
	
	When bill访问jobs的webapp
	And bill浏览jobs的webapp的'全部'商品列表页
	Then webapp页面标题为'商品列表'
	And bill获得webapp商品列表
		"""
		[{
			"name": "商品3"
		}, {
			"name": "商品2"
		}, {
			"name": "商品12"
		}, {
			"name": "商品11"
		}]
		"""

@mall2 @buy @productList   @mall.webapp
Scenario:2 按分类浏览商品
	jobs添加多个商品后
	1. bill能在webapp中按分类浏览商品
	2. 每个分类中"商品列表"会按照添加的顺序倒序排列
	
	When bill访问jobs的webapp
	And bill浏览jobs的webapp的'分类1'商品列表页
	Then webapp页面标题为'商品列表'
	And bill获得webapp商品列表
		"""
		[{
			"name": "商品12"
		}, {
			"name": "商品11"
		}]
		"""
	When bill浏览jobs的webapp的'分类2'商品列表页
	Then webapp页面标题为'商品列表'
	And bill获得webapp商品列表
		"""
		[{
			"name": "商品2"
		}, {
			"name": "商品12"
		}, {
			"name": "商品11"
		}]
		"""
	When bill浏览jobs的webapp的'分类3'商品列表页
	Then webapp页面标题为'商品列表'
	And bill获得webapp商品列表
		"""
		[{
			"name": "商品2"
		}, {
			"name": "商品11"
		}]
		"""
	When bill浏览jobs的webapp的'分类4'商品列表页
	Then webapp页面标题为'商品列表'
	And bill获得webapp商品列表
		"""
		[]
		"""
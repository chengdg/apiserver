Feature: 添加商品分组
"""
	Add Product Category
	Jobs能通过管理系统为管理商城添加的"商品分类"
"""

Background:
	Given 重置weapp的bdd环境

@mall @mall.product_category
Scenario:1 添加商品分类
	Jobs添加一组"商品分类"后，"商品分类列表"会按照添加的顺序倒序排列

	Given jobs登录系统:weapp
	When jobs添加商品分类:weapp
		"""
		[{
			"name": "分类1"
		}, {
			"name": "分类2"
		}, {
			"name": "分类3"
		}]
		"""
	Given bill获得访问'jobs'数据的授权
	Then bill能获取商品分类列表
		"""
		[{
			"name": "分类1",
			"product_count": 0
		}, {
			"name": "分类2",
			"product_count": 0
		}, {
			"name": "分类3",
			"product_count": 0
		}]
		"""
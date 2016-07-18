# watcher: zhangsanxiang@weizoom.com,benchi@weizoom.com
#_author_:张三香 2016.07.18

Feature:用户手机端商品列表分页

Background:
	Given 重置'weapp'的bdd环境
	Given jobs登录系统::weapp
	And jobs已添加商品::weapp
		"""
		[{
			"name":"商品1",
			"price":10.00,
			"created_at":"2015-06-01 08:00:00",
			"status":"在售"
		},{
			"name":"商品2",
			"price":20.00,
			"created_at":"2015-07-01 08:00:00",
			"status":"在售"
		},{
			"name":"商品3",
			"price":30.00,
			"created_at":"2015-08-01 08:00:00",
			"status":"在售"
		}]
		"""
	When bill关注jobs的公众号

@productlist
Scenario: 1 手机端商品列表分页
	Given jobs登录系统::weapp
	Then jobs能获取商品列表::weapp
		| name    | created_at       | display_index |
		| 商品3   | 2015-08-01 08:00 |  0            |
		| 商品2   | 2015-07-01 08:00 |  0            |
		| 商品1   | 2015-06-01 08:00 |  0            |
	When bill访问jobs的webapp
	And bill浏览jobs的webapp的'全部'商品列表页
	And bill设置商品列表分页查询参数
		"""
		{
			"count_per_page":2,
			"cur_page":1
		}
		"""
	Then bill获得webapp商品列表
		"""
		[{
			"name":"商品3",
			"price":30.00
		},{
			"name":"商品2",
			"price":20.00
		}]
		"""
	When bill设置商品列表分页查询参数
		"""
		{
			"count_per_page":2,
			"cur_page":2
		}
		"""
	Then bill获得webapp商品列表
		"""
		[{
			"name":"商品1",
			"price":10.00
		}]
		"""
	#修改商品排序后，查看手机端商品列表
		Given jobs登录系统::weapp
		When jobs更新'商品1'商品排序1::weapp
		Then jobs能获取商品列表::weapp
			| name    | created_at       | display_index |
			| 商品1   | 2015-06-01 08:00 |  1            |
			| 商品3   | 2015-08-01 08:00 |  0            |
			| 商品2   | 2015-07-01 08:00 |  0            |
		When bill访问jobs的webapp
		And bill浏览jobs的webapp的'全部'商品列表页
		And bill设置商品列表分页查询参数
			"""
			{
				"count_per_page":2,
				"cur_page":1
			}
			"""
		Then bill获得webapp商品列表
			"""
			[{
				"name":"商品1",
				"price":10.00
			},{
				"name":"商品3",
				"price":30.00
			}]
			"""
		When bill设置商品列表分页查询参数
			"""
			{
				"count_per_page":2,
				"cur_page":2
			}
			"""
		Then bill获得webapp商品列表
			"""
			[{
				"name":"商品2",
				"price":20.00
			}]
			"""

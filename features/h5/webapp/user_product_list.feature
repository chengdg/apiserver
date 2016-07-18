# watcher: zhangsanxiang@weizoom.com,benchi@weizoom.com
#_author_:张三香 2016.07.18

Feature:用户手机端商品列表分页

Background:
	Given 重置'weapp'的bdd环境
	Given jobs登录系统::weapp
	When jobs已添加商品分类::weapp
		"""
		[{
			"name": "分类1"
		}, {
			"name": "分类2"
		}]
		"""
	And jobs已添加商品::weapp
		"""
		[{
			"name":"商品1",
			"categories": "分类1,分类2",
			"price":10.00,
			"created_at":"2015-06-01 08:00:00",
			"status":"在售"
		},{
			"name":"商品2",
			"categories": "分类2",
			"price":20.00,
			"created_at":"2015-07-01 08:00:00",
			"status":"在售"
		},{
			"name":"商品3",
			"categories": "分类1",
			"price":30.00,
			"created_at":"2015-08-01 08:00:00",
			"status":"在售"
		}]
		"""
	When bill关注jobs的公众号


@mall3 @app @buy @productList @ztq
Scenario:1 手机端商品列表分页-全部商品
	When bill访问jobs的webapp
	And bill设置商品列表分页查询参数
		"""
		{
			"count_per_page":2,
			"cur_page":1,
			"categories":"全部"
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
			"cur_page":2,
			"categories":"全部"
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

		When bill访问jobs的webapp
		And bill设置商品列表分页查询参数
			"""
			{
				"count_per_page":2,
				"cur_page":1,
				"categories":"全部"
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
				"cur_page":2,
				"categories":"全部"
			}
			"""
		Then bill获得webapp商品列表
			"""
			[{
				"name":"商品2",
				"price":20.00
			}]
			"""
	#对商品进行'下架'操作
		Given jobs登录系统::weapp
		When jobs'下架'商品'商品3'::weapp
		When bill访问jobs的webapp
		And bill设置商品列表分页查询参数
			"""
			{

				"count_per_page":2,
				"cur_page":1,
				"categories":"全部"
			}
			"""
		Then bill获得webapp商品列表
			"""
			[{
				"name":"商品1",
				"price":10.00
			},{
				"name":"商品2",
				"price":20.00
			}]
			"""

	#对商品进行'上架'操作
		Given jobs登录系统::weapp
		When jobs'上架'商品'商品3'::weapp
		When bill访问jobs的webapp
		And bill设置商品列表分页查询参数
			"""
			{

				"count_per_page":2,
				"cur_page":1,
				"categories":"全部"
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
				"cur_page":2,
				"categories":"全部"
			}
			"""
		Then bill获得webapp商品列表
			"""
			[{
				"name":"商品2",
				"price":20.00
			}]
			"""
	#对商品进行'永久删除'操作
		Given jobs登录系统::weapp
		When jobs'永久删除'商品'商品3'::weapp
		When bill访问jobs的webapp
		And bill设置商品列表分页查询参数
			"""
			{

				"count_per_page":2,
				"cur_page":1,
				"categories":"全部"
			}
			"""
		Then bill获得webapp商品列表
			"""
			[{
				"name":"商品1",
				"price":10.00
			},{
				"name":"商品2",
				"price":20.00
			}]
			"""

@mall3 @app @buy @productList @ztq
Scenario:2 手机端商品列表分页-分类商品
	When bill访问jobs的webapp
	And bill设置商品列表分页查询参数
		"""
		{
			"count_per_page":1,
			"cur_page":1,
			"categories":"分类1"
		}
		"""
	Then bill获得webapp商品列表
		"""
		[{
			"name":"商品3",
			"price":30.00
		}]
		"""
	When bill设置商品列表分页查询参数
		"""
		{
			"count_per_page":1,
			"cur_page":2,
			"categories":"分类1"
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
		When jobs更新分类'分类1'中商品'商品1'商品排序1::weapp

		When bill访问jobs的webapp
		And bill设置商品列表分页查询参数
			"""
			{
				"count_per_page":1,
				"cur_page":1,
				"categories":"分类1"
			}
			"""
		Then bill获得webapp商品列表
			"""
			[{
				"name":"商品1",
				"price":10.00
			}]
			"""
		When bill设置商品列表分页查询参数
			"""
			{
				"count_per_page":1,
				"cur_page":2,
				"categories":"分类1"
			}
			"""
		Then bill获得webapp商品列表
			"""
			[{
				"name":"商品3",
				"price":30.00
			}]
			"""


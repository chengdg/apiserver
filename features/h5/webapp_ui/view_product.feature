# __author__ : "冯雪静"
@func:webapp.modules.mall.views.list_products
Feature: 在webapp中浏览商品
	bill能在webapp中看到jobs添加的"商品"
	"""
	准备数据：1.商品分类，2.商品规格，3.会员等级，4.商品，5.限时抢购活动，6.会员
	1.浏览商品
	2.浏览商品列表
	3.浏览商品分类
	4.限时抢购优先于会员价
	5.买赠活动优先于会员价
	"""

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
		}]
		"""
	And jobs已添加商品规格
		"""
		[{
			"name": "颜色",
			"type": "图片",
			"values": [{
				"name": "黑色",
				"image": "/standard_static/test_resource_img/hangzhou1.jpg"
			}, {
				"name": "白色",
				"image": "/standard_static/test_resource_img/hangzhou2.jpg"
			}]
		}, {
			"name": "尺寸",
			"type": "文字",
			"values": [{
				"name": "M"
			}, {
				"name": "S"
			}]
		}]
		"""
	When jobs添加会员等级
		"""
		[{
			"name": "铜牌会员",
			"upgrade": "手动升级",
			"discount": "9"
		}]
		"""
	Given jobs已添加商品
	#商品1：开起了会员价，多规格，起购数量 商品2：是限时抢购商品，商品3：普通商品，商品5：起购数量
		"""
		[{
			"name": "商品1",
			"promotion_title": "促销的东坡肘子",
			"categories": "分类1,分类2,分类3",
			"detail": "东坡肘子的详情",
			"status": "在售",
			"purchase_count": 3,
			"is_member_product": "on",
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou1.jpg"
			}, {
				"url": "/standard_static/test_resource_img/hangzhou2.jpg"
			}, {
				"url": "/standard_static/test_resource_img/hangzhou3.jpg"
			}],
			"is_enable_model": "启用规格",
			"model": {
				"models": {
					"黑色 S": {
						"price": 20.00,
						"stock_type": "有限",
						"stocks": 3
					},
					"白色 S": {
						"price": 10.00,
						"stock_type": "无限"
					}
				}
			}
		}, {
			"name": "商品2",
			"category": "分类1",
			"detail": "叫花鸡的详情",
			"status": "在售",
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou2.jpg"
			}],
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"stock_type": "有限",
						"stocks": 3
					}
				}
			}
		}, {
			"name": "商品3",
			"category": "",
			"detail": "叫花鸡的详情",
			"status": "在售",
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou2.jpg"
			}],
			"model": {
				"models": {
					"standard": {
						"price": 12.00,
						"stock_type": "有限",
						"stocks": 3
					}
				}
			}
		}, {
			"name": "商品4",
			"category": "",
			"detail": "叫花鸡的详情",
			"status": "待售",
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou2.jpg"
			}],
			"model": {
				"models": {
					"standard": {
						"price": 15.00,
						"stock_type": "无限"
					}
				}
			}
		}, {
			"name": "商品5",
			"category": "",
			"detail": "",
			"status": "在售",
			"purchase_count": 3,
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou2.jpg"
			}],
			"model": {
				"models": {
					"standard": {
						"price": 15.00,
						"stock_type": "有限",
						"stocks": 2
					}
				}
			}
		}]
		"""
	When jobs创建限时抢购活动
		"""
		[{
			"name": "商品2限时抢购",
			"promotion_title":"限时抢购",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name":"商品2",
			"member_grade": "铜牌会员",
			"count_per_purchase": 1,
			"promotion_price": 50.00,
			"limit_period": 1
		}]
		"""
	Given bill关注jobs的公众号
	And tom关注jobs的公众号
	Given jobs登录系统
	When jobs更新'bill'的会员等级
		"""
		{
			"name": "bill",
			"member_rank": "铜牌会员"
		}
		"""
	Then jobs可以获得会员列表
		"""
		[{
			"name": "tom",
			"member_rank": "普通会员"
		}, {
			"name": "bill",
			"member_rank": "铜牌会员"
		}]
		"""


@product @ui @ProductDetail
Scenario: 1 浏览商品
	jobs添加商品后
	1. bill能在webapp中看到jobs添加的商品
	2. tom能在webapp中看到jobs添加的商品

	When bill访问jobs的webapp
	And bill浏览jobs的webapp的'商品1'商品页
	#享受会员价的会员能获取商品原价和会员价
	#设置了起购数量3，商品详情页提示“至少购买3件”
	#库存和起购数量相等时，点击加数量时提示“库存不足”
	Then webapp页面标题为'商品1'
	And bill获得webapp商品
		"""
		{
			"name": "商品1",
			"promotion_title": "促销的东坡肘子",
			"detail": "东坡肘子的详情",
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou1.jpg"
			}, {
				"url": "/standard_static/test_resource_img/hangzhou2.jpg"
			}, {
				"url": "/standard_static/test_resource_img/hangzhou3.jpg"
			}],
			"model": {
				"models": {
					"黑色 S": {
						"price": 20.00,
						"member_price": 18.00,
						"stocks": 3,
						"count": 3,
						"提示信息": "库存不足",
						"提示信息": "至少购买3件"
					},
					"白色 S": {
						"price": 10.00,
						"member_price": 9.00,
						"count": 3,
						"提示信息": "至少购买3件"
					}
				}
			}
		}
		"""
	When bill浏览jobs的webapp的'商品2'商品页
	#享受限时抢购的会员获取的是限时抢购价
	#购买的数量等于显示抢购数量时，点击加数量提示“限购一件”
	Then webapp页面标题为'商品2'
	And bill获得webapp商品
		"""
		{
			"name": "商品2",
			"detail": "限时抢购",
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou2.jpg"
			}],
			"model": {
				"models": {
					"standard": {
						"price": 50.00,
						"count": 1,
						"提示信息": "限购一件"
					}
				}
			}
		}
		"""
	When bill浏览jobs的webapp的'商品3'商品页
	Then webapp页面标题为'商品3'
	And bill获得webapp商品
		"""
		{
			"name": "商品3",
			"detail": "叫花鸡的详情",
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou2.jpg"
			}],
			"model": {
				"models": {
					"standard": {
						"price": 12.00,
						"stocks": 3
					}
				}
			}
		}
		"""
	When bill浏览jobs的webapp的'商品5'商品页
	#起购数量大于库存数量时提示“库存不足”，“至少购买几件”
	#点击加入购物车和立即购买时提示“库存不足”
	Then webapp页面标题为'商品5'
	And bill获得webapp商品
		"""
		{
			"name": "商品5",
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou2.jpg"
			}],
			"model": {
				"models": {
					"standard": {
						"price": 15.00,
						"count": 3,
						"提示信息": "库存不足",
						"提示信息": "至少购买3件"
					}
				}
			}
		}
		"""
	When bill点击"加入购物车"
	Then bill获得错误提示'库存不足'
	When bill点击"立即购买"
	Then bill获得错误提示'库存不足'

	When tom访问jobs的webapp
	And tom浏览jobs的webapp的'商品1'商品页
	Then webapp页面标题为'商品1'
	And tom获得webapp商品
		"""
		{
			"name": "商品1",
			"promotion_title": "促销的东坡肘子",
			"detail": "东坡肘子的详情",
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou1.jpg"
			}, {
				"url": "/standard_static/test_resource_img/hangzhou2.jpg"
			}, {
				"url": "/standard_static/test_resource_img/hangzhou3.jpg"
			}],
			"model": {
				"models": {
					"黑色 S": {
						"price": 20.00,
						"stocks": 3,
						"count": 3,
						"提示信息": "库存不足",
						"提示信息": "至少购买3件"
					},
					"白色 S": {
						"price": 10.00,
						"count": 3,
						"提示信息": "至少购买3件"
					}
				}
			}
		}
		"""
	When tom浏览jobs的webapp的'商品2'商品页
	#有限商品，库存和购买数量相等时，点击加数量提示“库存不足”
	Then webapp页面标题为'商品2'
	And tom获得webapp商品
		"""
		{
			"name": "商品2",
			"detail": "叫花鸡的详情",
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou2.jpg"
			}],
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"count": 3,
						"提示信息": "库存不足"
					}
				}
			}
		} 
		"""
	When tom浏览jobs的webapp的'商品3'商品页
	Then webapp页面标题为'商品3'
	And tom获得webapp商品
		"""
		{
			"name": "商品3",
			"detail": "叫花鸡的详情",
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou2.jpg"
			}],
			"model": {
				"models": {
					"standard": {
						"price": 12.00,
						"stocks": 3
					}
				}
			}
		}
		"""

@product @ui @ProductList
Scenario: 2 浏览商品列表
	jobs添加商品后
	1. bill获得webapp商品列表，商品按添加顺序倒序排序
	2. tom获得webapp商品列表，商品按添加顺序倒序排序

	When bill访问jobs的webapp
	And bill浏览jobs的webapp的'全部'商品列表页
	#有会员价的会员获取商品列表时是会员价
	#享受限时抢购的会员获取商品列表是限时抢购价
	Then webapp页面标题为'商品列表'
	And bill获得webapp商品列表
		"""
		[{
			"name": "商品5",
			"price": 15.00
		}, {
			"name": "商品3",
			"price": 12.00
		}, {
			"name": "商品2",
			"price": 50.00
		}, {
			"name": "商品1",
			"price": 9.00
		}]
		"""
	When tom访问jobs的webapp
	And tom浏览jobs的webapp的'全部'商品列表页
	Then webapp页面标题为'商品列表'
	And tom获得webapp商品列表
		"""
		[{
			"name": "商品5",
			"price": 15.00
		}, {
			"name": "商品3",
			"price": 12.00
		}, {
			"name": "商品2",
			"price": 100.00
		}, {
			"name": "商品1",
			"price": 10.00
		}]
		"""
@product @ui @ProductList
Scenario: 3 浏览商品分类
	jobs添加商品后
	1. bill获得webapp商品列表，商品按添加顺序倒序排序
	2. tom获得webapp商品列表，商品按添加顺序倒序排序

	When bill访问jobs的webapp
	And bill浏览jobs的webapp的'分类1'商品列表页
	Then webapp页面标题为'商品列表'
	And bill获得webapp商品列表
		"""
		[{
			"name": "商品2",
			"price": 50.00
		}, {
			"name": "商品1",
			"price": 9.00
		}]
		"""
	When tom访问jobs的webapp
	And tom浏览jobs的webapp的'分类1'商品列表页
	Then webapp页面标题为'商品列表'
	And tom获得webapp商品列表
		"""
		[{
			"name": "商品2",
			"price": 100.00
		}, {
			"name": "商品1",
			"price": 10.00
		}]
		"""

#补充：张三香 2015.11.09
	#针对微商城bug5848-商品同时参与买赠和会员折扣时，手机端商品详情页显示错误（不应显示会员价）
@product @ui @ProductList
Scenario:4 查看商品详情页（买赠和会员价同时，买赠优先）
	Given jobs登录系统
	And jobs已添加商品
		"""
		[{
			"name": "买赠和会员价1",
			"promotion_title": "铜牌买赠和会员价",
			"detail": "买赠和会员价1的详情",
			"status": "在售",
			"is_member_product": "on",
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou1.jpg"
			}, {
				"url": "/standard_static/test_resource_img/hangzhou2.jpg"
			}, {
				"url": "/standard_static/test_resource_img/hangzhou3.jpg"
			}],
			"is_enable_model": "启用规格",
			"model": {
				"models": {
					"黑色 S": {
						"price": 20.00,
						"stock_type": "有限",
						"stocks": 3
					},
					"白色 S": {
						"price": 10.00,
						"stock_type": "无限"
					}
				}
			}
			},{
				"name": "买赠和会员价2",
				"promotion_title": "全部买赠和会员价",
				"detail": "买赠和会员价2的详情",
				"is_member_product": "on",
				"status": "在售",
				"swipe_images": [{
					"url": "/standard_static/test_resource_img/hangzhou2.jpg"
					}],
				"model": {
					"models": {
						"standard": {
							"price": 100.00,
							"stock_type": "无限"
						}
					}
				}
			},{
				"name": "赠品1",
				"status": "在售",
				"price": 100.00,
				"stock_type": "无限"
		}]
		"""
	When jobs创建买赠活动
		"""
		[{
			"name": "铜牌买赠和会员价1",
			"promotion_title":"铜牌买赠啦",
			"start_date": "今天",
			"end_date": "1天后",
			"member_grade": "铜牌会员",
			"product_name": "买赠和会员价1",
			"premium_products": 
			[{
				"name": "赠品1",
				"count": 1
			}],
			"count": 2,
			"is_enable_cycle_mode": true
		},{
			"name": "全部买赠和会员价2",
			"promotion_title":"全部买赠啦",
			"start_date": "今天",
			"end_date": "1天后",
			"member_grade": "全部会员",
			"product_name": "买赠和会员价2",
			"premium_products": 
			[{
				"name": "赠品1",
				"count": 1
			}],
			"count": 2,
			"is_enable_cycle_mode": true
		}]
		"""
	#普通会员浏览'买赠和会员价1',显示会员价
		When tom访问jobs的webapp
		And tom浏览jobs的webapp的'买赠和会员价1'商品页
		Then webapp页面标题为'买赠和会员价1'
		And tom获得webapp商品
			"""
			{
				"name": "买赠和会员价1",
				"promotion_title": "铜牌买赠和会员价",
				"detail": "买赠和会员价1的详情",
				"swipe_images": [{
					"url": "/standard_static/test_resource_img/hangzhou1.jpg"
				}, {
					"url": "/standard_static/test_resource_img/hangzhou2.jpg"
				}, {
					"url": "/standard_static/test_resource_img/hangzhou3.jpg"
				}],
				"model": {
					"models": {
						"黑色 S": {
							"price": 20.00,
							"member_price": 18.00,
							"stocks": 3
						},
						"白色 S": {
							"price": 10.00,
							"member_price": 9.00
						}
					}
				}
			}
			"""

	#铜牌会员浏览'买赠和会员价1',显示买赠价,不显示会员价
		When bill访问jobs的webapp
		And bill浏览jobs的webapp的'买赠和会员价1'商品页
		Then webapp页面标题为'买赠和会员价1'
		And bill获得webapp商品
			"""
			{
				"name": "买赠和会员价1",
				"promotion_title": "铜牌买赠啦",
				"detail": "买赠和会员价1的详情",
				"swipe_images": [{
					"url": "/standard_static/test_resource_img/hangzhou1.jpg"
				}, {
					"url": "/standard_static/test_resource_img/hangzhou2.jpg"
				}, {
					"url": "/standard_static/test_resource_img/hangzhou3.jpg"
				}],
				"model": {
					"models": {
						"黑色 S": {
							"price": 20.00,
							"stocks": 3
						},
						"白色 S": {
							"price": 10.00
						}
					}
				}
			}
			"""

	#普通会员浏览'买赠和会员价2',显示买赠价,不显示会员价
		When tom访问jobs的webapp
		And tom浏览jobs的webapp的'买赠和会员价2'商品页
		Then webapp页面标题为'买赠和会员价2'
		And tom获得webapp商品
			"""
			{
				"name": "买赠和会员价2",
				"promotion_title": "全部买赠啦",
				"detail": "买赠和会员价2的详情",
				"status": "在售",
				"swipe_images": [{
					"url": "/standard_static/test_resource_img/hangzhou2.jpg"
					}],
				"model": {
					"models": {
						"standard": {
							"price": 100.00
						}
					}
				}
			}
			"""

	#铜牌会员浏览'买赠和会员价2',显示买赠价,不显示会员价
		When bill访问jobs的webapp
		And bill浏览jobs的webapp的'买赠和会员价2'商品页
		Then webapp页面标题为'买赠和会员价2'
		And bill获得webapp商品
			"""
			{
				"name": "买赠和会员价2",
				"promotion_title": "全部买赠啦",
				"detail": "买赠和会员价2的详情",
				"status": "在售",
				"swipe_images": [{
					"url": "/standard_static/test_resource_img/hangzhou2.jpg"
					}],
				"model": {
					"models": {
						"standard": {
							"price": 100.00
						}
					}
				}
			}
			"""
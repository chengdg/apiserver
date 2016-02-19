# watcher: wangxinrui@weizoom.com,benchi@weizoom.com
#editor 新新 2016.2.17


Feature: 自营平台的购物车
"""
	1.每个商品都有属于的'供货商';
	2.包裹下的商品,全部勾选商品,包裹自动勾选;
	勾选包裹,其下所有商品全部自动勾选;
	勾选'全选',所以商品和包裹全部自动勾选;
	3.根据勾选的商品,重新计算合计金额;
	4.失效商品中不按供货商划分;
	5.购物车排序按照添加商品的顺序正序排序,其它按照原来的规则;
	6.限时抢购与买赠置顶;

"""

#特殊说明：jobs表示自营平台，bill，tom表示商家
Background:
	#商家bill的商品信息
	Given bill登录系统
	When bill已添加支付方式
		"""
		[{
			"type": "微信支付",
			"is_active": "启用"
		}, {
			"type": "支付宝",
			"is_active": "启用"
		}, {
			"type": "货到付款",
			"is_active": "启用"
		}]
		"""
	And bill添加邮费配置
		"""
		[{
			"name":"顺丰",
			"first_weight":1,
			"first_weight_price":15.00,
			"added_weight":1,
			"added_weight_price":5.00
		}]
		"""
	And bill选择'顺丰'运费配置
	And bill添加商品分类
		"""
		[{
			"name": "分类1"
		}, {
			"name": "分类2"
		}, {
			"name": "分类3"
		}]
		"""
	And bill已添加商品规格
		"""
		[{
			"name": "颜色",
			"type": "图片",
			"values": [{
				"name": "红色",
				"image": "/standard_static/test_resource_img/icon_color/icon_1.png"
			}, {
				"name": "黄色",
				"image": "/standard_static/test_resource_img/icon_color/icon_5.png"
			}, {
				"name": "蓝色",
				"image": "/standard_static/test_resource_img/icon_color/icon_9.png"
			}]
		},{
			"name": "尺寸",
			"type": "文字",
			"values": [{
				"name": "M"
			}, {
				"name": "S"
			}, {
				"name": "L"
			}]
		}]
		"""
	And bill添加属性模板
		"""
		[{
			"name": "计算机模板",
			"properties": [{
				"name": "CPU",
				"description": "CPU描述"
			}, {
				"name": "内存",
				"description": "内存描述"
			}]
		},{
			"name": "大米模板",
			"properties": [{
				"name": "产地",
				"description": "产地描述"
			}]
		}]
		"""
	And bill已添加商品
		"""
		[{
			"name": "bill无规格商品1",
			"created_at": "2015-07-02 10:20",
			"promotion_title": "促销的东坡肘子",
			"categories": "分类1,分类2,分类3",
			"bar_code":"112233",
			"min_limit":2,
			"is_member_product":"on",
			"model": {
				"models": {
					"standard": {
						"price": 11.12,
						"user_code":"1112",
						"weight": 5.0,
						"stock_type": "无限"
					}
				}
			},
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou1.jpg"
			}, {
				"url": "/standard_static/test_resource_img/hangzhou2.jpg"
			}, {
				"url": "/standard_static/test_resource_img/hangzhou3.jpg"
			}],
			"postage":10.00,
			"pay_interfaces":[{
					"type": "在线支付"
				},{
					"type": "货到付款"
				}],
			"invoice":true,
			"distribution_time":"on",
			"properties": [{
					"name": "CPU",
					"description": "CPU描述"
				}, {
					"name": "内存",
					"description": "内存描述"
				}],
			"detail": "商品描述信息",
			"status": "在售"
		},{
			"name": "bill无规格商品3",
			"created_at": "2015-07-04 10:20",
			"promotion_title": "促销的蜜桔",
			"categories": "",
			"bar_code":"3123456",
			"min_limit":2,
			"is_member_product":"off",
			"model": {
				"models": {
					"standard": {
						"price": 33.12,
						"user_code":"3312",
						"weight":1.0,
						"stock_type": "有限",
						"stocks":100
					}
				}
			},
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou1.jpg"
			}],
			"postage": "顺丰",
			"pay_interfaces":[{
					"type": "在线支付"
				}],
			"invoice":true,
			"distribution_time":"on",
			"properties": [{
					"name": "规格大小",
					"description": "规格大小描述"
				}, {
					"name": "产地",
					"description": "产地描述"
				}],
			"detail": "商品描述信息",
			"status": "在售"
		}]
		"""

	#商家tom的商品信息
	Given tom登录系统
	When tom已添加支付方式
		"""
		[{
			"type": "微信支付",
			"is_active": "启用"
		}]
		"""
	And tom添加邮费配置
		"""
		[{
			"name":"顺丰",
			"first_weight":1,
			"first_weight_price":15.00,
			"added_weight":1,
			"added_weight_price":5.00
		}]
		"""
	And tom选择'顺丰'运费配置
	And tom添加商品分类
		"""
		[{
			"name": "分类1"
		}, {
			"name": "分类2"
		}, {
			"name": "分类3"
		}]
		"""
	And tom已添加商品规格
		"""
		[{
			"name": "颜色",
			"type": "图片",
			"values": [{
				"name": "红色",
				"image": "/standard_static/test_resource_img/icon_color/icon_1.png"
			}, {
				"name": "黄色",
				"image": "/standard_static/test_resource_img/icon_color/icon_5.png"
			}, {
				"name": "蓝色",
				"image": "/standard_static/test_resource_img/icon_color/icon_9.png"
			}]
		},{
			"name": "尺寸",
			"type": "文字",
			"values": [{
				"name": "M"
			}, {
				"name": "S"
			}, {
				"name": "L"
			}]
		}]
		"""
	And tom添加属性模板
		"""
		[{
			"name": "计算机模板",
			"properties": [{
				"name": "CPU",
				"description": "CPU描述"
			}, {
				"name": "内存",
				"description": "内存描述"
			}]
		},{
			"name": "大米模板",
			"properties": [{
				"name": "产地",
				"description": "产地描述"
			}]
		}]
		"""
	And tom已添加商品
		"""
		[{
			"name": "tom无规格商品1",
			"created_at": "2015-07-02 10:20",
			"promotion_title": "促销的东坡肘子",
			"categories": "分类1,分类2,分类3",
			"bar_code":"112233",
			"min_limit":2,
			"is_member_product":"on",
			"model": {
				"models": {
					"standard": {
						"price": 11.12,
						"user_code":"1112",
						"weight": 5.0,
						"stock_type": "无限"
					}
				}
			},
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou1.jpg"
			}, {
				"url": "/standard_static/test_resource_img/hangzhou2.jpg"
			}, {
				"url": "/standard_static/test_resource_img/hangzhou3.jpg"
			}],
			"postage":10.00,
			"pay_interfaces":[{
					"type": "在线支付"
				}],
			"invoice":true,
			"properties": [{
					"name": "CPU",
					"description": "CPU描述"
				}, {
					"name": "内存",
					"description": "内存描述"
				}],
			"detail": "商品描述信息",
			"status": "在售"
		},{
			"name": "tom无规格商品3",
			"created_at": "2015-07-04 10:20",
			"promotion_title": "促销的蜜桔",
			"categories": "",
			"bar_code":"3123456",
			"min_limit":2,
			"is_member_product":"off",
			"model": {
				"models": {
					"standard": {
						"price": 33.12,
						"user_code":"3312",
						"weight":1.0,
						"stock_type": "有限",
						"stocks":100
					}
				}
			},
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou1.jpg"
			}],
			"postage": "顺丰",
			"pay_interfaces":[{
					"type": "在线支付"
				}],
			"invoice":true,
			"properties": [{
					"name": "规格大小",
					"description": "规格大小描述"
				}, {
					"name": "产地",
					"description": "产地描述"
				}],
			"detail": "商品描述信息",
			"status": "在售"
		}]
		"""
	#自营平台jobs登录
	Given jobs登录系统
	When jobs已添加支付方式
		"""
		[{
			"type": "微信支付",
			"is_active": "启用"
		}, {
			"type": "支付宝",
			"is_active": "启用"
		}, {
			"type": "货到付款",
			"is_active": "启用"
		}]
		"""
	And jobs已添加商品分类
		"""
		[{
			"name": "分组1"
		},{
			"name": "分组2"
		},{
			"name": "分组3"
		}]
		"""
	Then jobs获得商品池商品列表
		"""
		[{
			"name": "tom无规格商品3",
			"user_code": "3312",
			"supplier":"tom商家",
			"stocks":100,
			"status":"未选择",
			"sync_time":"",
			"actions": ["放入待售"]
		},{
			"name": "bill无规格商品3",
			"user_code":"3312",
			"supplier":"bill商家",
			"stocks":100,
			"status":"未选择",
			"sync_time":"",
			"actions": ["放入待售"]
		},{
			"name": "tom无规格商品1",
			"user_code":"1112",
			"supplier":"tom商家",
			"stock_type": "无限",
			"status":"未选择",
			"sync_time":"",
			"actions": ["放入待售"]
		},{
			"name": "bill无规格商品1",
			"user_code":"1112",
			"supplier":"bill商家",
			"stock_type": "无限",
			"status":"未选择",
			"sync_time":"",
			"actions": ["放入待售"]
		}]
		"""

#自营平台把商品从商品池放入待售商品列表，获取待售商品列表

	When jobs将商品'bill无规格商品1'放入待售于'2015-08-02 10:30'
	And jobs将商品'tom无规格商品1'放入待售于'2015-08-02 11:30'
	And jobs批量将商品放入待售于'2015-08-02 12:30'
		"""
		[{
			"name": "tom无规格商品3"
		}, {
			"name": "bill无规格商品3"
		}]
		"""
	Then jobs获得商品池商品列表
		"""
		[{
			"name": "tom无规格商品3",
			"user_code": "3312",
			"supplier":"tom商家",
			"stocks":100,
			"status":"已选择",
			"sync_time":"2015-08-02 12:30",
			"actions": ["无更新"]
		},{
			"name": "bill无规格商品3",
			"user_code":"3312",
			"supplier":"bill商家",
			"stocks":100,
			"status":"已选择",
			"sync_time":"2015-08-02 12:30",
			"actions": ["无更新"]
		},{
			"name": "tom无规格商品1",
			"user_code":"1112",
			"supplier":"tom商家",
			"stock_type": "无限",
			"status":"已选择",
			"sync_time":"2015-08-02 11:30",
			"actions": ["无更新"]
		},{
			"name": "bill无规格商品1",
			"user_code":"1112",
			"supplier":"bill商家",
			"stock_type": "无限",
			"status":"已选择",
			"sync_time":"2015-08-02 10:30",
			"actions": ["无更新"]
		}]
		"""
	Then jobs能获得'待售'商品列表
		"""
		[{
			"name": "tom无规格商品3",
			"user_code": "3312",
			"supplier":"tom商家",
			"categories": "",
			"price": 33.12,
			"stocks":100,
			"sales": 0,
			"sync_time":"2015-08-02 12:30",
			"actions": ["修改", "上架", "彻底删除"]
		},{
			"name": "bill无规格商品3",
			"user_code":"3312",
			"supplier":"bill商家",
			"categories": "",
			"price": 33.12,
			"stocks":100,
			"sales": 0,
			"sync_time":"2015-08-02 12:30",
			"actions": ["修改", "上架", "彻底删除"]
		},{
			"name": "tom无规格商品1",
			"user_code":"1112",
			"supplier":"tom商家",
			"categories": "",
			"price": 11.12,
			"stock_type": "无限",
			"sales": 0,
			"sync_time":"2015-08-02 11:30",
			"actions": ["修改", "上架", "彻底删除"]
		},{
			"name": "bill无规格商品1",
			"user_code":"1112",
			"supplier":"bill商家",
			"categories": "",
			"price": 11.12,
			"stock_type": "无限",
			"sales": 0,
			"sync_time":"2015-08-02 10:30",
			"actions": ["修改", "上架", "彻底删除"]
		}]
		"""
	When jobs批量上架商品
		"""
		[
			"tom无规格商品3", 
			"bill无规格商品3",
			"tom无规格商品1", 
			"bill无规格商品1"
		]
		"""
	Then jobs能获得'在售'商品列表
		"""
		[{
			"name": "tom无规格商品3",
			"user_code": "3312",
			"supplier":"tom商家",
			"categories": "",
			"price": 33.12,
			"stocks":100,
			"sales": 0,
			"sync_time":"2015-08-02 12:30",
			"actions": ["修改", "下架", "彻底删除"]
		},{
			"name": "bill无规格商品3",
			"user_code":"3312",
			"supplier":"bill商家",
			"categories": "",
			"price": 33.12,
			"stocks":100,
			"sales": 0,
			"sync_time":"2015-08-02 12:30",
			"actions": ["修改", "下架", "彻底删除"]
		},{
			"name": "tom无规格商品1",
			"user_code":"1112",
			"supplier":"tom商家",
			"categories": "",
			"price": 11.12,
			"stock_type": "无限",
			"sales": 0,
			"sync_time":"2015-08-02 11:30",
			"actions": ["修改", "下架", "彻底删除"]
		},{
			"name": "bill无规格商品1",
			"user_code":"1112",
			"supplier":"bill商家",
			"categories": "",
			"price": 11.12,
			"stock_type": "无限",
			"sales": 0,
			"sync_time":"2015-08-02 10:30",
			"actions": ["修改", "下架", "彻底删除"]
		}]
		"""
#自营平台创建商品

	And jobs已添加供货商
		"""
		[{
			"name": "土小宝",
			"responsible_person": "宝宝",
			"supplier_tel": "13811223344",
			"supplier_address": "北京市海淀区泰兴大厦",
			"remark": "备注卖花生油"
		}]
		"""
	And jobs已添加商品
		"""
		[{
			"status": "在售"
			"name": "jobs商品1",
			"supplier":"土小宝",
			"purchase_price": 9.00,
			"created_at": "2015-08-03 12:30",
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"weight": 5.0,
						"stock_type": "无限"
					}
				}
			}
		},{
			"status": "在售"
			"name": "jobs商品2",
			"supplier":"土小宝",
			"purchase_price": 19.00,
			"created_at": "2015-08-04 12:30",
			"model": {
				"models": {
					"standard": {
						"price": 200.00,
						"weight": 5.0,
						"stock_type": "无限"
					}
				}
			}
		}]
		"""
	Then jobs能获得'在售'商品列表
		"""
		[{
			"name": "jobs商品2",
			"user_code": "",
			"supplier":"土小宝",
			"categories": "",
			"price": 200.00,
			"stock_type": "无限",
			"sales": 0,
			"sync_time":"2015-08-04 12:30",
			"actions": ["修改", "下架", "彻底删除"]
		},{
			"name": "jobs商品1",
			"user_code": "",
			"supplier":"土小宝",
			"categories": "",
			"price": 100.00,
			"stock_type": "无限",
			"sales": 0,
			"sync_time":"2015-08-03 12:30",
			"actions": ["修改", "下架", "彻底删除"]
		},{
			"name": "tom无规格商品3",
			"user_code": "3312",
			"supplier":"tom商家",
			"categories": "",
			"price": 33.12,
			"stocks":100,
			"sales": 0,
			"sync_time":"2015-08-02 12:30",
			"actions": ["修改", "下架", "彻底删除"]
		},{
			"name": "bill无规格商品3",
			"user_code":"3312",
			"supplier":"bill商家",
			"categories": "",
			"price": 33.12,
			"stocks":100,
			"sales": 0,
			"sync_time":"2015-08-02 12:30",
			"actions": ["修改", "下架", "彻底删除"]
		},{
			"name": "tom无规格商品1",
			"user_code":"1112",
			"supplier":"tom商家",
			"categories": "",
			"price": 11.12,
			"stock_type": "无限",
			"sales": 0,
			"sync_time":"2015-08-02 11:30",
			"actions": ["修改", "下架", "彻底删除"]
		},{
			"name": "bill无规格商品1",
			"user_code":"1112",
			"supplier":"bill商家",
			"categories": "",
			"price": 11.12,
			"stock_type": "无限",
			"sales": 0,
			"sync_time":"2015-08-02 10:30",
			"actions": ["修改", "下架", "彻底删除"]
		}]
		"""
	And tom1关注jobs的公众号

Scenario:1 加入商品到购物车并且按照商品添加购物车中的正序显示
	1.tom1添加商品到购物车显示供货商到
	When tom1访问jobs的webapp
	And tom1加入jobs的商品到购物车
		"""
		[{
			"supplier": "土小宝",
			"name": "jobs商品1",
			"count": 1
		}]
		"""
	
	Then tom1能获得购物车
		"""
		{
			"product_groups": [{
				"promotion": null,
				"can_use_promotion": false,
				"products": [{
					"土小宝": [{
					"name": "jobs商品1",
					"price": 100,
					"count": 1
					}]
				}]
			}],
			"invalid_products": []
		}
		"""

	And tom1加入jobs的商品到购物车
		"""
		[{
			"supplier": "土小宝",
			"name": "jobs商品2",
			"count": 1
		}]
		"""
	Then tom1能获得购物车
		"""
		{
			"product_groups": [{
				"promotion": null,
				"can_use_promotion": false,
				"products": [{
					"土小宝": [{
					"name": "jobs商品1",
					"price": 100,
					"count": 1
					},{
					"name": "jobs商品2",
					"price": 100,
					"count": 1
					}]
				}]
			}],
			"invalid_products": []
		}
		"""
	And tom1加入jobs的商品到购物车
		"""
		[{
			"supplier": "bill商家",
			"name": "bill无规格商品3",
			"count": 1
		}]
		"""
	Then tom1能获得购物车
		"""
		{
			"product_groups": [{
				"promotion": null,
				"can_use_promotion": false,
				"products": [{
					"土小宝": [{
					"name": "jobs商品1",
					"price": 100,
					"count": 1
					},{
					"name": "jobs商品2",
					"price": 100,
					"count": 1
					}],
					"bill商家": [{
					"name": "bill无规格商品3",
					"price": 33.12,
					"count": 1
					}]
				}]
			}],
			"invalid_products": []
		}
		"""
	And tom1加入jobs的商品到购物车
		"""
		[{
			"supplier": "tom商家",
			"name": "tom无规格商品1",
			"count": 1
		}]
		"""

	Then tom1能获得购物车
		"""
		{
			"product_groups": [{
				"promotion": null,
				"can_use_promotion": false,
				"products": [{
					"土小宝": [{
					"name": "jobs商品1",
					"price": 100,
					"count": 1
					},{
					"name": "jobs商品2",
					"price": 100,
					"count": 1
					}],
					"bill商家": [{
					"name": "bill无规格商品3",
					"price": 33.12,
					"count": 1
					}],
					"tom商家": [{
					"name": "tom无规格商品1",
					"price": 11.12,
					"count": 1
					}]
				}]
			}],
			"invalid_products": []
		}
		"""
Scenario:2 限时抢购与买赠置顶
	1.限时排第一,买赠排第二,其它还按原有规则

	Given jobs登录系统
	When jobs创建限时抢购活动
		"""
		{
			"name": "jobs商品1限时抢购",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "jobs商品1",
			"member_grade": "全部",
			"count_per_purchase": 2,
			"promotion_price": 50.00
		}
		"""
	When jobs创建买赠活动
		"""
		[{
			"name": "bill无规格商品3买一赠一",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "bill无规格商品3",
			"premium_products": [{
				"name": "tom无规格商品1",
				"count": 1
			}],
			"count": 1,
			"member_grade":"全部",
			"is_enable_cycle_mode": true
		}]
		"""
	When tom1访问jobs的webapp
	And tom1加入jobs的商品到购物车
		"""
		[{
			"supplier": "土小宝",
			"name": "jobs商品2",
			"count": 1
		}]
		"""
	
	Then tom1能获得购物车
		"""
		{
			"product_groups": [{
				"promotion": null,
				"can_use_promotion": false,
				"products": [{
					"土小宝": [{
					"name": "jobs商品2",
					"price": 200,
					"count": 1
					}]
				}]
			}],
			"invalid_products": []
		}
		"""
	And tom1加入jobs的商品到购物车
		"""
		[{
			"supplier": "土小宝",
			"name": "jobs商品1",
			"count": 1
		}]
		"""
	Then tom1能获得购物车
		"""
		{
			"product_groups": [{
				"promotion": null,
				"can_use_promotion": false,
				"products": [{
					"土小宝": [{
					"name": "jobs商品1",
					"price": 50,
					"count": 1
					}],
					"土小宝": [{
					"name": "jobs商品2",
					"price": 200,
					"count": 1
					}]
				}]
			}],
			"invalid_products": []
		}
		"""
	And tom1加入jobs的商品到购物车
		"""
		[{
			"supplier": "bill商家",
			"name": "bill无规格商品3",
			"count": 1
		}]
		"""
	Then tom1能获得购物车
		"""
		{
			"product_groups": [{
				"promotion": null,
				"can_use_promotion": false,
				"products": [{
					"土小宝": [{
					"name": "jobs商品1",
					"price": 50,
					"count": 1
					}],
					"bill商家": [{
					"name": "bill无规格商品3",
					"price": 33.12,
					"count": 1
					}],
					"土小宝": [{
					"name": "jobs商品2",
					"price": 200,
					"count": 1
					}]
				}]
			}],
			"invalid_products": []
		}
		"""


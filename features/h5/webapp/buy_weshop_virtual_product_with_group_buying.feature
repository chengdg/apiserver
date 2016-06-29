# watcher: benchi@weizoom.com, zhangsanxiang@weizoom.com
#_author_:张三香 2016.06.14

Feature:购买参与团购活动的电子微众卡或虚拟商品

Background:
	Given 重置'weapp'的bdd环境
	Given 设置jobs为自营平台账号::weapp
	Given jobs登录系统::weapp
	And jobs已添加商品分类::weapp
		"""
		[{
			"name": "分类1"
		},{
			"name": "分类2"
		}]
		"""
	And jobs已添加供货商::weapp
		"""
		[{
			"name": "电子微众",
			"responsible_person": "张大众",
			"supplier_tel": "15211223344",
			"supplier_address": "北京市海淀区海淀科技大厦",
			"remark": "备注"
		},{
			"name": "虚拟a",
			"responsible_person": "许稻香",
			"supplier_tel": "15311223344",
			"supplier_address": "北京市朝阳区稻香大厦",
			"remark": ""
		}]
		"""
	And jobs已添加支付方式::weapp
		"""
		[{
			"type": "货到付款",
			"is_active": "启用"
		},{
			"type": "微信支付",
			"is_active": "启用"
		},{
			"type": "支付宝",
			"is_active": "启用"
		}]
		"""
	When jobs开通使用微众卡权限::weapp
	When jobs添加支付方式::weapp
		"""
		[{
			"type": "微众卡支付",
			"description": "我的微众卡支付",
			"is_active": "启用"
		}]
		"""
	Given jobs已添加商品::weapp
		"""
		[{
			"name":"电子微众卡1",
			"product_type":"电子微众卡",
			"supplier": "电子微众",
			"purchase_price": 9.00,
			"promotion_title": "10元通用卡",
			"categories": "分类1,分类2",
			"bar_code":"112233",
			"min_limit":1,
			"is_member_product":"off",
			"price": 10.00,
			"weight": 1.0,
			"stock_type": "有限",
			"stocks": 0,
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou1.jpg"
			},{
				"url": "/standard_static/test_resource_img/hangzhou2.jpg"
			}],
			"postage":0.00,
			"pay_interfaces":
				[{
					"type": "在线支付"
				},{
					"type": "货到付款"
				}],
			"detail":"电子微众卡1的详情",
			"status":"在售"
		},{
			"name": "虚拟商品2",
			"product_type":"虚拟商品",
			"supplier": "虚拟a",
			"purchase_price": 19.00,
			"promotion_title": "虚拟商品2",
			"categories": "分类2",
			"bar_code":"212233",
			"min_limit":1,
			"is_member_product":"off",
			"price": 20.00,
			"weight": 1.0,
			"stock_type": "有限",
			"stocks": 0,
			"swipe_images": [{
				"url": "/standard_static/test_resource_img/hangzhou1.jpg"
			}],
			"postage":0.00,
			"pay_interfaces":
				[{
					"type": "在线支付"
				},{
					"type": "货到付款"
				}],
			"detail":"虚拟商品2的详情",
			"status":"在售"
		}]
		"""
	When jobs新建福利卡券活动::weapp
		"""
		[{
			"product":
				{
					"name":"电子微众卡1",
					"bar_code":"112233",
					"price":10.00
				},
			"activity_name":"电子卡活动1",
			"card_start_date":"今天",
			"card_end_date":"30天后",
			"cards":
				[{
					"id":"0000001",
					"password":"1234567"
				},{
					"id":"0000002",
					"password":"2234567"
				},{
					"id":"0000003",
					"password":"3234567"
				}],
			"create_time":"今天"
		},{
			"product":
				{
					"name":"虚拟商品2",
					"bar_code":"212233",
					"price":20.00
				},
			"activity_name":"虚拟活动2",
			"card_start_date":"今天",
			"card_end_date":"30天后",
			"cards":
				[{
					"id":"00000021",
					"password":"1234567"
				},{
					"id":"0000022",
					"password":"2234567"
				},{
					"id":"0000023",
					"password":"3234567"
				}],
			"create_time":"今天"
		}]
		"""
	When jobs添加微信证书::weapp
	And jobs新建团购活动::weapp
		"""
		[{
			"group_name":"电子卡团购1",
			"start_date":"今天",
			"end_date":"2天后",
			"product_name":"电子微众卡1",
			"group_dict":{
				"0":{
					"group_type":"3",
					"group_days":"1",
					"group_price":"0.01"
					}
			},
			"ship_date":"20",
			"product_counts":"100",
			"material_image":"1.jpg",
			"share_description":"团购分享描述"
		}, {
			"group_name":"虚拟商品团购2",
			"start_date":"今天",
			"end_date":"3天后",
			"product_name":"虚拟商品2",
			"group_dict":{
				"0":{
					"group_type":"3",
					"group_days":"2",
					"group_price":"10.00"
					},
				"1":{
					"group_type":"5",
					"group_days":"2",
					"group_price":"9.99"
				}
			},
			"ship_date":"20",
			"product_counts":"100",
			"material_image":"1.jpg",
			"share_description":"团购分享描述"
		}]
		"""
	When jobs开启团购活动'电子卡团购1'::weapp
	When jobs开启团购活动'虚拟商品团购2'::weapp
	When bill关注jobs的公众号
	When tom关注jobs的公众号
	When jack关注jobs的公众号

@weshop @nj_group
Scenario:1 团购未成功的待发货订单，不自动发货
	#电子微众卡参与团购活动
		When bill访问jobs的webapp
		When bill参加jobs的团购活动"电子卡团购1"进行开团::weapp
			"""
			{
				"group_name": "电子卡团购1",
				"group_leader": "bill",
				"group_dict":
					{
						"group_type":"3",
						"group_days":"1",
						"group_price":"0.01"
					},
				"products": {
					"name": "电子微众卡1"
				}
			}
			"""
		When bill提交团购订单
			"""
			{
				"ship_name": "bill",
				"ship_tel": "13811223344",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦",
				"pay_type":"微信支付"
			}
			"""
		When bill使用支付方式'微信支付'进行支付
		When bill访问jobs的webapp
		Then bill获得微众卡包列表
			"""
			[{
				"can_use":[],
				"not_use":[]
			}]
			"""
	#虚拟商品参与团购活动
			When bill访问jobs的webapp
			When bill参加jobs的团购活动"虚拟商品团购2"进行开团::weapp
				"""
				{
					"group_name": "虚拟商品团购2",
					"group_leader": "bill",
					"group_dict":
						{
							"group_type":"3",
							"group_days":"1",
							"group_price":"10.00"
						},
					"products": {
						"name": "虚拟商品2"
					}
				}
				"""
			When bill提交团购订单
				"""
				{
					"ship_name": "bill",
					"ship_tel": "13811223344",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦",
					"pay_type":"微信支付"
				}
				"""
			When bill使用支付方式'微信支付'进行支付
			When bill访问jobs的webapp
			Then bill获得虚拟卡包列表
				"""
				[{
					"can_use":[],
					"not_use":[]
				}]
				"""

@weshop @nj_group
Scenario:2 团购成功的待发货订单，自动发货
	#电子微众卡参与团购活动
		#001-bill开团购买电子微众卡1
			When bill访问jobs的webapp
			When bill参加jobs的团购活动"电子卡团购1"进行开团::weapp
				"""
				{
					"group_name": "电子卡团购1",
					"group_leader": "bill",
					"group_dict":
						{
							"group_type":"3",
							"group_days":"1",
							"group_price":"0.01"
						},
					"products": {
						"name": "电子微众卡1"
					}
				}
				"""
			When bill提交团购订单
				"""
				{
					"ship_name": "bill",
					"ship_tel": "13811223344",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦",
					"pay_type":"微信支付",
					"order_id":"001"
				}
				"""
			When bill使用支付方式'微信支付'进行支付
		#002-tom参加bill的团
			When tom访问jobs的webapp
			When tom参加bill的团购活动"电子卡团购1"::weapp
				"""
				{
					"group_name": "电子卡团购1",
					"group_leader": "bill",
					"group_dict":
						{
							"group_type":3,
							"group_days":1,
							"group_price":0.01
						},
					"products": {
						"name": "电子微众卡1"
					}
				}
				"""
			When tom提交团购订单
				"""
				{
					"ship_name": "tom",
					"ship_tel": "13811223344",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦",
					"pay_type":"微信支付",
					"order_id":"002"
				}
				"""
			When tom使用支付方式'微信支付'进行支付
		#003-jack参加bill的团
			When jack访问jobs的webapp
			When jack参加bill的团购活动"电子卡团购1"::weapp
				"""
				{
					"group_name": "电子卡团购1",
					"group_leader": "bill",
					"group_dict":
						{
							"group_type":3,
							"group_days":1,
							"group_price":0.01
						},
					"products": {
						"name": "电子微众卡1"
					}
				}
				"""
			When jack提交团购订单
				"""
				{
					"ship_name": "tom",
					"ship_tel": "13811223344",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦",
					"pay_type":"微信支付",
					"order_id":"003"
				}
				"""
			When jack使用支付方式'微信支付'进行支付
		When 系统自动发货
				"""
				[{
					"order_id":"001",
					"weizoom_card":
						[{
							"id":"0000001",
							"password":"1234567"
						}],
					"other_card":[]
				},{
					"order_id":"002",
					"weizoom_card":
						[{
							"id":"0000002",
							"password":"2234567"
						}],
					"other_card":[]
				},{
					"order_id":"003",
					"weizoom_card":
						[{
							"id":"0000003",
							"password":"3234567"
						}],
					"other_card":[]
				}]

				"""
		When bill访问jobs的webapp
		Then bill获得微众卡包列表
			"""
			[{
				"can_use":
					[{
						"card_start_date":"今天",
						"card_end_date":"30天后",
						"card_remain_value":10.00,
						"card_total_value":10.00,
						"id":"0000001",
						"order_date":"今天",
						"source":"商城下单",
						"actions":["查看详情"]
					}],
				"not_use":[]
			}]
			"""
		When tom访问jobs的webapp
		Then tom获得微众卡包列表
			"""
			[{
				"can_use":
					[{
						"card_start_date":"今天",
						"card_end_date":"30天后",
						"card_remain_value":10.00,
						"card_total_value":10.00,
						"id":"0000002",
						"order_date":"今天",
						"source":"商城下单",
						"actions":["查看详情"]
					}],
				"not_use":[]
			}]
			"""
		When jack访问jobs的webapp
		Then jack获得微众卡包列表
			"""
			[{
				"can_use":
					[{
						"card_start_date":"今天",
						"card_end_date":"30天后",
						"card_remain_value":10.00,
						"card_total_value":10.00,
						"id":"0000003",
						"order_date":"今天",
						"source":"商城下单",
						"actions":["查看详情"]
					}],
				"not_use":[]
			}]
			"""
	#虚拟商品参与团购活动
		#011-bill开团购买电子微众卡1
			When bill访问jobs的webapp
			When bill参加jobs的团购活动"虚拟商品团购2"进行开团::weapp
				"""
				{
					"group_name": "虚拟商品团购2",
					"group_leader": "bill",
					"group_dict":
						{
							"group_type":"3",
							"group_days":"1",
							"group_price":"10.00"
						},
					"products": {
						"name": "虚拟商品2"
					}
				}
				"""
			When bill提交团购订单
				"""
				{
					"ship_name": "bill",
					"ship_tel": "13811223344",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦",
					"pay_type":"微信支付",
					"order_id":"011"
				}
				"""
			When bill使用支付方式'微信支付'进行支付
		#012-tom参加bill的团
			When tom访问jobs的webapp
			When tom参加bill的团购活动"虚拟商品团购2"::weapp
				"""
				{
					"group_name": "虚拟商品团购2",
					"group_leader": "bill",
					"group_dict":
						{
							"group_type":3,
							"group_days":1,
							"group_price":10.00
						},
					"products": {
						"name": "虚拟商品2"
					}
				}
				"""
			When tom提交团购订单
				"""
				{
					"ship_name": "tom",
					"ship_tel": "13811223344",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦",
					"pay_type":"微信支付",
					"order_id":"012"
				}
				"""
			When tom使用支付方式'微信支付'进行支付
		#003-jack参加bill的团
			When jack访问jobs的webapp
			When jack参加bill的团购活动"虚拟商品团购2"::weapp
				"""
				{
					"group_name": "虚拟商品团购2",
					"group_leader": "bill",
					"group_dict":
						{
							"group_type":3,
							"group_days":1,
							"group_price":10.00
						},
					"products": {
						"name": "虚拟商品2"
					}
				}
				"""
			When jack提交团购订单
				"""
				{
					"ship_name": "tom",
					"ship_tel": "13811223344",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦",
					"pay_type":"微信支付",
					"order_id":"013"
				}
				"""
			When jack使用支付方式'微信支付'进行支付
		When 系统自动发货
				"""
				[{
					"order_id":"011",
					"weizoom_card":[],
					"other_card":
						[{
							"id":"0000021",
							"password":"1234567"
						}],
				},{
					"order_id":"012",
					"weizoom_card":[],
					"other_card":
						[{
							"id":"0000022",
							"password":"2234567"
						}],
				},{
					"order_id":"013",
					"weizoom_card":[],
					"other_card":
						[{
							"id":"0000023",
							"password":"3234567"
						}],
				}]
				"""
		When bill访问jobs的webapp
		Then bill获得虚拟卡包列表
			"""
			[{
				"can_use":
					[{
						"card_start_date":"今天",
						"card_end_date":"30天后",
						"name":"虚拟商品2",
						"id":"0000021",
						"password":"1234567"
						"get_time":"今天",
						"actions":["查看详情"]
					}],
				"not_use":[]
			}]
			"""
		When tom访问jobs的webapp
		Then tom获得虚拟卡包列表
			"""
			[{
				"can_use":
					[{
						"card_start_date":"今天",
						"card_end_date":"30天后",
						"name":"虚拟商品2",
						"id":"0000022",
						"password":"2234567"
						"get_time":"今天",
						"actions":["查看详情"]
					}],
				"not_use":[]
			}]
			"""
		When jack访问jobs的webapp
		Then jack获得虚拟卡包列表
			"""
			[{
				"can_use":
					[{
						"card_start_date":"今天",
						"card_end_date":"30天后",
						"name":"虚拟商品2",
						"id":"0000023",
						"password":"3234567"
						"get_time":"今天",
						"actions":["查看详情"]
					}],
				"not_use":[]
			}]
			"""
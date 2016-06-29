# watcher: benchi@weizoom.com, zhangsanxiang@weizoom.com
#_author_:张三香 2016.06.14
#_editor_:张三香 2016.06.29

Feature:购买参与买赠活动的电子微众卡或虚拟商品
	"""
		1、电子微众卡和虚拟商品参与买赠活动，不支持买普通商品或实体微众卡赠电子卡或虚拟商品的情况
		2、电子微众卡和虚拟商品参与买赠活动
			2.1买a赠a：
				买a赠a（a为电子微众卡）
				买a赠a（a为虚拟商品）
			2.2买a赠b：
				买电子微众卡a赠电子微众卡b
				买虚拟商品a赠虚拟商品b（a、b同供货商）
				买虚拟商品a赠虚拟商品b（a、b不同供货商）
				买电子微众卡a赠虚拟商品b
			2.3买a赠a、b：
				a、b均为电子微众卡商品
				a、b均虚拟商品
				a电子微众卡、b虚拟商品
				a虚拟商品、b电子微众卡
			2.4买a赠b、c
	"""

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
			"name": "实体微众",
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
		},{
			"name": "虚拟b",
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
			"name":"电子微众卡2",
			"product_type":"电子微众卡",
			"supplier": "电子微众",
			"purchase_price": 19.00,
			"promotion_title": "20元通用卡",
			"categories": "",
			"bar_code":"212233",
			"min_limit":2,
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
			"detail": "电子微众卡2的详情",
			"status": "在售"
		},{
			"name": "虚拟商品3",
			"product_type":"虚拟商品",
			"supplier": "虚拟a",
			"purchase_price": 29.00,
			"promotion_title": "虚拟商品3",
			"categories": "分类2",
			"bar_code":"312233",
			"min_limit":1,
			"is_member_product":"off",
			"price": 30.00,
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
				}],
			"detail":"虚拟商品3的详情",
			"status":"在售"
		},{
			"name": "虚拟商品4",
			"product_type":"虚拟商品",
			"supplier": "虚拟a",
			"purchase_price": 39.00,
			"promotion_title": "虚拟商品4",
			"categories": "分类2",
			"bar_code":"412233",
			"min_limit":1,
			"is_member_product":"off",
			"price": 40.00,
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
				}],
			"detail":"虚拟商品4的详情",
			"status":"在售"
		},{
			"name": "虚拟商品5",
			"product_type":"虚拟商品",
			"supplier": "虚拟b",
			"purchase_price": 49.00,
			"promotion_title": "虚拟商品5",
			"categories": "分类2",
			"bar_code":"512233",
			"min_limit":1,
			"is_member_product":"off",
			"price": 50.00,
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
				}],
			"detail":"虚拟商品5的详情",
			"status":"在售"
		}]
		"""
	When bill关注jobs的公众号
	When jack关注jobs的公众号
	When tom关注jobs的公众号
	When lily关注jobs的公众号

@weshop @preminum_sale
Scenario:1 购买电子微众卡或虚拟商品，买a赠a
	#买a赠a（a为电子微众卡）
	#买a赠a（a为虚拟商品）

	#买电子微众卡赠电子微众卡（电子微众卡1-买1赠1，循环买赠）
		Given jobs登录系统::weapp
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
					},{
						"id":"0000004",
						"password":"4234567"
					},{
						"id":"0000005",
						"password":"5234567"
					}],
				"create_time":"今天"
			}]
			"""
		When jobs创建买赠活动::weapp
			"""
			[{
				"name": "买a赠a",
				"promotion_title":"",
				"start_date": "今天",
				"end_date": "1天后",
				"member_grade": "全部会员",
				"product_name": "电子微众卡1",
				"premium_products": 
					[{
						"name":"电子微众卡1",
						"count": 1
					}],
				"count":1,
				"is_enable_cycle_mode": true
			}]
			"""
		#001-bill买2个电子微众卡1-循环买赠（0000001、0000002/0000003、0000004）
			When bill访问jobs的webapp
			When bill购买jobs的商品
				"""
				[{
					"order_id": "001",
					"date":"今天",
					"products":
						[{
							"name":"电子微众卡1",
							"count": 2
						}],
					"pay_type":"微信支付",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦"
				}]
				"""
			When bill使用支付方式'微信支付'进行支付订单'001'
			When 系统自动发货
				"""
				[{
					"order_id":"001",
					"weizoom_card":
						[{
							"id":"0000001",
							"password":"1234567"
						},{
							"id":"0000002",
							"password":"2234567"
						},{
							"id":"0000003",
							"password":"3234567"
						},{
							"id":"0000004",
							"password":"4234567"
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
							"id":"0000004",
							"order_date":"今天",
							"source":"商城下单",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"card_remain_value":10.00,
							"card_total_value":10.00,
							"id":"0000003",
							"order_date":"今天",
							"source":"商城下单",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"card_remain_value":10.00,
							"card_total_value":10.00,
							"id":"0000002",
							"order_date":"今天",
							"source":"商城下单",
							"actions":["查看详情"]
						},{
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
	#买虚拟商品赠虚拟商品（虚拟商品3-买2赠1，非循环买赠）
		Given jobs登录系统::weapp
		When jobs新建福利卡券活动::weapp
			"""
			[{
				"product":
					{
						"name":"虚拟商品3",
						"bar_code":"312233",
						"price":30.00
					},
				"activity_name":"虚拟活动3",
				"card_start_date":"今天",
				"card_end_date":"30天后",
				"cards":
					[{
						"id":"0000031",
						"password":"1234567"
					},{
						"id":"0000032",
						"password":"2234567"
					},{
						"id":"0000033",
						"password":"3234567"
					},{
						"id":"0000034",
						"password":"4234567"
					},{
						"id":"0000035",
						"password":"5234567"
					},{
						"id":"0000036",
						"password":"6234567"
					}],
				"create_time":"今天"
			}]
			"""
		When jobs创建买赠活动::weapp
			"""
			[{
				"name": "买a赠a",
				"promotion_title":"",
				"start_date": "今天",
				"end_date": "1天后",
				"member_grade": "全部会员",
				"product_name": "虚拟商品3",
				"premium_products": 
					[{
						"name":"虚拟商品3",
						"count": 1
					}],
				"count":2,
				"is_enable_cycle_mode": false
			}]
			"""
		#002-tom买1个虚拟商品3-不满足买赠条件（0000031）
			When tom访问jobs的webapp
			When tom购买jobs的商品
				"""
				[{
					"order_id": "002",
					"date":"今天",
					"products":
						[{
							"name":"虚拟商品3",
							"count": 1
						}],
					"pay_type":"微信支付",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦"
				}]
				"""
			When tom使用支付方式'微信支付'进行支付订单'002'
			When 系统自动发货
				"""
				[{
					"order_id":"002",
					"weizoom_card":[],
					"other_card":
						[{
							"id":"0000031",
							"password":"1234567"
						}]
				}]
				"""
		#003-tom买4个虚拟商品3-满足买赠条件，不循环买赠（0000032-0000036）
			When tom访问jobs的webapp
			When tom购买jobs的商品
				"""
				[{
					"order_id": "003",
					"date":"今天",
					"products":
						[{
							"name":"虚拟商品3",
							"count": 4
						}],
					"pay_type":"微信支付",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦"
				}]
				"""
			When tom使用支付方式'微信支付'进行支付订单'003'
			When 系统自动发货
				"""
				[{
					"order_id":"003",
					"weizoom_card":[],
					"other_card":
						[{
							"id":"0000032",
							"password":"2234567"
						},{
							"id":"0000033",
							"password":"3234567"
						},{
							"id":"0000034",
							"password":"4234567"
						},{
							"id":"0000035",
							"password":"5234567"
						},{
							"id":"0000036",
							"password":"6234567"
						}]
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
							"name":"虚拟商品3",
							"id":"0000036",
							"password":"6234567"
							"get_time":"今天",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品3",
							"id":"0000035",
							"password":"5234567"
							"get_time":"今天",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品3",
							"id":"0000034",
							"password":"4234567"
							"get_time":"今天",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品3",
							"id":"0000033",
							"password":"3234567"
							"get_time":"今天",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品3",
							"id":"0000032",
							"password":"2234567"
							"get_time":"今天",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品3",
							"id":"0000031",
							"password":"1234567"
							"get_time":"今天",
							"actions":["查看详情"]
						}],
					"not_use":[]
					
				}]
				"""

@weshop @preminum_sale
Scenario:2 购买电子微众卡或虚拟商品，买a赠b
	#买电子微众卡a赠电子微众卡b
	#买虚拟商品a赠虚拟商品b（a、b同供货商）
	#买虚拟商品a赠虚拟商品b（a、b不同供货商）
	#买电子微众卡a赠虚拟商品b

	Given jobs登录系统::weapp
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
					}],
				"create_time":"今天"
			},{
				"product":
					{
						"name":"电子微众卡2",
						"bar_code":"212233",
						"price":20.00
					},
				"activity_name":"电子卡活动2",
				"card_start_date":"今天",
				"card_end_date":"30天后",
				"cards":
					[{
						"id":"0000021",
						"password":"1234567"
					},{
						"id":"0000022",
						"password":"2234567"
					},{
						"id":"0000023",
						"password":"3234567"
					},{
						"id":"0000024",
						"password":"4234567"
					}],
				"create_time":"今天"
			},{
				"product":
					{
						"name":"虚拟商品3",
						"bar_code":"312233",
						"price":30.00
					},
				"activity_name":"虚拟活动3",
				"card_start_date":"今天",
				"card_end_date":"30天后",
				"cards":
					[{
						"id":"0000031",
						"password":"1234567"
					},{
						"id":"0000032",
						"password":"2234567"
					}],
				"create_time":"今天"
			},{
				"product":
					{
						"name":"虚拟商品4",
						"bar_code":"412233",
						"price":40.00
					},
				"activity_name":"虚拟活动4",
				"card_start_date":"今天",
				"card_end_date":"30天后",
				"cards":
					[{
						"id":"0000041",
						"password":"1234567"
					},{
						"id":"0000042",
						"password":"2234567"
					},{
						"id":"0000043",
						"password":"3234567"
					},{
						"id":"0000044",
						"password":"4234567"
					},{
						"id":"0000045",
						"password":"5234567"
					},{
						"id":"0000046",
						"password":"6234567"
					},{
						"id":"0000047",
						"password":"7234567"
					}],
				"create_time":"今天"
			},{
				"product":
					{
						"name":"虚拟商品5",
						"bar_code":"512233",
						"price":50.00
					},
				"activity_name":"虚拟活动5",
				"card_start_date":"今天",
				"card_end_date":"30天后",
				"cards":
					[{
						"id":"0000051",
						"password":"1234567"
					},{
						"id":"0000052",
						"password":"2234567"
					},{
						"id":"0000053",
						"password":"3234567"
					},{
						"id":"0000054",
						"password":"4234567"
					}],
				"create_time":"今天"
			}]
			"""
	#买'电子微众卡1'赠'电子微众卡2'-买1赠1，非循环买赠
		Given jobs登录系统::weapp
		When jobs创建买赠活动::weapp
			"""
			[{
				"name": "买a赠b活动1",
				"promotion_title":"",
				"start_date": "今天",
				"end_date": "1天后",
				"member_grade": "全部会员",
				"product_name": "电子微众卡1",
				"premium_products": 
					[{
						"name":"电子微众卡2",
						"count": 1
					}],
				"count":1,
				"is_enable_cycle_mode": false
			}]
			"""
		#001-bill买1个电子微众卡1（0000001/0000021）
			When bill访问jobs的webapp
			When bill购买jobs的商品
				"""
				[{
					"order_id": "001",
					"date":"今天",
					"products":
						[{
							"name":"电子微众卡1",
							"count": 1
						}],
					"pay_type":"微信支付",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦"
				}]
				"""
			When bill使用支付方式'微信支付'进行支付订单'001'
			When 系统自动发货
				"""
				[{
					"order_id":"001",
					"weizoom_card":
						[{
							"id":"0000001",
							"password":"1234567"
						},{
							"id":"0000021",
							"password":"1234567"
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
							"card_remain_value":20.00,
							"card_total_value":20.00,
							"id":"0000021",
							"order_date":"今天",
							"source":"商城下单",
							"actions":["查看详情"]
						},{
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
		#002-bill买1个'电子为卡1+电子微众卡2'（0000002/0000022、0000023）
			When bill访问jobs的webapp
			When bill购买jobs的商品
				"""
				[{
					"order_id": "002",
					"date":"今天",
					"products":
						[{
							"name":"电子微众卡1",
							"count": 1
						},{
							"name":"电子微众卡2",
							"count": 1
						}],
					"pay_type":"微信支付",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦"
				}]
				"""
			When bill使用支付方式'微信支付'进行支付订单'002'
			When 系统自动发货
				"""
				[{
					"order_id":"002",
					"weizoom_card":
						[{
							"id":"0000002",
							"password":"2234567"
						},{
							"id":"0000022",
							"password":"2234567"
						},{
							"id":"0000023",
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
							"card_remain_value":20.00,
							"card_total_value":20.00,
							"id":"0000023",
							"order_date":"今天",
							"source":"商城下单",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"card_remain_value":20.00,
							"card_total_value":20.00,
							"id":"0000022",
							"order_date":"今天",
							"source":"商城下单",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"card_remain_value":10.00,
							"card_total_value":10.00,
							"id":"0000002",
							"order_date":"今天",
							"source":"商城下单",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"card_remain_value":20.00,
							"card_total_value":20.00,
							"id":"0000021",
							"order_date":"今天",
							"source":"商城下单",
							"actions":["查看详情"]
						},{
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
	#买'虚拟商品3'赠'虚拟商品4'（同供货商）-买1赠2，非循环买赠
		Given jobs登录系统::weapp
		When jobs创建买赠活动::weapp
			"""
			[{
				"name": "买a赠b活动2",
				"promotion_title":"",
				"start_date": "今天",
				"end_date": "1天后",
				"member_grade": "全部会员",
				"product_name": "虚拟商品3",
				"premium_products": 
					[{
						"name":"虚拟商品4",
						"count": 2
					}],
				"count":1,
				"is_enable_cycle_mode": false
			}]
			"""
		#003-jack买1个'虚拟商品3'（0000031/0000041、0000042）
			When jack访问jobs的webapp
			When jack购买jobs的商品
				"""
				[{
					"order_id": "003",
					"date":"今天",
					"products":
						[{
							"name":"虚拟商品3",
							"count": 1
						}],
					"pay_type":"微信支付",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦"
				}]
				"""
			When bill使用支付方式'微信支付'进行支付订单'003'
			When 系统自动发货
				"""
				[{
					"order_id":"003",
					"weizoom_card":[],
					"other_card":
						[{
							"id":"0000031",
							"password":"1234567"
						},{
							"id":"0000041",
							"password":"1234567"
						},{
							"id":"0000042",
							"password":"2234567"
						}]
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
							"name":"虚拟商品4",
							"id":"0000042",
							"password":"2234567"
							"get_time":"今天",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品4",
							"id":"0000041",
							"password":"1234567"
							"get_time":"今天",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品3",
							"id":"0000031",
							"password":"1234567"
							"get_time":"今天",
							"actions":["查看详情"]
						}],
					"not_use":[]
				}]
				"""
		#004-jack买1个'虚拟商品3+虚拟商品4'（0000032/0000043、0000044、0000045）
			When jack访问jobs的webapp
			When jack购买jobs的商品
				"""
				[{
					"order_id": "004",
					"date":"今天",
					"products":
						[{
							"name":"虚拟商品3",
							"count": 1
						},{
							"name":"虚拟商品4",
							"count": 1
						}],
					"pay_type":"微信支付",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦"
				}]
				"""
			When jack使用支付方式'微信支付'进行支付订单'004'
			When 系统自动发货
				"""
				[{
					"order_id":"004",
					"weizoom_card":[],
					"other_card":
						[{
							"id":"0000032",
							"password":"2234567"
						},{
							"id":"0000043",
							"password":"3234567"
						},{
							"id":"0000044",
							"password":"4234567"
						},{
							"id":"0000045",
							"password":"5234567"
						}]
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
							"name":"虚拟商品4",
							"id":"0000045",
							"password":"5234567"
							"get_time":"今天",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品4",
							"id":"0000044",
							"password":"4234567"
							"get_time":"今天",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品4",
							"id":"0000043",
							"password":"3234567"
							"get_time":"今天",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品3",
							"id":"0000032",
							"password":"2234567"
							"get_time":"今天",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品4",
							"id":"0000042",
							"password":"2234567"
							"get_time":"今天",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品4",
							"id":"0000041",
							"password":"1234567"
							"get_time":"今天",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品3",
							"id":"0000031",
							"password":"1234567"
							"get_time":"今天",
							"actions":["查看详情"]
						}],
					"not_use":[]
				}]
				"""
	#买'虚拟商品4'赠'虚拟商品5'（不同供货商）-买1赠1，循环买赠
		Given jobs登录系统::weapp
		When jobs创建买赠活动::weapp
			"""
			[{
				"name": "买a赠b活动3",
				"promotion_title":"",
				"start_date": "今天",
				"end_date": "1天后",
				"member_grade": "全部会员",
				"product_name": "虚拟商品4",
				"premium_products": 
					[{
						"name":"虚拟商品5",
						"count": 1
					}],
				"count":1,
				"is_enable_cycle_mode": true
			}]
			"""
		#005-tom买1个'虚拟商品4'（0000046/0000051）
			When tom访问jobs的webapp
			When tom购买jobs的商品
				"""
				[{
					"order_id": "005",
					"date":"今天",
					"products":
						[{
							"name":"虚拟商品4",
							"count": 1
						}],
					"pay_type":"微信支付",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦"
				}]
				"""
			When tom使用支付方式'微信支付'进行支付订单'005'
			When 系统自动发货
				"""
				[{
					"order_id":"005",
					"weizoom_card":[],
					"other_card":
						[{
							"id":"0000046",
							"password":"6234567"
						},{
							"id":"0000051",
							"password":"1234567"
						}]
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
							"name":"虚拟商品5",
							"id":"0000051",
							"password":"1234567"
							"get_time":"今天",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品4",
							"id":"0000046",
							"password":"6234567"
							"get_time":"今天",
							"actions":["查看详情"]
						}],
					"not_use":[]
				}]
				"""
		#006-tom买1个'虚拟商品4+虚拟商品5'（0000047/0000052、0000053）
			When tom访问jobs的webapp
			When tom购买jobs的商品
				"""
				[{
					"order_id": "006",
					"date":"今天",
					"products":
						[{
							"name":"虚拟商品4",
							"count": 1
						},{
							"name":"虚拟商品5",
							"count": 1
						}],
					"pay_type":"微信支付",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦"
				}]
				"""
			When tom使用支付方式'微信支付'进行支付订单'006'
			When 系统自动发货
				"""
				[{
					"order_id":"006",
					"weizoom_card":[],
					"other_card":
						[{
							"id":"0000047",
							"password":"7234567"
						},{
							"id":"0000052",
							"password":"2234567"
						},{
							"id":"0000053",
							"password":"3234567"
						}]
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
							"name":"虚拟商品5",
							"id":"0000053",
							"password":"3234567"
							"get_time":"今天",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品5",
							"id":"0000052",
							"password":"2234567"
							"get_time":"今天",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品4",
							"id":"0000047",
							"password":"7234567"
							"get_time":"今天",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品5",
							"id":"0000051",
							"password":"1234567"
							"get_time":"今天",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品4",
							"id":"0000046",
							"password":"6234567"
							"get_time":"今天",
							"actions":["查看详情"]
						}],
					"not_use":[]
				}]
				"""
	#买'电子微众卡2'赠'虚拟商品5'-买1赠1，非循环买赠
		Given jobs登录系统::weapp
		When jobs创建买赠活动::weapp
			"""
			[{
				"name": "买a赠b活动4",
				"promotion_title":"",
				"start_date": "今天",
				"end_date": "1天后",
				"member_grade": "全部会员",
				"product_name": "电子微众卡卡2",
				"premium_products": 
					[{
						"name":"虚拟商品5",
						"count": 1
					}],
				"count":1,
				"is_enable_cycle_mode": false
			}]
			"""
		#007-lily买1个'电子微众卡卡2'（0000024/0000054）
			When lily访问jobs的webapp
			When lily购买jobs的商品
				"""
				[{
					"order_id": "007",
					"date":"今天",
					"products":
						[{
							"name":"电子微众卡2",
							"count": 1
						}],
					"pay_type":"微信支付",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦"
				}]
				"""
			When lily使用支付方式'微信支付'进行支付订单'007'
			When 系统自动发货
				"""
				[{
					"order_id":"007",
					"weizoom_card":
						[{
							"id":"0000024",
							"password":"4234567"
						}],
					"other_card":
						[{
							"id":"0000054",
							"password":"4234567"
						}]
				}]
				"""
			When lily访问jobs的webapp
			Then lily获得微众卡包列表
				"""
				[{
					"can_use":
						[{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"card_remain_value":20.00,
							"card_total_value":20.00,
							"id":"0000024",
							"order_date":"今天",
							"source":"商城下单",
							"actions":["查看详情"]
						}],
					"not_use":[]
				}]
				"""
			And lily获得虚拟卡包列表
				"""
				[{
					"can_use":
						[{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品5",
							"id":"0000054",
							"password":"4234567"
							"get_time":"今天",
							"actions":["查看详情"]
						}],
					"not_use":[]
				}]
				"""

@weshop @preminum_sale
Scenario:3 购买电子微众卡或虚拟商品，买a赠a和b
	#a、b均为电子微众卡商品
	#a、b均虚拟商品
	#a电子微众卡、b虚拟商品
	#a虚拟商品、b电子微众卡

	Given jobs登录系统::weapp
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
					},{
						"id":"0000004",
						"password":"4234567"
					},{
						"id":"0000005",
						"password":"5234567"
					},{
						"id":"0000006",
						"password":"6234567"
					}],
				"create_time":"今天"
			},{
				"product":
					{
						"name":"电子微众卡2",
						"bar_code":"212233",
						"price":20.00
					},
				"activity_name":"电子卡活动2",
				"card_start_date":"今天",
				"card_end_date":"30天后",
				"cards":
					[{
						"id":"0000021",
						"password":"1234567"
					},{
						"id":"0000022",
						"password":"2234567"
					},{
						"id":"0000023",
						"password":"3234567"
					},{
						"id":"0000024",
						"password":"4234567"
					},{
						"id":"0000025",
						"password":"5234567"
					}],
				"create_time":"今天"
			},{
				"product":
					{
						"name":"虚拟商品3",
						"bar_code":"312233",
						"price":30.00
					},
				"activity_name":"虚拟活动3",
				"card_start_date":"今天",
				"card_end_date":"30天后",
				"cards":
					[{
						"id":"0000031",
						"password":"1234567"
					},{
						"id":"0000032",
						"password":"2234567"
					},{
						"id":"0000033",
						"password":"3234567"
					},{
						"id":"0000034",
						"password":"4234567"
					},{
						"id":"0000035",
						"password":"5234567"
					},{
						"id":"0000036",
						"password":"6234567"
					}],
				"create_time":"今天"
			},{
				"product":
					{
						"name":"虚拟商品4",
						"bar_code":"412233",
						"price":40.00
					},
				"activity_name":"虚拟活动4",
				"card_start_date":"今天",
				"card_end_date":"30天后",
				"cards":
					[{
						"id":"0000041",
						"password":"1234567"
					},{
						"id":"0000042",
						"password":"2234567"
					},{
						"id":"0000043",
						"password":"3234567"
					}],
				"create_time":"今天"
			}]
			"""
	#买'电子微众卡1'，赠'电子微众卡1'和'电子微众卡2'（买1赠1和1-循环买赠）
		Given jobs登录系统::weapp
		When jobs创建买赠活动::weapp
			"""
			[{
				"name": "买a赠a和b活动1",
				"promotion_title":"",
				"start_date": "今天",
				"end_date": "1天后",
				"member_grade": "全部会员",
				"product_name": "电子微众卡1",
				"premium_products": 
					[{
						"name":"电子微众卡1",
						"count": 1
					},{
						"name":"电子微众卡2",
						"count": 1
					}],
				"count":1,
				"is_enable_cycle_mode": true
			}]
			"""
		#001-bill买2个电子微众卡1（0000001、0000002/0000003、0000021+0000004、0000022）
			When bill访问jobs的webapp
			When bill购买jobs的商品
				"""
				[{
					"order_id": "001",
					"date":"今天",
					"products":
						[{
							"name":"电子微众卡1",
							"count": 2
						}],
					"pay_type":"微信支付",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦"
				}]
				"""
			When bill使用支付方式'微信支付'进行支付订单'001'
			When 系统自动发货
				"""
				[{
					"order_id":"001",
					"weizoom_card":
						[{
							"id":"0000001",
							"password":"1234567"
						},{
							"id":"0000002",
							"password":"2234567"
						},{
							"id":"0000003",
							"password":"3234567"
						},{
							"id":"0000004",
							"password":"4234567"
						},{
							"id":"0000021",
							"password":"1234567"
						},{
							"id":"0000022",
							"password":"2234567"
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
							"card_remain_value":20.00,
							"card_total_value":20.00,
							"id":"0000022",
							"order_date":"今天",
							"source":"商城下单",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"card_remain_value":20.00,
							"card_total_value":20.00,
							"id":"0000021",
							"order_date":"今天",
							"source":"商城下单",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"card_remain_value":10.00,
							"card_total_value":10.00,
							"id":"0000004",
							"order_date":"今天",
							"source":"商城下单",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"card_remain_value":10.00,
							"card_total_value":10.00,
							"id":"0000003",
							"order_date":"今天",
							"source":"商城下单",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"card_remain_value":10.00,
							"card_total_value":10.00,
							"id":"0000002",
							"order_date":"今天",
							"source":"商城下单",
							"actions":["查看详情"]
						},{
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
	#买'虚拟商品3'，赠'虚拟商品3'和'虚拟商品4'（买2赠1和1-非循环买赠）
		Given jobs登录系统::weapp
		When jobs创建买赠活动::weapp
			"""
			[{
				"name": "买a赠a和b活动2",
				"promotion_title":"",
				"start_date": "今天",
				"end_date": "1天后",
				"member_grade": "全部会员",
				"product_name": "虚拟商品3",
				"premium_products": 
					[{
						"name":"虚拟商品3",
						"count": 1
					},{
						"name":"虚拟商品4",
						"count": 1
					}],
				"count":2,
				"is_enable_cycle_mode": false
			}]
			"""
		#002-tom买2个虚拟商品3（0000031、0000032/0000033、0000041）
			When tom访问jobs的webapp
			When tom购买jobs的商品
				"""
				[{
					"order_id": "002",
					"date":"今天",
					"products":
						[{
							"name":"虚拟商品3",
							"count": 2
						}],
					"pay_type":"微信支付",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦"
				}]
				"""
			When tom使用支付方式'微信支付'进行支付订单'002'
			When 系统自动发货
				"""
				[{
					"order_id":"002",
					"weizoom_card":[],
					"other_card":
						[{
							"id":"0000031",
							"password":"1234567"
						},{
							"id":"0000032",
							"password":"2234567"
						},{
							"id":"0000033",
							"password":"3234567"
						},{
							"id":"0000041",
							"password":"1234567"
						}]
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
						"name":"虚拟商品4",
						"id":"0000041",
						"password":"1234567"
						"get_time":"今天",
						"actions":["查看详情"]
					},{
						"card_start_date":"今天",
						"card_end_date":"30天后",
						"name":"虚拟商品3",
						"id":"0000033",
						"password":"3234567"
						"get_time":"今天",
						"actions":["查看详情"]
					},{
						"card_start_date":"今天",
						"card_end_date":"30天后",
						"name":"虚拟商品3",
						"id":"0000032",
						"password":"2234567"
						"get_time":"今天",
						"actions":["查看详情"]
					},{
						"card_start_date":"今天",
						"card_end_date":"30天后",
						"name":"虚拟商品3",
						"id":"0000031",
						"password":"1234567"
						"get_time":"今天",
						"actions":["查看详情"]
					}],
					"not_use":[]
				}]
				"""
	#买'电子微众卡2'，赠'电子微众卡2'和'虚拟商品3'（买1赠2和3-非循环买赠）
		Given jobs登录系统::weapp
		When jobs创建买赠活动::weapp
			"""
			[{
				"name": "买a赠a和b活动3",
				"promotion_title":"",
				"start_date": "今天",
				"end_date": "1天后",
				"member_grade": "全部会员",
				"product_name": "电子微众卡2",
				"premium_products": 
					[{
						"name":"电子微众卡2",
						"count": 2
					},{
						"name":"虚拟商品3",
						"count": 3
					}],
				"count":1,
				"is_enable_cycle_mode": false
			}]
			"""
		#003-jack买1个电子微众卡2（0000023/0000024-25、0000034-36）
			When jack访问jobs的webapp
			When jack购买jobs的商品
				"""
				[{
					"order_id": "003",
					"date":"今天",
					"products":
						[{
							"name":"电子微众卡2",
							"count": 1
						}],
					"pay_type":"微信支付",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦"
				}]
				"""
			When jack使用支付方式'微信支付'进行支付订单'003'
			When 系统自动发货
				"""
				[{
					"order_id":"003",
					"weizoom_card":
						[{
							"id":"0000023",
							"password":"3234567"
						},{
							"id":"0000024",
							"password":"4234567"
						},{
							"id":"0000025",
							"password":"5234567"
						}],
					"other_card":
						[{
							"id":"0000034",
							"password":"4234567"
						},{
							"id":"0000035",
							"password":"5234567"
						},{
							"id":"0000036",
							"password":"6234567"
						}]
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
							"card_remain_value":20.00,
							"card_total_value":20.00,
							"id":"0000025",
							"order_date":"今天",
							"source":"商城下单",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"card_remain_value":20.00,
							"card_total_value":20.00,
							"id":"0000024",
							"order_date":"今天",
							"source":"商城下单",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"card_remain_value":20.00,
							"card_total_value":20.00,
							"id":"0000023",
							"order_date":"今天",
							"source":"商城下单",
							"actions":["查看详情"]
						}],
					"not_use":[]
				}]
				"""
			And jack获得虚拟卡包列表
				"""
				[{
					"can_use":
						[{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品3",
							"id":"0000036",
							"password":"6234567"
							"get_time":"今天",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品3",
							"id":"0000035",
							"password":"5234567"
							"get_time":"今天",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品3",
							"id":"0000034",
							"password":"4234567"
							"get_time":"今天",
							"actions":["查看详情"]
						}],
					"not_use":[]
				}]
				"""
	#买'虚拟商品4'，赠'虚拟商品4'和'电子微众卡1'（买1赠1和2-循环买赠）
		Given jobs登录系统::weapp
		When jobs创建买赠活动::weapp
			"""
			[{
				"name": "买a赠a和b活动4",
				"promotion_title":"",
				"start_date": "今天",
				"end_date": "1天后",
				"member_grade": "全部会员",
				"product_name": "虚拟商品4",
				"premium_products": 
					[{
						"name":"虚拟商品4",
						"count": 1
					},{
						"name":"电子微众卡1",
						"count": 2
					}],
				"count":1,
				"is_enable_cycle_mode": true
			}]
			"""
		#004-lily买1个虚拟商品4（0000042/0000043、0000005-06）
			When lily访问jobs的webapp
			When lily购买jobs的商品
				"""
				[{
					"order_id": "004",
					"date":"今天",
					"products":
						[{
							"name":"虚拟商品4",
							"count": 1
						}],
					"pay_type":"微信支付",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦"
				}]
				"""
			When lily使用支付方式'微信支付'进行支付订单'004'
			When 系统自动发货
				"""
				[{
					"order_id":"004",
					"weizoom_card":
						[{
							"id":"0000005",
							"password":"5234567"
						},{
							"id":"0000006",
							"password":"6234567"
						}],
					"other_card":
						[{
							"id":"0000042",
							"password":"2234567"
						},{
							"id":"0000043",
							"password":"3234567"
						}]
				}]
				"""
			When lily访问jobs的webapp
			Then lily获得微众卡包列表
				"""
				[{
					"can_use":
						[{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"card_remain_value":10.00,
							"card_total_value":10.00,
							"id":"0000006",
							"order_date":"今天",
							"source":"商城下单",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"card_remain_value":10.00,
							"card_total_value":10.00,
							"id":"0000005",
							"order_date":"今天",
							"source":"商城下单",
							"actions":["查看详情"]
						}],
					"not_use":[]
				}]
				"""
			And lily获得虚拟卡包列表
				"""
				[{
					"can_use":
						[{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品4",
							"id":"0000043",
							"password":"3234567"
							"get_time":"今天",
							"actions":["查看详情"]
						},{
							"card_start_date":"今天",
							"card_end_date":"30天后",
							"name":"虚拟商品4",
							"id":"0000042",
							"password":"2234567"
							"get_time":"今天",
							"actions":["查看详情"]
						}],
					"not_use":[]
				}]
				"""

@weshop @preminum_sale
Scenario:4 购买电子微众卡或虚拟商品，买a赠b和c
	#买电子卡1赠电子卡2和虚拟商品3（买1赠1和2-循环买赠）

	Given jobs登录系统::weapp
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
				}],
			"create_time":"今天"
		},{
			"product":
				{
					"name":"电子微众卡2",
					"bar_code":"212233",
					"price":20.00
				},
			"activity_name":"电子卡活动2",
			"card_start_date":"今天",
			"card_end_date":"30天后",
			"cards":
				[{
					"id":"0000021",
					"password":"1234567"
				}],
			"create_time":"今天"
		},{
			"product":
				{
					"name":"虚拟商品3",
					"bar_code":"312233",
					"price":30.00
				},
			"activity_name":"虚拟活动3",
			"card_start_date":"今天",
			"card_end_date":"30天后",
			"cards":
				[{
					"id":"0000031",
					"password":"1234567"
				},{
					"id":"0000032",
					"password":"2234567"
				}],
			"create_time":"今天"
		}]
		"""
	When jobs创建买赠活动::weapp
		"""
		[{
			"name": "买a赠b和c活动1",
			"promotion_title":"",
			"start_date": "今天",
			"end_date": "1天后",
			"member_grade": "全部会员",
			"product_name": "电子微众卡1",
			"premium_products":
				[{
					"name":"电子微众卡2",
					"count": 1
				},{
					"name":"虚拟商品3",
					"count": 2
				}],
			"count":1,
			"is_enable_cycle_mode": true
		}]
		"""
	#001-lily买1个电子微众卡1（0000001/0000021、0000031-32）
		When lily访问jobs的webapp
		When lily购买jobs的商品
			"""
			[{
				"order_id": "001",
				"date":"今天",
				"products":
					[{
						"name":"电子微众卡1",
						"count": 1
					}],
				"pay_type":"微信支付",
				"ship_area": "北京市 北京市 海淀区",
				"ship_address": "泰兴大厦"
			}]
			"""
		When lily使用支付方式'微信支付'进行支付订单'001'
		When 系统自动发货
			"""
			[{
				"order_id":"001",
				"weizoom_card":
					[{
						"id":"0000001",
						"password":"1234567"
					},{
						"id":"0000021",
						"password":"1234567"
							}],
						"other_card":[]
					}],
				"other_card":
					[{
						"id":"0000031",
						"password":"1234567"
					},{
						"id":"0000032",
						"password":"2234567"
					}]
			}]
			"""
		When lily访问jobs的webapp
		Then lily获得微众卡包列表
			"""
			[{
				"can_use":
					[{
						"card_start_date":"今天",
						"card_end_date":"30天后",
						"card_remain_value":20.00,
						"card_total_value":20.00,
						"id":"0000021",
						"order_date":"今天",
						"source":"商城下单",
						"actions":["查看详情"]
					},{
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
			}
			"""
		And lily获得虚拟卡包列表
			"""
			[{
				"can_use":
					[{
						"card_start_date":"今天",
						"card_end_date":"30天后",
						"name":"虚拟商品3",
						"id":"0000032",
						"password":"2234567"
						"get_time":"今天",
						"actions":["查看详情"]
					},{
						"card_start_date":"今天",
						"card_end_date":"30天后",
						"name":"虚拟商品3",
						"id":"0000031",
						"password":"1234567"
						"get_time":"今天",
						"actions":["查看详情"]
					}],
				"not_use":[]
			}]
			"""
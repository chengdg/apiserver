#watcher: zhangsanxiang@weizoom.com,benchi@weizoom.com
#_author_: "张三香" 2016.06.29

Feature:查看微众卡包列表
	"""
		微众商城:点击个人中心-我的卡包，页面中有'微众卡包'和'虚拟卡包'两个页签
		非微众商城:点击个人中心-我的卡包，无页签，页面显示微众卡的数据
		微众卡包列表:
			可用卡顺序:按照进入卡包列表时间倒序显示（如果只有绑定卡的数据，则按照绑定时间的倒序）
			卡信息显示:
				余额:显示卡的当前余额
				面值:显示卡的面值
				卡号:显示卡号
				有效期:显示卡的有效期，格式xxxx/xx/xx~xxxx/xx/xx
				来源:显示卡的来源，商城下单（购买的电子微众卡）、绑定卡、返利卡
				【详情】:点击跳转到该张微众卡的使用详情页面
			【点击查看不可用卡】:在可用卡数据下方显示，默认收起，点击则展开不可用卡的数据（已用完、已过期、已冻结（卡的状态为未激活））
			不可用卡数据的排序规则：已冻结的放在最上面，已过期和已用完的放在下面按倒序（绑卡时间的倒序）排列，因为已冻结的有可能还会被开通
			不可用卡的【详情】可点击进入微众卡详情页
	"""

Background:
	Given 重置'weapp'的bdd环境
	Given 重置'weizoom_card'的bdd环境
	Given 设置jobs为自营平台账号::weapp
	Given jobs登录系统::weapp
	And jobs已添加供货商::weapp
		"""
		[{
			"name": "供货商a",
			"responsible_person": "张大众",
			"supplier_tel": "15211223344",
			"supplier_address": "北京市海淀区海淀科技大厦",
			"remark": "备注"
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
			"name":"商品1",
			"product_type":"普通商品",
			"supplier": "供货商a",
			"purchase_price": 9.99,
			"price": 10.00,
			"weight": 1.0,
			"stock_type": "无限",
			"pay_interfaces":
				[{
					"type": "在线支付"
				},{
					"type": "货到付款"
				}],
			"detail":"普通商品1的详情",
			"status":"在售"
		}]
		"""

	#普通商家nokia
	Given nokia登录系统::weapp
	And nokia已添加支付方式::weapp
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
	When nokia开通使用微众卡权限::weapp
	Given nokia已添加商品::weapp
		"""
		[{
			"name":"nokia商品1",
			"price": 10.00
		}]
		"""

	When bill关注jobs的公众号
	When bill关注nokia的公众号
	When tom关注jobs的公众号

	#创建微众卡
	Given test登录管理系统::weizoom_card
	When test新建通用卡::weizoom_card
		"""
		[{
			"name":"10元微众卡",
			"prefix_value":"101",
			"type":"virtual",
			"money":"10.00",
			"num":"3",
			"comments":"微众卡"
		}]
		"""
	#微众卡审批出库
	When test下订单::weizoom_card
		"""
		[{
			"card_info":[{
				"name":"10元微众卡",
				"order_num":"3",
				"start_date":"2016-06-16 00:00",
				"end_date":"2026-06-16 00:00"
			}],
			"order_info":{
				"order_id":"0001"
				}
		}]
		"""
	#激活微众卡
	When test批量激活订单'0001'的卡::weizoom_card

@weizoon_card @weizoon_card_list @mall3
Scenario:1 查看我的卡包-微众卡包可用卡列表
	#我的卡包-微众卡包数据为空
		When bill访问jobs的webapp
		Then bill获得微众卡包列表
			"""
			{
				"usable_cards":[],
				"unusable_cards":[]

			}
			"""
	#我的卡包-微众卡包数据不为空（只包含可用卡的数据）
		When bill访问jobs的webapp
		When bill绑定微众卡
			"""
			{
				"binding_date":"2016-06-16",
				"binding_shop":"jobs",
				"weizoom_card_info":
					{
						"id":"101000001",
						"password":"1234567"
					}
			}
			"""
		When bill绑定微众卡
			"""
			{
				"binding_date":"2016-06-16",
				"binding_shop":"jobs",
				"weizoom_card_info":
					{
						"id":"101000002",
						"password":"1234567"
					}
			}
			"""
		Then bill获得微众卡包列表
			"""
			{
				"usable_cards":
					[{
						"valid_time_from":"2016-06-16 00:00",
						"valid_time_to":"2026-06-16 00:00",
						"balance":"10.00",
						"face_value":"10.00",
						"card_number":"101000002",
						"binding_date":"2016-06-16",
						"source":"绑定卡",
						"actions":["详情"]
					},{
						"valid_time_from":"2016-06-16 00:00",
						"valid_time_to":"2026-06-16 00:00",
						"balance":"10.00",
						"face_value":"10.00",
						"card_number":"101000001",
						"binding_date":"2016-06-16",
						"source":"绑定卡",
						"actions":["详情"]
					}],
				"unusable_cards":[]
			}
			"""
		#同一张卡，可以多人绑定
		When tom访问jobs的webapp
		When tom绑定微众卡
			"""
			{
				"binding_date":"2016-06-16",
				"binding_shop":"jobs",
				"weizoom_card_info":
					{
						"id":"101000001",
						"password":"1234567"
					}
			}
			"""
		Then tom获得微众卡包列表
			"""
			{
				"usable_cards":
					[{
						"valid_time_from":"2016-06-16 00:00",
						"valid_time_to":"2026-06-16 00:00",
						"balance":"10.00",
						"face_value":"10.00",
						"card_number":"101000001",
						"binding_date":"2016-06-16",
						"source":"绑定卡",
						"actions":["详情"]
					}],
				"unusable_cards":[]
			}
			"""
		#同一张卡，可以在不同商家绑定
		When bill访问nokia的webapp
		When bill绑定微众卡
			"""
			{
				"binding_date":"2016-06-16",
				"binding_shop":"nokia",
				"weizoom_card_info":
					{
						"id":"101000001",
						"password":"1234567"
					}
			}
			"""
		Then bill获得微众卡包列表
			"""
			{
				"usable_cards":
					[{
						"valid_time_from":"2016-06-16 00:00",
						"valid_time_to":"2026-06-16 00:00",
						"balance":"10.00",
						"face_value":"10.00",
						"card_number":"101000001",
						"binding_date":"2016-06-16",
						"source":"绑定卡",
						"actions":["详情"]
					}],
				"unusable_cards":[]
			}
			"""

@weizoon_card @weizoon_card_list
Scenario:2 查看我的卡包-微众卡包不可用卡列表
		When bill访问jobs的webapp
		#bill在jobs绑卡101000001
		When bill绑定微众卡
			"""
			{
				"binding_date":"2016-06-16",
				"binding_shop":"jobs",
				"weizoom_card_info":
					{
						"id":"101000001",
						"password":"1234567"
					}
			}
			"""
		#bill在jobs绑卡101000002
		When bill绑定微众卡
			"""
			{
				"binding_date":"2016-06-16",
				"binding_shop":"jobs",
				"weizoom_card_info":
					{
						"id":"101000002",
						"password":"1234567"
					}
			}
			"""
		#bill在jobs绑卡101000003
		When bill绑定微众卡
			"""
			{
				"binding_date":"2016-06-16",
				"binding_shop":"jobs",
				"weizoom_card_info":
					{
						"id":"101000003",
						"password":"1234567"
					}
			}
			"""
		#tom在jobs绑卡101000001
		When tom访问jobs的webapp
		When tom绑定微众卡
			"""
			{
				"binding_date":"2016-06-16",
				"binding_shop":"jobs",
				"weizoom_card_info":
					{
						"id":"101000001",
						"password":"1234567"
					}
			}
			"""
		#bill在nokia绑卡101000001
		When bill访问nokia的webapp
		When bill绑定微众卡
			"""
			{
				"binding_date":"2016-06-16",
				"binding_shop":"nokia",
				"weizoom_card_info":
					{
						"id":"101000001",
						"password":"1234567"
					}
			}
			"""
		#绑定成功后，后台将卡101000002停用
			Given test登录管理系统::weizoom_card
			When test停用卡号'101000002'的卡::weizoom_card
			When bill访问jobs的webapp
			Then bill获得微众卡包列表
				"""
				{
					"usable_cards":
						[{
							"valid_time_from":"2016-06-16 00:00",
							"valid_time_to":"2026-06-16 00:00",
							"balance":"10.00",
							"face_value":"10.00",
							"card_number":"101000003",
							"binding_date":"2016-06-16",
							"source":"绑定卡",
							"actions":["详情"]
						},{
							"valid_time_from":"2016-06-16 00:00",
							"valid_time_to":"2026-06-16 00:00",
							"balance":"10.00",
							"face_value":"10.00",
							"card_number":"101000001",
							"binding_date":"2016-06-16",
							"source":"绑定卡",
							"actions":["详情"]
						}],
					"unusable_cards":
						[{
							"valid_time_from":"2016-06-16 00:00",
							"valid_time_to":"2026-06-16 00:00",
							"balance":"10.00",
							"face_value":"10.00",
							"card_number":"101000002",
							"binding_date":"2016-06-16",
							"source":"绑定卡",
							"actions":["详情"],
							"status":"未激活"
						}]
				}
				"""
		#绑定成功后，后台将卡101000001停用
			Given test登录管理系统::weizoom_card
			When test停用卡号'101000001'的卡::weizoom_card
			When bill访问jobs的webapp
			Then bill获得微众卡包列表
				"""
				{
					"usable_cards":
						[{
							"valid_time_from":"2016-06-16 00:00",
							"valid_time_to":"2026-06-16 00:00",
							"balance":"10.00",
							"face_value":"10.00",
							"card_number":"101000003",
							"binding_date":"2016-06-16",
							"source":"绑定卡",
							"actions":["详情"]
						}],
					"unusable_cards":
						[{
							"valid_time_from":"2016-06-16 00:00",
							"valid_time_to":"2026-06-16 00:00",
							"balance":"10.00",
							"face_value":"10.00",
							"card_number":"101000002",
							"binding_date":"2016-06-16",
							"source":"绑定卡",
							"actions":["详情"]
						},{
							"valid_time_from":"2016-06-16 00:00",
							"valid_time_to":"2026-06-16 00:00",
							"balance":"10.00",
							"face_value":"10.00",
							"card_number":"101000001",
							"binding_date":"2016-06-16",
							"source":"绑定卡",
							"actions":["详情"],
							"status":"未激活"
						}]
				}
				"""
		#绑定成功后，当该卡余额为0时，微众卡包中不可用，显示'已用完'
			When bill访问jobs的webapp
			When bill购买jobs的商品
				"""
				{
					"pay_type": "微信支付",
					"products":[{
						"name":"商品1",
						"price":10.00,
						"count":1
					}],
					"weizoom_card":[{
						"card_name":"101000003",
						"card_pass":"1234567"
					}]
				}
				"""
			Then bill获得微众卡包列表
				"""
				[{
					"usable_cards":[],
					"unusable_cards":
						[{
							"valid_time_from":"2016-06-16 00:00",
							"valid_time_to":"2026-06-16 00:00",
							"balance":10.00,
							"face_value":10.00,
							"card_number":"101000002",
							"binding_date":"2016-06-16",
							"source":"绑定卡",
							"actions":["详情"],
							"status":"未激活"
						},{
							"valid_time_from":"2016-06-16 00:00",
							"valid_time_to":"2026-06-16 00:00",
							"balance":10.00,
							"face_value":10.00,
							"card_number":"101000001",
							"binding_date":"2016-06-16",
							"source":"绑定卡",
							"actions":["详情"],
							"status":"已用完"
						},{
							"valid_time_from":"2016-06-16 00:00",
							"valid_time_to":"2026-06-16 00:00",
							"balance":10.00,
							"face_value":10.00,
							"card_number":"101000003",
							"binding_date":"2016-06-16",
							"source":"绑定卡",
							"actions":["详情"],
							"status":"已用完"
						}]
				}]
				"""

			When bill访问nokia的webapp
			Then bill获得微众卡包列表
				"""
				{
					"usable_cards":[],
					"unusable_cards":
						[{
							"valid_time_from":"2016-06-16 00:00",
							"valid_time_to":"2026-06-16 00:00",
							"balance":"10.00",
							"face_value":"10.00",
							"card_number":"101000001",
							"binding_date":"2016-06-16",
							"source":"绑定卡",
							"actions":["详情"],
							"status":"未激活"
						}]
				}
				"""

			When tom访问jobs的webapp
			Then tom获得微众卡包列表
				"""
				{
					"usable_cards":[],
					"unusable_cards":
						[{
							"valid_time_from":"2016-06-16 00:00",
							"valid_time_to":"2026-06-16 00:00",
							"balance":"10.00",
							"face_value":"10.00",
							"card_number":"101000001",
							"binding_date":"2016-06-16",
							"source":"绑定卡",
							"actions":["详情"],
							"status":"未激活"
						}]
				}
				"""

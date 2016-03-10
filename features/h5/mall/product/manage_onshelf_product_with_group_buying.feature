# watcher: benchi@weizoom.com, zhangsanxiang@weizoom.com
#_author_:张三香 2016.03.10

Feature:在售商品列表-团购活动
	"""
	1、团购进行中的商品,不能进行下架和永久删除操作,点击【下架】或【永久删除】时，红框提示"该商品正在进行团购活动"
	2、团购进行中的商品，在进行 全选-批量删除 和 全选-批量下架时时，不被选取
	3、团购成功的订单，在订单完成后计算商品的销量
	"""
Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
	And jobs已添加支付方式:weapp
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
	When jobs开通使用微众卡权限:weapp
	When jobs添加支付方式:weapp
		"""
		[{
			"type": "微众卡支付",
			"is_active": "启用"
		}]
		"""
	Given jobs已创建微众卡:weapp
		"""
		[{
			"cards": [{
				"id": "0000001",
				"password": "1234567",
				"status": "未使用",
				"price": 50
			},{
			"cards": [{
				"id": "0000002",
				"password": "2234567",
				"status": "未使用",
				"price": 200
		}]
		"""
	Given jobs已添加商品:weapp
		"""
		[{
			"name":"商品1",
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"user_code":"0101",
						"weight":1.0,
						"stock_type": "有限",
						"stocks": 100
					}
				}
			},
			"postage":10.0,
			"distribution_time":"on"
		},{
			"name":"商品2",
			"model": {
				"models": {
					"standard": {
						"price": 200.00,
						"user_code":"0102",
						"weight":1.0,
						"stock_type": "无限"
					}
				}
			}
		}]
		"""
	When jobs创建团购活动:weapp
		"""
		[{
			"group_name":"团购活动1",
			"start_time":"今天",
			"end_time":"2天后",
			"product_name":"商品1",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":90.00
				}],
				"ship_date":20,
				"product_counts":100,
				"material_image":"1.jpg",
				"share_description":"团购活动1分享描述"
		},{
			"group_name":"团购活动2",
			"start_time":"今天",
			"end_time":"2天后",
			"product_name":"商品2",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":190.00
				},{
					"group_type":10,
					"group_days":2,
					"group_price":188.00
				}],
				"ship_date":20,
				"product_counts":100,
				"material_image":"1.jpg",
				"share_description":"团购活动2分享描述"
		}]
		"""

Scenario:1 对团购活动中的商品进行下架或删除操作
	Given jobs登录系统:weapp
	Then jobs能获得'在售'商品列表:weapp
		"""
		[{
			"name": "商品2"
		}, {
			"name": "商品1"
		}]
		"""
	#团购活动中的商品,不能进行下架和删除操作
	When jobs'下架'商品'商品2':weapp
	Then jobs获得提示信息'该商品正在进行团购活动':weapp
	When jobs'永久删除'商品'商品1':weapp
	Then jobs获得提示信息'该商品正在进行团购活动':weapp

	#团购活动结束后,可以对商品进行下架和删除操作
	When jobs'结束'团购活动'团购活动2':weapp
	When jobs'下架'商品'商品2':weapp
	Then jobs能获得'在售'商品列表:weapp
		"""
		[{
			"name": "商品1"
		}]
		"""
	And jobs能获得'待售'商品列表:weapp
		"""
		[{
			"name": "商品2"
		}]
		"""
	When jobs'结束'团购活动'团购活动1':weapp
	When jobs'永久删除'商品'商品1':weapp
	Then jobs能获得'在售'商品列表:weapp
		"""
		[]
		"""
	And jobs能获得'待售'商品列表:weapp
		"""
		[{
			"name": "商品2"
		}]
		"""

Scenario:2 团购成功的订单,订单完成后计算商品'销量'
	Given bill关注jobs的公众号
	And tom关注jobs的公众号
	And bill1关注jobs的公众号
	And bill2关注jobs的公众号
	And bill3关注jobs的公众号
	Given jobs登录系统:weapp
	Then jobs能获取商品'商品2':weapp
		"""
		{
			"name": "商品1",
			"sales": 0,
			"model": {
				"models": {
					"standard": {
						"price": 200.00,
						"user_code":"0102",
						"weight":1.0,
						"stock_type": "无限"
					}
				}
			}
		}
		"""
	#通过团购购买'商品2'
		#00201-待发货（团购成功,tom开团'团购活动2'）
			When tom访问jobs的webapp
			When tom参加jobs的团购活动
				"""
				{
					"group_name": "团购活动2",
					"group_leader": "tom",
					"group_dict":
						[{
							"group_type":5,
							"group_days":1,
							"group_price":190.00
						}],
					"ship_name": "tom",
					"ship_tel": "13811223344",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦",
					"order_id":"00201",
					"pay_type":"微信支付",
					"products": [{
						"name": "商品2"
					}]
				}
				"""
			When tom使用支付方式'微信支付'进行支付
		#00202-待发货（团购成功,bill参团'团购活动2'）
			When bill访问jobs的webapp
			When bill参加jobs的团购活动
				"""
				{
					"group_name": "团购活动2",
					"group_leader": "tom",
					"group_dict":
						[{
							"group_type":5,
							"group_days":1,
							"group_price":190.00
						}],
					"ship_name": "bill",
					"ship_tel": "13811223344",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦",
					"order_id":"00202",
					"pay_type":"微信支付",
					"products": [{
						"name": "商品2"
					}]
				}
				"""
			When bill使用支付方式'微信支付'进行支付
		#00203-待发货（团购成功,bill1参团'团购活动2'）
			When bill1访问jobs的webapp
			When bill1参加jobs的团购活动
				"""
				{
					"group_name": "团购活动2",
					"group_leader": "tom",
					"group_dict":
						[{
							"group_type":5,
							"group_days":1,
							"group_price":190.00
						}],
					"ship_name": "bill1",
					"ship_tel": "13811223344",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦",
					"order_id":"00203",
					"pay_type":"微信支付",
					"products": [{
						"name": "商品2"
					}]
				}
				"""
			When bill1使用支付方式'微信支付'进行支付
		#00204-待发货（团购成功,bill2参团'团购活动2'）
			When bill2访问jobs的webapp
			When bill2参加jobs的团购活动
				"""
				{
					"group_name": "团购活动2",
					"group_leader": "tom",
					"group_dict":
						[{
							"group_type":5,
							"group_days":1,
							"group_price":190.00
						}],
					"ship_name": "bill2",
					"ship_tel": "13811223344",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦",
					"order_id":"00204",
					"pay_type":"微信支付",
					"products": [{
						"name": "商品2"
					}]
				}
				"""
			When bill2使用支付方式'微信支付'进行支付
		#00205-待发货（团购成功,bill3参团'团购活动2'）
			When bill3访问jobs的webapp
			When bill3参加jobs的团购活动
				"""
				{
					"group_name": "团购活动2",
					"group_leader": "tom",
					"group_dict":
						[{
							"group_type":5,
							"group_days":1,
							"group_price":190.00
						}],
					"ship_name": "bill3",
					"ship_tel": "13811223344",
					"ship_area": "北京市 北京市 海淀区",
					"ship_address": "泰兴大厦",
					"order_id":"00205",
					"pay_type":"微信支付",
					"products": [{
						"name": "商品2"
					}],
					"weizoom_card":[{
						"card_name":"0000002",
						"card_pass":"2234567"
							}]
				}
				"""
	Given jobs登录系统:weapp
	Then jobs能获取商品'商品2':weapp
		"""
		{
			"name": "商品1",
			"sales": 0,
			"model": {
				"models": {
					"standard": {
						"price": 200.00,
						"user_code":"0102",
						"weight":1.0,
						"stock_type": "无限"
					}
				}
			}
		}
		"""
	#订单完成后才计算商品销量
	When jobs对订单进行发货:weapp
		"""
		{
			"order_no": "00205",
			"logistics": "off",
			"shipper": ""
		}
		"""
	When jobs'完成'订单'00205':weapp
	Then jobs能获取商品'商品2':weapp
		"""
		{
			"name": "商品1",
			"sales": 1,
			"model": {
				"models": {
					"standard": {
						"price": 200.00,
						"user_code":"0102",
						"weight":1.0,
						"stock_type": "无限"
					}
				}
			}
		}
		"""
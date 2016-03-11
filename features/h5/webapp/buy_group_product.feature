# watcher: fengxuejing@weizoom.com,benchi@weizoom.com
# __author__ : "冯雪静"
#团购：手机端购买
Feature: 手机端购买团购活动
	"""
	手机端访问团购活动，进行购买
		1.团购商品在商品列表页显示商品的原价
		2.会员访问团购活动，能进行开团购买
		3.会员可开团也可参团，非会员可以参团，不能开团
		4.开团后，人数达到上限，团购成功，获得成功页面，参与团购会员手机端会收到模板消息
		5.开团后，人数没有达到标准，期限到了，团购失败，支付的订单自动退款
		6.下单成功，库存减少，团购失败，库存恢复
		7.开团时下单不进行支付，不能成功开团
		8.一个会员可以参加多个团，对一个团购活动只能开一次团，不能重复参加，也不能重复开团
		9.参团列表参团人数一样的话以开团时间倒序显示，优先显示团购差一人的团
		10.商品加入购物车后，后台对此商品创建团购活动，此商品在购物车为失效状态，结束活动后，购物车的商品恢复正常
	"""

Background:
	Given jobs登录系统:weapp
	And jobs已有微众卡支付权限:weapp
	And jobs已添加支付方式:weapp
		"""
		[{
			"type": "支付宝"
		},{
			"type": "微众卡支付"
		}, {
			"type": "货到付款"
		}, {
			"type": "微信支付"
		}]
		"""
	And jobs已创建微众卡:weapp
		"""
		{
			"cards":[{
				"id":"0000001",
				"password":"1234567",
				"status":"未使用",
				"price":100.00
			},{
				"id":"0000002",
				"password":"1234567",
				"status":"未使用",
				"price":100.00
			}]
		}
		"""
	When jobs添加邮费配置:weapp
		"""
		[{
			"name":"顺丰",
			"first_weight":1,
			"first_weight_price":15.00,
			"added_weight":1,
			"added_weight_price":5.00
		}]
		"""
	And jobs选择'顺丰'运费配置:weapp
	And jobs已添加商品:weapp
		"""
		[{
			"name": "商品1",
			"price": 100.00,
			"weight": 1,
			"postage": "顺丰",
			"distribution_time":"on"
		}, {
			"name": "商品2",
			"price": 100.00,
			"weight": 1,
			"stock_type": "有限",
			"stocks": 100,
			"postage": 10.00
		}, {
			"name": "商品3",
			"price": 100.00,
			"stock_type": "有限",
			"stocks": 9
		}]
		"""
	And jobs新建团购活动:weapp
		"""
		[{
			"group_name":"团购1",
			"start_time":"今天",
			"end_time":"2天后",
			"product_name":"商品1",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":20.00
				},{
					"group_type":10,
					"group_days":2,
					"group_price":10.00
				}],
				"ship_date":20,
				"product_counts":100,
				"material_image":"1.jpg",
				"share_description":"团购分享描述"
		}, {
			"group_name":"团购2",
			"start_time":"今天",
			"end_time":"2天后",
			"product_name":"商品2",
			"group_dict":
				[{
					"group_type":5,
					"group_days":2,
					"group_price":21.00
				},{
					"group_type":10,
					"group_days":2,
					"group_price":11.00
				}],
				"ship_date":20,
				"product_counts":100,
				"material_image":"1.jpg",
				"share_description":"团购分享描述"
		}]
		"""
	Given bill关注jobs的公众号
	And tom关注jobs的公众号

Scenario: 1 会员访问团购活动首页能进行开团
	jobs创建团购，活动期内
	1.bill获得商品列表页
	2.会员bill可以开团购买，开团成功后就不能重复开一个团购活动
	3.会员tom可以通过bill分享的链接直接参团
	4.非会员nokia通过分享链接能直接参团，不能开团购买

	When bill访问jobs的webapp
	And bill浏览jobs的webapp的'全部'商品列表页
	Then bill获得webapp商品列表
		"""
		[{
			"name": "商品3",
			"price": 100.00
		}, {
			"name": "商品2",
			"price": 100.00
		}, {
			"name": "商品1",
			"price": 100.00
		}]
		"""

	#bill是已关注的会员可以直接开团
	Then bill能获得开团活动列表
		"""
		{
			"group_name": "团购2"
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				},{
					"group_type":10,
					"group_days":2,
					"group_price":11.00
				}]
		}, {
			"group_name": "团购1"
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":20.00
				},{
					"group_type":10,
					"group_days":2,
					"group_price":10.00
				}]
		}]
		"""

	#bill开“团购5人团”，团购活动只能使用微信支付，有配送时间，运费0元
	#支付完成后跳转到活动详情页-显示邀请好友参团
	When bill参加jobs的团购活动
		"""
		{
			"group_name": "团购1",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":20.00
				}],
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"distribution_time":"5天后 10:00-12:30",
			"pay_type":"微信支付",
			"products": [{
				"name": "商品1"
			}]
		}
		"""
	When bill使用支付方式'微信支付'进行支付
	Then bill成功创建订单
		"""
		{
			"is_group_buying": "true",
			"status": "待发货",
			"final_price": 20.00,
			"postage": 0.00,
			"products": [{
				"name": "商品1",
				"price": 20.00,
				"count": 1
			}]
		}
		"""

	#bill开团后，就不能重复开一个团购活动
	Then bill能获得开团活动列表
		"""
		[{
			"group_name": "团购2"
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				},{
					"group_type":10,
					"group_days":2,
					"group_price":11.00
				}]
		}]
		"""

Scenario: 2 会员可以通过分享链接直接参加团购活动
	bill开团后分享团购活动链接
	1.会员tom可以直接参加团购活动，参加后就不能重复参加，可以开团
	2.非会员nokia通过分享链接能直接参团，不能开团购买

	When bill访问jobs的webapp
	When bill参加jobs的团购活动
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				}],
			"pay_type":"微信支付",
			"products": [{
				"name": "商品2"
			}]
		}
		"""
	When bill使用支付方式'微信支付'进行支付
	Then bill成功创建订单
		"""
		{
			"is_group_buying": "true",
			"status": "待发货",
			"final_price": 21.00,
			"postage": 0.00,
			"products": [{
				"name": "商品2",
				"price": 21.00,
				"count": 1
			}]
		}
		"""

	When bill把jobs的团购活动"团购2"的链接分享到朋友圈

	#会员打开链接显示-我要参团，看看还有什么团
	When tom访问jobs的webapp
	Then tom能获得参团活动列表
		"""
		[{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00,
					"offered":[{
						"number":1,
						"member":["bill"]
						}]
				}]
		}]
		"""

	#支付完成后跳转到活动详情页显示-邀请好友参团,我要开团
	When tom参加jobs的团购活动
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				}],
			"pay_type":"微信支付",
			"products": [{
				"name": "商品2"
			}]
		}
		"""
	When tom使用支付方式'微信支付'进行支付
	Then tom成功创建订单
		"""
		{
			"is_group_buying": "true",
			"status": "待发货",
			"final_price": 21.00,
			"postage": 0.00,
			"products": [{
				"name": "商品2",
				"price": 21.00,
				"count": 1
			}]
		}
		"""
	Then tom能获得开团活动列表
		"""
		[{
			"group_name": "团购2"
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				},{
					"group_type":10,
					"group_days":2,
					"group_price":11.00
				}]
		}, {
			"group_name": "团购1"
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":20.00
				},{
					"group_type":10,
					"group_days":2,
					"group_price":10.00
				}]
		}]
		"""
	Then tom能获得参团活动列表
		"""
		[]
		"""

	When 清空浏览器:weapp
	When nokia点击bill分享链接
	When nokia访问jobs的webapp
	Then nokia能获得参团活动列表
		"""
		[{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00,
					"offered":[{
						"number":2,
						"member":["bill", "tom"]
						}]
				}]
		}]
		"""

	#非会员支付完成后跳转二维码引导关注
	When nokia参加jobs的团购活动
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				}],
			"pay_type":"微信支付",
			"products": [{
				"name": "商品2"
			}]
		}
		"""
	When nokia使用支付方式'微信支付'进行支付
	Then nokia成功创建订单
		"""
		{
			"is_group_buying": "true",
			"status": "待发货",
			"final_price": 21.00,
			"postage": 0.00,
			"products": [{
				"name": "商品2",
				"price": 21.00,
				"count": 1
			}]
		}
		"""

	#非会员不能开团,点击“我要开团”弹出二维码
	Then nokia能获得开团活动列表
		"""
		[]
		"""

Scenario: 3 会员开团后团购活动成功
	会员开团后
	1.在活动期内团购人数达到开团人数，团购成功
	2.团购人数达到开团人数，不能再参加此团购

	Given tom1关注jobs的公众号
	And tom2关注jobs的公众号
	And tom3关注jobs的公众号
	And tom4关注jobs的公众号

	#bill参与团购"团购2"开团
	When bill访问jobs的webapp
	When bill参加jobs的团购活动
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				}],
			"pay_type":"微信支付",
			"products": [{
				"name": "商品2"
			}]
		}
		"""
	When bill使用支付方式'微信支付'进行支付

	#tom参与bill开的团
	When tom访问jobs的webapp
	Then tom能获得参团活动列表
		"""
		[{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00,
					"offered":[{
						"number":1,
						"member":["bill"]
						}]
				}]
		}]
		"""
	When tom参加jobs的团购活动
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				}],
			"pay_type":"微信支付",
			"products": [{
				"name": "商品2"
			}]
		}
		"""
	When tom使用支付方式'微信支付'进行支付

	#tom1参与bill开的团
	When tom1访问jobs的webapp
	Then tom1能获得参团活动列表
		"""
		[{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00,
					"offered":[{
						"number":2,
						"member":["bill", "tom"]
						}]
				}]
		}]
		"""
	When tom1参加jobs的团购活动
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				}],
			"pay_type":"微信支付",
			"products": [{
				"name": "商品2"
			}]
		}
		"""
	When tom1使用支付方式'微信支付'进行支付

	#tom2参与bill开的团
	When tom2访问jobs的webapp
	Then tom2能获得参团活动列表
		"""
		[{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00,
					"offered":[{
						"number":3,
						"member":["bill", "tom", "tom1"]
						}]
				}]
		}]
		"""
	When tom2参加jobs的团购活动
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				}],
			"pay_type":"微信支付",
			"products": [{
				"name": "商品2"
			}]
		}
		"""
	When tom2使用支付方式'微信支付'进行支付

	#tom3参与bill开的团
	When tom3访问jobs的webapp
	Then tom3能获得参团活动列表
		"""
		[{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00,
					"offered":[{
						"number":4,
						"member":["bill", "tom", "tom1", "tom2"]
						}]
				}]
		}]
		"""
	When tom3参加jobs的团购活动
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				}],
			"pay_type":"微信支付",
			"products": [{
				"name": "商品2"
			}]
		}
		"""
	When tom3使用支付方式'微信支付'进行支付
	Then tom3获得提示信息'恭喜您团购成功 商家将在该商品团购结束20天内进行发货'


	#团购活动达到上限，团购成功，下一个人就不能参加这个活动了
	When tom4访问jobs的webapp
	Then tom4能获得参团活动列表
		"""
		[]
		"""

Scenario: 4 会员开团后团购活动失败
	会员开团后
	1.没有在期限内达到人数，团购活动失败
	2.结束活动，团购活动失败
	3.团购失败后，用微众卡支付的订单直接返还微众卡
	4.库存恢复

	When bill访问jobs的webapp
	When bill参加jobs的团购活动
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				}],
			"order_id":"001",
			"pay_type":"微信支付",
			"products": [{
				"name": "商品2"
			}],
			"weizoom_card":[{
				"card_name":"0000001",
				"card_pass":"1234567"
			}]
		}
		"""

	Given jobs登录系统:weapp
	Then jobs能获取微众卡'0000001':weapp
		"""
		{
			"status":"已使用",
			"price":79.00
		}
		"""

	#下单成功，库存减少
	Then jobs能获取商品'商品2':weapp
		"""
		{
			"name": "商品2",
			"price": 100.00,
			"weight": 1,
			"stock_type": "有限",
			"stocks": 99,
			"postage": 10.00
		}
		"""
	When jobs'结束'团购活动'团购2':weapp
	Then jobs能获取微众卡'0000001':weapp
		"""
		{
			"status":"已使用",
			"price":100.00
		}
		"""

	#团购失败，库存恢复
	Then jobs能获取商品'商品2':weapp
		"""
		{
			"name": "商品2",
			"price": 100.00,
			"weight": 1,
			"stock_type": "有限",
			"stocks": 100,
			"postage": 10.00
		}
		"""

	When bill访问jobs的webapp
	Then bill手机端获取订单'001'
		"""
		{
			"order_no": "001",
			"status": "已取消"
		}
		"""

Scenario: 5 会员开团不进行支付，开团不成功
	会员开团不进行支付，开团不成功
	1.其他会员获取不到参团列表

	When bill访问jobs的webapp
	When bill参加jobs的团购活动
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				}],
			"order_id":"001",
			"pay_type":"微信支付",
			"products": [{
				"name": "商品2"
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"is_group_buying": "true",
			"status": "待支付",
			"final_price": 21.00,
			"postage": 0.00,
			"products": [{
				"name": "商品2",
				"price": 21.00,
				"count": 1
			}]
		}
		"""
	When tom3访问jobs的webapp
	Then tom3能获得参团活动列表
		"""
		[]
		"""

Scenario: 6 一个会员可以参加多个会员开启的团购活动
	1.一个会员既能开团又能参团，可以参加多个团购活动

	Given tom1关注jobs的公众号
	And tom2关注jobs的公众号
	And tom3关注jobs的公众号

	When bill访问jobs的webapp
	When bill参加jobs的团购活动
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				}],
			"pay_type":"微信支付",
			"products": [{
				"name": "商品2"
			}]
		}
		"""
	When bill使用支付方式'微信支付'进行支付

	When tom访问jobs的webapp
	When tom参加jobs的团购活动
		"""
		{
			"group_name": "团购2",
			"group_leader": "tom",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				}],
			"pay_type":"微信支付",
			"products": [{
				"name": "商品2"
			}]
		}
		"""
	When tom使用支付方式'微信支付'进行支付

	When tom1访问jobs的webapp
	#参团列表参团人数一样的话以开团时间倒序显示
	Then tom1能获得参团活动列表
		"""
		[{
			"group_name": "团购2",
			"group_leader": "tom",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00,
					"offered":[{
						"number":1,
						"member":["tom"]
						}]
				}]
		}, {
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00,
					"offered":[{
						"number":1,
						"member":["bill"]
						}]
				}]
		}]
		"""
	When tom1参加jobs的团购活动
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				}],
			"pay_type":"微信支付",
			"products": [{
				"name": "商品2"
			}]
		}
		"""
	When tom1使用支付方式'微信支付'进行支付
	When tom1参加jobs的团购活动
		"""
		{
			"group_name": "团购2",
			"group_leader": "tom",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				}],
			"pay_type":"微信支付",
			"products": [{
				"name": "商品2"
			}]
		}
		"""
	When tom1使用支付方式'微信支付'进行支付

	When tom访问jobs的webapp
	Then tom能获得参团活动列表
		"""
		[{
			"group_name": "团购1",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00,
					"offered":[{
						"number":2,
						"member":["bill", "tom1"]
						}]
				}]
		}]
		"""
	When tom参加jobs的团购活动
		"""
		{
			"group_name": "团购1",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				}],
			"pay_type":"微信支付",
			"products": [{
				"name": "商品2"
			}]
		}
		"""
	When tom使用支付方式'微信支付'进行支付

	When tom3参加jobs的团购活动
		"""
		{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00
				}],
			"pay_type":"微信支付",
			"products": [{
				"name": "商品2"
			}]
		}
		"""
	When tom3使用支付方式'微信支付'进行支付

	When tom2访问jobs的webapp
	#参团列表优先显示拼团人数差一人的团购活动
	Then tom2能获得参团活动列表
		"""
		[{
			"group_name": "团购2",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00,
					"offered":[{
						"number":4,
						"member":["bill", "tom1", "tom", "tom3"]
						}]
				}]
		}, {
			"group_name": "团购2",
			"group_leader": "tom",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":21.00,
					"offered":[{
						"number":1,
						"member":["tom"]
						}]
				}]
		}]
		"""

Scenario: 7 会员把商品添加购物车后，后台把这个商品创建成团购活动
	会员把商品3添加到购物车，后台把商品创建成团购活动
	1.商品3在购物车为失效状态
	2.结束活动后，商品恢复到正常状态

	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品3",
			"count": 1
		}]
		"""
	Then bill能获得购物车
		"""
		{
			"product_groups": [{
				"products": [{
					"name": "商品3",
					"price": 100,
					"count": 1
				}]
			}],
			"invalid_products": []
		}
		"""
	Given jobs登录系统
	When jobs新建团购活动:weapp
		"""
		[{
			"group_name":"团购3",
			"start_time":"今天",
			"end_time":"2天后",
			"product_name":"商品3",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":20.00
				},{
					"group_type":10,
					"group_days":2,
					"group_price":10.00
				}],
				"ship_date":20,
				"product_counts":100,
				"material_image":"1.jpg",
				"share_description":"团购分享描述"
		}]
		"""

	When bill访问jobs的webapp
	Then bill能获得购物车
		"""
		{
			"product_groups": [],
			"invalid_products": [{
				"name": "商品3",
				"price": 100,
				"count": 1
			}]
		}
		"""

	Given jobs登录系统:weapp
	When jobs'结束'团购活动'团购3':weapp

	When bill访问jobs的webapp
	Then bill能获得购物车
		"""
		{
			"product_groups": [{
				"products": [{
					"name": "商品3",
					"price": 100,
					"count": 1
				}]
			}],
			"invalid_products": []
		}
		"""







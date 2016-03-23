# Created by Administrator at 2016/3/14
Feature: #Enter feature name here
  # Enter feature description here

  Scenario: # Enter scenario name here
    # Enter steps here



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
	Then bill能获得开团活动列表:weapp
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
	When bill参加jobs的团购活动:weapp
		"""
		{
			"group_name": "团购1",
			"group_leader": "bill",
			"group_dict":
				[{
					"group_type":5,
					"group_days":1,
					"group_price":20.00
				}]
		}
		"""


    When bill团购购买jobs的商品
        """
        {
            "order_id":"0000001",
            "group_name": "团购1"
            "ship_name": "bill",
            "ship_tel": "13811223344",
            "ship_area": "北京市 北京市 海淀区",
            "ship_address": "泰兴大厦",
            "pay_type": "微信支付",
            "products": [{
                "name": "商品1",
                "count": 1
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
	Then bill能获得开团活动列表:weapp
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

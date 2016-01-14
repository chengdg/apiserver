#editor: benchi
#editor: 师帅 2015.10.20
#editor: 王丽 2015.12.25

Feature: 测试使用微众卡购买商品
	用户能通过webapp使用微众卡购买jobs的商品
	feathure里要加一个  "weizoom_card_money":50.00,的字段

Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
	And jobs已有微众卡支付权限:weapp
	And jobs已添加支付方式:weapp
		"""
		[{
			"type":"货到付款"
		},{
			"type":"微信支付"
		},{
			"type":"支付宝"
		},{
			"type":"微众卡支付"
		}]
		"""
	And jobs已添加商品:weapp
		"""
		[{
			"name": "商品2",
			"price": 88
		}]
		"""
	And jobs已创建微众卡:weapp
		"""
		{
			"cards":[{
				"id":"0000001",
				"password":"1234567",
				"status":"已使用",
				"price": 81.35
			},{
				"id":"0000002",
				"password":"1234567",
				"status":"未使用",
				"price":200.00
			}]
		}
		"""
	And bill关注jobs的公众号

@mall3 @mall2 @mall @mall.pay_weizoom_card @victor @wip.bpuc14
#对应Bug 7240
Scenario:14 用两张微众卡购买，第一张卡的金额大于商品金额
	商品金额：88元
	第一张卡金额：81.35元，使用金额：81.35元
	第二张卡金额：200元，使用金额：6.65元
	取消订单后
	第一张卡金额：6.65元
	第二张卡金额：200元

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id": "001",
			"pay_type": "微信支付",
			"products":[{
				"name":"商品2",
				"price":81.35,
				"count":1
			}],
			"weizoom_card":[{
				"card_name":"0000001",
				"card_pass":"1234567"
			},{
				"card_name":"0000002",
				"card_pass":"1234567"
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待发货",
			"final_price": 0.0,
			"product_price": 88,
			"weizoom_card_money": 88,
			"products":[{
				"name":"商品2",
				"price":88,
				"count":1
			}]
		}
		"""
	When bill取消订单'001'

	Given jobs登录系统:weapp
	Then jobs能获取微众卡'0000001'
		"""
		{
			"status":"已使用",
			"price":81.35
		}
		"""
	Then jobs能获取微众卡'0000002'
		"""
		{
			"status":"已使用",
			"price":200
		}
		"""

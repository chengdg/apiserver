#_author_:张三香 2015.12.25

Feature:校验多个下单错误提示信息
	"""
	下单时错误信息有如下几种:
		商品1-库存不足
		商品2-已售罄
		商品3-已下架
		商品4-已删除
		商品5-已经过期(买赠活动)
		商品6-限制购买(有限购周期)
		商品7-限购3件 （多规格 M S）
		商品8-已删除
	"""

Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
	And jobs已添加支付方式:weapp
		"""
		[{
			"type": "货到付款"
		}, {
			"type": "微信支付"
		}]
		"""
	And jobs已添加商品规格:weapp
		"""
		[{
			"name": "尺寸",
			"type": "文字",
			"values": [{
				"name": "M"
			}, {
				"name": "S"
			}]
		}]
		"""
	And jobs已添加商品:weapp
		"""
		[{
			"name": "商品1",
			"stock_type": "有限",
			"stocks": 2,
			"price": 10.0
		},{
			"name": "商品2",
			"stock_type": "有限",
			"stocks": 1,
			"price": 20.0
		},{
			"name": "商品3",
			"price": 30.0
		},{
			"name": "商品4",
			"price": 40.0
		},{
			"name": "商品5",
			"price": 50.0
		},{
			"name": "商品6",
			"price": 60.0
		},{
			"name": "商品7",
			"is_enable_model": "启用规格",
			"model": {
				"models": {
					"M": {
						"price": 70.0
						},
					"S": {
						"price": 70.0
					}
				}
			}
		},{
			"name": "赠品",
			"price": 10.0
		},{
			"name": "商品8",
			"price": 80.0
		}]
		"""
	When jobs创建买赠活动:weapp
		"""
		[{
			"name": "商品5买二赠一",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品5",
			"premium_products": [{
				"name": "赠品",
				"count": 1
			}],
			"count": 2,
			"is_enable_cycle_mode": true
		}]
		"""
	When jobs创建限时抢购活动:weapp
		"""
		[{
			"name": "商品6限时抢购",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品6",
			"member_grade": "全部",
			"promotion_price": 50.0,
			"limit_period": 1
		}, {
			"name": "商品7限时抢购",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品7",
			"member_grade": "全部",
			"count_per_purchase": 3,
			"promotion_price": 60.0
		}]
		"""
	Given bill关注jobs的公众号

@todo @mall.webapp @mall.promotion @wip.me1
Scenario:1 校验多个下单错误信息提示（错误信息类型不同）

	#bill购买有限购周期的商品-商品6
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type":"货到付款",
			"products": [{
				"name": "商品6",
				"count": 2
			}]
		}
		"""

	#bill加入多个商品到购物车
	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品6",
			"count": 2
		},{
			"name": "商品7",
			"model": {
				"models":{
					"M": {
						"count": 2
					}
				}
			}
		}, {
			"name": "商品7",
			"model": {
				"models":{
					"S": {
						"count": 2
					}
				}
			}
		}, {
			"name": "商品5",
			"count": 2
		}, {
			"name": "商品1",
			"count": 2
		}, {
			"name": "商品2",
			"count": 1
		}, {
			"name": "商品3",
			"count": 1
		}, {
			"name": "商品4",
			"count": 1
		}]
		"""

	#bill从购物车发起购买操作
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"context": [{
				"name": "商品6"
			},{
				"name": "商品7",
				"model":"M"
			}, {
				"name": "商品7",
				"model":"S"
			}, {
				"name": "商品5"
			}, {
				"name": "商品1"
			}, {
				"name": "商品2"
			}, {
				"name": "商品3"
			}, {
				"name": "商品4"
			
			}]
		}
		"""

	#jobs在台进行下架、删除等操作
	Given jobs登录系统:weapp
	#修改商品1的库存为1（由2变为1）
	When jobs更新商品'商品1':weapp
		"""
		{
			"name":"商品1",
			"stock_type": "有限",
			"stocks": 1
		}
		"""

	#修改商品2的库存为0
	When jobs更新商品'商品2':weapp
		"""
		{
			"name":"商品2",
			"stock_type": "有限",
			"stocks": 0
		}
		"""

	#下架商品3
	When jobs'下架'商品'商品3':weapp

	#删除商品4
	When jobs'删除'商品'商品4':weapp

	#结束商品5参与的买赠活动
	When jobs'结束'促销活动'商品5买二赠一':weapp

	#提交订单时校验多种错误提示信息
	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "微信支付"
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
			"detail": 
			[{
				"id": "商品6",
				"msg": "限制购买"
			},{
				"id": "商品7",
				"model":"M",
				"msg": "限购3件"
			},{
				"id": "商品7",
				"model":"S",
				"msg": "限购3件"
			},{
				"id": "商品5",
				"msg": "已经过期"
			},{
				"id": "商品1",
				"msg": "库存不足"
			},{
				"id": "商品2",
				"msg": "已售罄"
			},{
				"id": "商品3",
				"msg": "已下架"
			},{
				"id": "商品4",
				"msg": "已删除"
			}]
		}
		"""

@mall.webapp @mall.promotion
Scenario:2 校验多个下单错误信息提示（错误信息类型相同）

	When bill访问jobs的webapp
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品4",
			"count": 2
		}, {
			"name": "商品8",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"context": [{
			}, {
				"name": "商品4"
			}, {
				"name": "商品8"
			}]
		}
		"""

	#删除商品
		Given jobs登录系统
		When jobs'删除'商品'商品4'
		When jobs'删除'商品'商品8'

	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "微信支付"
		}
		"""
	Then bill获得创建订单失败的信息
			"""
			{
				"detail": 
				[{
					"id": "商品4",
					"msg": "已删除"
				},{
					"id": "商品8",
					"msg": "已删除"
				}]
			}
			"""
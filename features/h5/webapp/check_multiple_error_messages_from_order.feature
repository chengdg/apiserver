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
			"model": {
				"models": {
					"standard": {
						"user_code": "10",
						"stock_type": "有限",
						"stocks": 2,
						"price": 10.0
					}
				}
			}
		},{
			"name": "商品2",
			"model": {
				"models": {
					"standard": {
						"user_code": "20",
						"stock_type": "有限",
						"stocks": 1,
						"price": 20.0
					}
				}
			}
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

@mall3 @mall.webapp @mall.promotion @wip.me1
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
	When jobs更新商品'商品1'的库存为:weapp
		"""
		[{
			"name":"商品1",
			"user_code": "10",
			"stock_type": "有限",
			"stocks": 1
		}]
		"""

	#修改商品2的库存为0
	When jobs更新商品'商品2'的库存为:weapp
		"""
		[{
			"name":"商品2",
			"user_code": "20",
			"stock_type": "有限",
			"stocks": 0
		}]
		"""

	#下架商品3
	When jobs'下架'商品'商品3':weapp

	#删除商品4
	When jobs'永久删除'商品'商品4':weapp

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
				"id": "商品1",
				"short_msg": "库存不足"
			},{
				"id": "商品2",
				"short_msg": "商品已售罄"
			},{
				"id": "商品3",
				"short_msg": "商品已下架"
			},{
				"id": "商品4",
				"short_msg": "商品已删除"
			},{
				"id": "商品5",
				"short_msg": "已经过期"
			},{
				"id": "商品6",
				"msg": "在限购周期内不能多次购买"
			},{
				"id": "商品7",
				"model": "M",
				"msg": "限购3件"
			},{
				"id": "商品7",
				"model": "S",
				"msg": "限购3件"
			}]
		}
		"""


@mall3 @mall.webapp @mall.promotion @wip.cmemfo2
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
				"name": "商品4"
			}, {
				"name": "商品8"
			}]
		}
		"""

	#删除商品
	Given jobs登录系统:weapp
	When jobs'永久删除'商品'商品4':weapp
	When jobs'永久删除'商品'商品8':weapp

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
				"short_msg": "商品已删除"
			},{
				"id": "商品8",
				"short_msg": "商品已删除"
			}]
		}
		"""

#根据需求7312在手机编辑订单时,修改后台积分规则,提交订单时给出提示:商家调整积分，订单优惠金额信息变化，请重新下单！
#_author_:新新 2016.1.20
@mall.webapp @mall.promotion @wip.cmemfo2
Scenario:3 校验编辑订单页时后台修改积分规则(由小变大:1元=1积分修改1元=10元积分)
	1.jobs全局积分不变50%
	2.jobs修改积分规则

	Given jobs登录系统:weapp
	Given jobs设定会员积分策略:weapp
		"""
		{
			"integral_each_yuan": 1,
			"use_ceiling": 50
		}
		"""	

	When bill访问jobs的webapp
	When bill获得jobs的50会员积分
	Then bill在jobs的webapp中拥有50会员积分
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品5",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"pay_type": "微信支付",
			"context": [{
				"name": "商品5",
				"count": 1
			}]
		}
		"""
	
	Given jobs登录系统:weapp
	When jobs设定会员积分策略:weapp
		"""
		{
			"integral_each_yuan": 10,
			"use_ceiling": 50
		}
		"""
	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "微信支付",
			"integral_money":25.00,
			"integral":25
		}
		"""

	Then bill获得创建订单失败的信息
		"""
		{
			"detail": 
			{
				"商家调整积分，订单优惠金额信息变化，请重新下单！"
			}
		}
		"""
#_author_:新新 2016.1.20
@mall.webapp @mall.promotion @wip.cmemfo2
Scenario:4 校验编辑订单页时后台修改积分规则(由大变小:1元=10积分修改1元=1元积分)
	1.jobs全局积分不变50%
	2.jobs修改积分规则

	Given jobs登录系统:weapp
	Given jobs设定会员积分策略:weapp
		"""
		{
			"integral_each_yuan": 10,
			"use_ceiling": 50
		}
		"""	

	When bill访问jobs的webapp
	When bill获得jobs的50会员积分
	Then bill在jobs的webapp中拥有50会员积分
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品5",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"pay_type": "微信支付",
			"context": [{
				"name": "商品5",
				"count": 1
			}]
		}
		"""
	
	Given jobs登录系统:weapp
	When jobs设定会员积分策略:weapp
		"""
		{
			"integral_each_yuan": 1,
			"use_ceiling": 50
		}
		"""
	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "微信支付",
			"integral_money":5.00,
			"integral":50
		}
		"""

	Then bill获得创建订单失败的信息
		"""
		{
			"detail": 
			{
				"商家调整积分，订单优惠金额信息变化，请重新下单！"
			}
		}
		"""
#_author_:新新 2016.1.20
@mall.webapp @mall.promotion @wip.cmemfo2
Scenario:5 校验编辑订单页时后台修改积分规则(全局积分抵扣百分比由小变大:50%修改80%)
	1.jobs1元1积分不变
	2.jobs修改积分规则

	Given jobs登录系统:weapp
	Given jobs设定会员积分策略:weapp
		"""
		{
			"integral_each_yuan": 1,
			"use_ceiling": 50
		}
		"""	

	When bill访问jobs的webapp
	When bill获得jobs的50会员积分
	Then bill在jobs的webapp中拥有50会员积分
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品5",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"pay_type": "微信支付",
			"context": [{
				"name": "商品5",
				"count": 1
			}]
		}
		"""
	
	Given jobs登录系统:weapp
	When jobs设定会员积分策略:weapp
		"""
		{
			"integral_each_yuan": 1,
			"use_ceiling": 80
		}
		"""
	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "微信支付",
			"integral_money":25.00,
			"integral":25
		}
		"""

	Then bill获得创建订单失败的信息
		"""
		{
			"detail": 
			{
				"商家调整积分，订单优惠金额信息变化，请重新下单！"
			}
		}
		"""
#_author_:新新 2016.1.20
@mall.webapp @mall.promotion @wip.cmemfo2
Scenario:6 校验编辑订单页时后台修改积分规则(全局积分抵扣百分比由大变大:80%修改50%)
	1.jobs1元1积分不变
	2.jobs修改积分规则

	Given jobs登录系统:weapp
	Given jobs设定会员积分策略:weapp
		"""
		{
			"integral_each_yuan": 1,
			"use_ceiling": 80
		}
		"""	

	When bill访问jobs的webapp
	When bill获得jobs的50会员积分
	Then bill在jobs的webapp中拥有50会员积分
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品5",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"pay_type": "微信支付",
			"context": [{
				"name": "商品5",
				"count": 1
			}]
		}
		"""
	
	Given jobs登录系统:weapp
	When jobs设定会员积分策略:weapp
		"""
		{
			"integral_each_yuan": 1,
			"use_ceiling": 50
		}
		"""
	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "微信支付",
			"integral_money":40.00,
			"integral":40
		}
		"""

	Then bill获得创建订单失败的信息
		"""
		{
			"detail": 
			{
				"商家调整积分，订单优惠金额信息变化，请重新下单！"
			}
		}
		"""
#_author_:新新 2016.1.20
@mall.webapp @mall.promotion @wip.cmemfo2
Scenario:7 校验编辑订单页时后台修改积分规则(即修改全局积分抵扣百分比,又修改1元1积分的规则)
	1.jobs1元1积分修改成1元10积分
	2.jobs全局积分抵扣百分比50修改成80

	Given jobs登录系统:weapp
	Given jobs设定会员积分策略:weapp
		"""
		{
			"integral_each_yuan": 1,
			"use_ceiling": 50
		}
		"""

	When bill访问jobs的webapp
	When bill获得jobs的50会员积分
	Then bill在jobs的webapp中拥有50会员积分
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品5",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"pay_type": "微信支付",
			"context": [{
				"name": "商品5",
				"count": 1
			}]
		}
		"""
	
	Given jobs登录系统:weapp
	When jobs设定会员积分策略:weapp
		"""
		{
			"integral_each_yuan": 10,
			"use_ceiling": 80
		}
		"""
	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "微信支付",
			"integral_money":25.00,
			"integral":25
		}
		"""

	Then bill获得创建订单失败的信息
		"""
		{
			"detail": 
			{
				"商家调整积分，订单优惠金额信息变化，请重新下单！"
			}
		}
		"""
#_author_:新新 2016.1.20
@mall.webapp @mall.promotion @wip.cmemfo2
Scenario:8 校验编辑订单页时后台修改积分规则(全局'开启'到'关闭')
	1.jobs1元1积分
	2.jobs全局积分抵扣百分比50

	Given jobs登录系统:weapp
	Given jobs设定会员积分策略:weapp
		"""
		{
			"integral_each_yuan": 1,
			"use_ceiling": 50
		}
		"""

	When bill访问jobs的webapp
	When bill获得jobs的50会员积分
	Then bill在jobs的webapp中拥有50会员积分
	And bill加入jobs的商品到购物车
		"""
		[{
			"name": "商品5",
			"count": 1
		}]
		"""
	When bill从购物车发起购买操作
		"""
		{
			"action": "pay",
			"pay_type": "微信支付",
			"context": [{
				"name": "商品5",
				"count": 1
			}]
		}
		"""
	
	Given jobs登录系统:weapp
	#关闭全局,怎么写才算关闭呢,保留实现时再确定
	When jobs设定会员积分策略:weapp
		"""
		{
			"integral_each_yuan": 1,
			"use_ceiling": 0
		}
		"""
	When bill在购物车订单编辑中点击提交订单
		"""
		{
			"ship_name": "bill",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "微信支付",
			"integral_money":25.00,
			"integral":25
		}
		"""

	Then bill获得创建订单失败的信息
		"""
		{
			"detail": 
			{
				"商家调整积分，订单优惠金额信息变化，请重新下单！"
			}
		}
		"""

# __edit__ : "benchi"
#editor: 新新 2015.10.19

Feature: 在webapp中购买参与买赠活动的商品
"""
	用户能在webapp中购买"参与买赠活动的商品"

	# __edit__ : 王丽
	1、买赠活动的设置规则
		1）买赠活动的【主商品】所有"在售商品"单规格或者是多规格商品
		2）买赠活动的【赠品】不能是多规格商品，必须是单规格的在售商品
		3）买赠活动的主商品和赠品可以相同
		4）【广告语】：在商品名称后红字显示
		5）【会员等级】：设置什么等级的会员可以参加，下拉选项为：全部会员、会员等级中设置会员等级列表；选择"全部会员"或者单选一级会员
		6）【购买基数】：购买多少主商品，才能获得设定的一份赠品。
			”循环买赠“：勾选了，支持循环买赠；
			例：设置【购买基数为1】
			支持循环买赠：单个订单购买2个主商品，就会获得2份赠品
			不支持循环买赠：单个订单购买2个主商品，就会获得1分赠品
			买赠规则是针对单个订单的，多个订单不累计
			多规格商品，不区分规格，判断购买基数，发放赠品

	2、订单规则
		1）订单中赠品只显示赠品的名称和数量，不显示价格
		2）买赠的商品在订单中会显示整个的"商品件数"和"金额小计"
		3）会员既具有会员等级价又具有买赠活动的权限时
			达到买赠条件：商品原价购买，有赠品
			未达到买赠条件：商品会员价购买，无赠品

	3、设置了“限时抢购”的商品，不能再设置“买赠”“优惠券活动”，三个活动是互斥的，只要设置了其中的一个活动，就不能再设置其他两个活动		
"""

Background:
	Given jobs登录系统
	And jobs已添加商品规格
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
	And jobs已添加商品
		"""
		[{
			"name": "商品1",
			"price": 100.00,
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"stock_type": "有限",
						"stocks": 5
					}
				}
			}
		}, {
			"name": "商品2",
			"price": 200.00
		}, {
			"name": "商品3",
			"price": 50.00
		}, {
			"name": "商品4",
			"model": {
				"models": {
					"standard": {
						"price": 40.00,
						"stock_type": "有限",
						"stocks": 20
					}
				}
			}
		}, {
			"name": "商品5",
			"is_enable_model": "启用规格",
			"model": {
				"models":{
					"M": {
						"price": 7,
						"stock_type": "有限",
						"stocks": 2
					},
					"S": {
						"price": 8,
						"stock_type": "无限"
					}
				}
			}
		}]
		"""
	#支付方式
	Given jobs已添加支付方式
		"""
		[{
			"type": "微信支付",
			"is_active": "启用"
		}, {
			"type": "货到付款",
			"is_active": "启用"
		}]
		"""
	When jobs创建买赠活动
		"""
		[{
			"name": "商品1买二赠一",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品1",
			"premium_products": [{
				"name": "商品2",
				"count": 1
			}, {
				"name": "商品3",
				"count": 2
			}],
			"count": 2,
			"is_enable_cycle_mode": true
		}, {
			"name": "商品2买一赠一",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品2",
			"premium_products": [{
				"name": "商品4",
				"count": 5
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}, {
			"name": "商品5买一赠一",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品5",
			"premium_products": [{
				"name": "商品4",
				"count": 1
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	Given bill关注jobs的公众号
	And marry1关注jobs的公众号
	And marry2关注jobs的公众号
	And marry3关注jobs的公众号
	And marry4关注jobs的公众号

@mall2 @promotion @mall.promotion @mall.webapp.promotion
Scenario: 1 购买买赠商品，不满足买赠基数

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 100.00,
			"products": [{
				"name": "商品1",
				"count": 1,
				"promotion": null
			}]
		}
		"""

@mall2 @promotion @mall.promotion @mall.webapp.promotion
Scenario: 2 购买买赠活动商品，满足买赠基数

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 2
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 200.00,
			"products": [{
				"name": "商品1",
				"count": 2,
				"promotion": {
					"type": "premium_sale"
				}
			}, {
				"name": "商品2",
				"count": 1,
				"promotion": {
					"type": "premium_sale:premium_product"
				}
			}, {
				"name": "商品3",
				"count": 2,
				"promotion": {
					"type": "premium_sale:premium_product"
				}
			}]
		}
		"""

@mall2 @promotion @mall.promotion @mall.webapp.promotion
Scenario: 3 购买多个买赠活动商品，满足买赠基数，并满足循环买赠
	商品2满足循环买赠，赠品应该累加
	赠品数量刚好等于赠品库存

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 2
			}, {
				"name": "商品2",
				"count": 4
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 1000.00,
			"products": [{
				"name": "商品1",
				"count": 2,
				"promotion": {
					"type": "premium_sale"
				}
			}, {
				"name": "商品2",
				"count": 1,
				"promotion": {
					"type": "premium_sale:premium_product"
				}
			}, {
				"name": "商品3",
				"count": 2,
				"promotion": {
					"type": "premium_sale:premium_product"
				}
			}, {
				"name": "商品2",
				"count": 4,
				"promotion": {
					"type": "premium_sale"
				}
			}, {
				"name": "商品4",
				"count": 20,
				"promotion": {
					"type": "premium_sale:premium_product"
				}
			}]
		}
		"""

@mall2 @promotion @mall.promotion @mall.webapp.promotion
Scenario: 4 购买单个买赠商品，超出库存限制
	第一次购买2个，成功；第二次购买4个，超出商品库存，确保缓存更新

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 2
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 200.0
		}
		"""
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 4
			}]
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
			"detail": [{
				"id": "商品1",
				"msg": "有商品库存不足，请重新下单",
				"short_msg": "库存不足"
			}]
		}
		"""

@mall2 @promotion @mall.promotion @mall.webapp.promotion
Scenario: 5 购买单个买赠商品，赠品数量超出库存限制

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品2",
				"count": 5
			}]
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
			"detail": [{
				"id": "商品4",
				"msg": "库存不足",
				"short_msg": "库存不足"
			}]
		}
		"""

@mall2 @promotion @mall.promotion @mall.webapp.promotion
Scenario: 6 购买多个 有规格的参与买赠的商品

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品5",
				"model": "M",
				"count": 1
			}, {
				"name": "商品5",
				"model": "S",
				"count": 2
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 23.00,
			"products": [{
				"name": "商品5",
				"count": 1,
				"model": "M",
				"promotion": {
					"type": "premium_sale"
				}
			}, {
				"name": "商品5",
				"count": 2,
				"model": "S",
				"promotion": {
					"type": "premium_sale"
				}
			}, {
				"name": "商品4",
				"count": 3,
				"promotion": {
					"type": "premium_sale:premium_product"
				}
			}]
		}
		"""

@mall2 @promotion @mall.promotion @mall.webapp.promotion
Scenario: 7  创建多规格商品 非循环买赠活动，购买多个 有规格的参与买赠的商品 赠品只赠送一次
	Given jobs登录系统
	And jobs已添加商品
		"""
		[{
			"name": "商品6",
			"is_enable_model": "启用规格",
			"model": {
				"models":{
					"M": {
						"price": 7,
						"stock_type": "有限",
						"stocks": 2
					},
					"S": {
						"price": 8,
						"stock_type": "无限"
					}
				}
			}
		}]
		"""
	When jobs创建买赠活动
		"""
		[{
			"name": "商品6买一赠一",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品6",
			"premium_products": [{
				"name": "商品4",
				"count": 1
			}],
			"count": 1,
			"is_enable_cycle_mode": false
		}]
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品6",
				"model": "M",
				"count": 1
			}, {
				"name": "商品6",
				"model": "S",
				"count": 2
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 23.00,
			"products": [{
				"name": "商品6",
				"count": 1,
				"model": "M",
				"promotion": {
					"type": "premium_sale"
				}
			}, {
				"name": "商品6",
				"count": 2,
				"model": "S",
				"promotion": {
					"type": "premium_sale"
				}
			}, {
				"name": "商品4",
				"count": 1,
				"promotion": {
					"type": "premium_sale:premium_product"
				}
			}]
		}
		"""

@mall2 @promotion @mall.promotion @mall.webapp.promotion
Scenario: 8  多规格商品，买2赠1 循环买赠
	Given jobs登录系统
	And jobs已添加商品
		"""
		[{
			"name": "商品8",
			"is_enable_model": "启用规格",
			"model": {
				"models":{
					"M": {
						"price": 7,
						"stock_type": "无限"

					},
					"S": {
						"price": 8,
						"stock_type": "无限"
					}
				}
			}
		}]
		"""

	When jobs创建买赠活动
		"""
		[{
			"name": "商品8买二赠一",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品8",
			"premium_products": [{
				"name": "商品4",
				"count": 1
			}],
			"count": 2,
			"is_enable_cycle_mode": true
		}]
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品8",
				"model": "M",
				"count": 1
			}, {
				"name": "商品8",
				"model": "S",
				"count": 1
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 15.00,
			"products": [{
				"name": "商品8",
				"count":1,
				"model": "M",
				"promotion": {
					"type": "premium_sale"
				}
			}, {
				"name": "商品8",
				"count": 1,
				"model": "S",
				"promotion": {
					"type": "premium_sale"
				}
			}, {
				"name": "商品4",
				"count": 1,
				"promotion": {
					"type": "premium_sale:premium_product"
				}
			}]
		}
		"""

@mall2 @promotion @mall.promotion @mall.webapp.promotion
Scenario: 9  创建买赠活动，但活动时间没开始，按原有商品销售，不进行赠送
	Given jobs登录系统
	And jobs已添加商品
		"""
		[{
			"name": "商品9",
			"price": 200.00
		}]
		"""
	When jobs创建买赠活动
		"""
		[{
			"name": "商品9买1赠1",
			"start_date": "1天后",
			"end_date": "3天后",
			"product_name": "商品9",
			"premium_products": [{
				"name": "商品4",
				"count": 1
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品9",
				"count": 1
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 200.00,
			"products": [{
				"name": "商品9",
				"count":1
			}]
		}
		"""

@mall2 @promotion @mall.promotion @mall.webapp.promotion
Scenario: 10  创建买赠活动，但活动时间没开始，按原有商品销售，不进行赠送
	Given jobs登录系统
	And jobs已添加商品
		"""
		[{
			"name": "商品9",
			"price": 200.00
		}]
		"""
	When jobs创建买赠活动
		"""
		[{
			"name": "商品9买1赠1",
			"start_date": "1天后",
			"end_date": "3天后",
			"product_name": "商品9",
			"premium_products": [{
				"name": "商品4",
				"count": 1
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品9",
				"count": 1
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 200.00,
			"products": [{
				"name": "商品9",
				"count":1
			}]
		}
		"""

@mall2 @promotion @mall.promotion @mall.webapp.promotion
Scenario: 11  创建买赠活动，选择商品时，活动进行中，但去付款时，活动已经结束了，系统提示：该活动已经过期
	Given jobs登录系统
	And jobs已添加商品
		"""
		[{
			"name": "商品10",
			"price": 200.00
		}]
		"""
	When jobs创建买赠活动
		"""
		[{
			"name": "商品10买1赠1",
			"start_date": "2天前",
			"end_date": "1天前",
			"product_name": "商品10",
			"premium_products": [{
				"name": "商品4",
				"count": 1
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品10",
				"count": 1
			}]
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
			"detail": [{
				"id": "商品10",
				"msg": "该活动已经过期",
				"short_msg": "已经过期"
			}]
		}
		"""

@mall2 @promotion @mall.promotion @mall.webapp.promotion
Scenario: 12 购买单个买赠活动商品，购买时活动进行中，提交订单时，该活动被商家手工结束

	Given jobs登录系统
	And jobs已添加商品
		"""
		[{
			"name": "商品10",
			"price": 200.00
		}]
		"""
	When jobs创建买赠活动
		"""
		[{
			"name": "商品10买1赠1",
			"start_date": "1天前",
			"end_date": "3天后",
			"product_name": "商品10",
			"premium_products": [{
				"name": "商品4",
				"count": 1
			}],
			"count": 1,
			"is_enable_cycle_mode": true
		}]
		"""
	Given jobs登录系统
	When jobs"结束"促销活动"商品10买1赠1"
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品10",
				"count": 1,
				"promotion": {
					"name": "商品10买1赠1"
				}
			}]
		}
		"""

	Then bill获得创建订单失败的信息
		"""
		{
			"detail": [{
				"id": "商品10",
				"msg": "该活动已经过期",
				"short_msg": "已经过期"
			}]
		}
		"""

# __edit__ : 王丽   补充 "雪静"
@mall2 @promotion @promotionPremium @meberGrade
Scenario: 13 不同等级的会员购买会员价，同时有会员等级买赠活动的商品
	Given jobs登录系统
	When jobs添加会员等级
		"""
		[{
			"name": "铜牌会员",
			"upgrade": "手动升级",
			"discount": "9"
		}, {
			"name": "银牌会员",
			"upgrade": "手动升级",
			"discount": "8"
		}, {
			"name": "金牌会员",
			"upgrade": "手动升级",
			"discount": "7"
		}]
		"""
	And jobs已添加商品
		"""
		[{
			"name": "商品赠品",
			"is_member_product": "on",
			"model": {
				"models": {
					"standard": {
						"price": 10.00,
						"stock_type": "有限",
						"stocks": 100
					}
				}
			}
		},{
			"name": "商品6",
			"is_member_product": "on",
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"stock_type": "有限",
						"stocks": 100
					}
				}
			}
		},{
			"name": "商品7",
			"is_member_product": "on",
			"is_enable_model": "启用规格",
			"model": {
				"models":{
					"M": {
						"price": 300,
						"stock_type": "无限"
					},
					"S": {
						"price": 300,
						"stock_type": "无限"
					}
				}
			}
		},{
			"name": "商品8",
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"stock_type": "有限",
						"stocks": 100
					}
				}
			}
		}]
		"""
	When jobs更新"marry2"的会员等级
		"""
		{
			"name":"marry2",
			"member_rank":"铜牌会员"
		}
		"""
	And jobs更新"marry3"的会员等级
		"""
		{
			"name":"marry3",
			"member_rank":"银牌会员"
		}
		"""
	And jobs更新"marry4"的会员等级
		"""
		{
			"name":"marry4",
			"member_rank":"金牌会员"
		}
		"""
	Then jobs可以获得会员列表
		"""
		[{
			"name":"marry4",
			"member_rank":"金牌会员"
		}, {
			"name":"marry3",
			"member_rank":"银牌会员"
		}, {
			"name":"marry2",
			"member_rank":"铜牌会员"
		}, {
			"name":"marry1",
			"member_rank":"普通会员"
		}, {
			"name":"bill",
			"member_rank":"普通会员"
		}]
		"""
	When jobs创建买赠活动
		"""
		[{
			"name": "商品6买一赠二",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品6",
			"premium_products": [{
				"name": "商品6",
				"count": 1
			},{
				"name": "商品赠品",
				"count": 1
			}],
			"count": 1,
			"member_grade":"金牌会员",
			"is_enable_cycle_mode": true
		},{
			"name": "商品7买二赠二",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品7",
			"premium_products": [{
				"name": "商品赠品",
				"count": 2
			}],
			"count": 2,
			"member_grade":"全部",
			"is_enable_cycle_mode": true
		},{
			"name": "商品8买一赠一",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品8",
			"premium_products": [{
				"name": "商品赠品",
				"count": 1
			}],
			"count": 1,
			"member_grade":"铜牌会员",
			"is_enable_cycle_mode": true
		}]
		"""

	#购买有单会员等级买赠活动，无会员价商品"商品8"
	#普通会员等级的会员marry1,购买铜牌会员等级买赠活动商品"商品8"，按照原价购买，无赠品
	When marry1访问jobs的webapp
	And marry1购买jobs的商品
		"""
		{
			"ship_name": "marry1",
			"ship_tel": "12345678911",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"products": [{
				"name": "商品8",
				"count": 1
			}]
		}
		"""
	Then marry1成功创建订单
		"""
		{
			"status": "待支付",
			"ship_name": "marry1",
			"ship_tel": "12345678911",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"final_price": 100.0,
			"products": [{
				"name": "商品8",
				"price": 100.0,
				"grade_discounted_money":0.00,
				"count": 1
			}]
		}
		"""

	#铜牌会员等级的会员marry2,购买铜牌会员等级买赠活动商品"商品8"，按照原价购买，有赠品
	When marry2访问jobs的webapp
	And marry2购买jobs的商品
		"""
		{
			"ship_name": "marry2",
			"ship_tel": "12345678912",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦2",
			"products": [{
				"name": "商品8",
				"count": 1
			}]
		}
		"""
	Then marry2成功创建订单
		"""
		{
			"status": "待支付",
			"ship_name": "marry2",
			"ship_tel": "12345678912",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦2",
			"final_price": 100.0,
			"products": [{
				"name": "商品8",
				"price": 100.0,
				"grade_discounted_money":0.00,
				"count": 1
			},{
				"name": "商品赠品",
				"price": 0.0,
				"count": 1
			}]
		}
		"""

	#购买有单会员等级买赠活动，有会员价商品"商品6"
	#铜牌会员等级的会员marry2,购买金牌会员等级买赠活动商品"商品6"，按照会员价购买，无赠品
	When marry2访问jobs的webapp
	And marry2购买jobs的商品
		"""
		{
			"ship_name": "marry2",
			"ship_tel": "12345678912",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦2",
			"products": [{
				"name": "商品6",
				"count": 1
			}]
		}
		"""
	Then marry2成功创建订单
		"""
		{
			"status": "待支付",
			"ship_name": "marry2",
			"ship_tel": "12345678912",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦2",
			"final_price": 90.0,
			"products": [{
				"name": "商品6",
				"price": 90.0,
				"grade_discounted_money":10.00,
				"count": 1
			}]
		}
		"""

	#金牌会员等级的会员marry4,购买金牌会员等级买赠活动商品"商品6"，按照原价购买，有赠品
	When marry4访问jobs的webapp
	And marry4购买jobs的商品
		"""
		{
			"ship_name": "marry4",
			"ship_tel": "12345678914",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦4",
			"products": [{
				"name": "商品6",
				"count": 1
			}]
		}
		"""
	Then marry4成功创建订单
		"""
		{
			"status": "待支付",
			"ship_name": "marry4",
			"ship_tel": "12345678914",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦4",
			"final_price": 100.0,
			"products": [{
				"name": "商品6",
				"price": 100.0,
				"grade_discounted_money": 0.00,
				"count": 1
			},{
				"name": "商品6",
				"count": 1
			},{
				"name": "商品赠品",
				"price": 0.0,
				"count": 1
			}]
		}
		"""

	#购买全部会员等级买赠活动，有会员价多规格商品"商品7"
	#铜牌会员等级的会员marry2,购买全部会员等级买赠活动，有会员价商品"商品7"，单规格没有达到买赠数量条件，按照会员价购买，无赠品
	When marry2访问jobs的webapp
	And marry2购买jobs的商品
		"""
		{
			"ship_name": "marry2",
			"ship_tel": "12345678912",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦2",
			"products": [{
				"name": "商品7",
				"model": "M",
				"count": 1
			}]
		}
		"""
	Then marry2成功创建订单
		"""
		{
			"status": "待支付",
			"ship_name": "marry2",
			"ship_tel": "12345678912",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦2",
			"final_price": 270.00,
			"products": [{
				"name": "商品7",
				"model": "M",
				"price": 270.00,
				"count": 1
			}]
		}
		"""

	#银牌会员等级的会员marry3,购买全部会员等级买赠活动，有会员价商品"商品7"，整体数量达到买赠数量条件，单规格没有达到买赠数量条件，按照原价购买，有赠品
	When marry3访问jobs的webapp
	And marry3购买jobs的商品
		"""
		{
			"ship_name": "marry3",
			"ship_tel": "12345678913",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦3",
			"products": [{
				"name": "商品7",
				"model": "M",
				"count": 1
			},{
				"name": "商品7",
				"model": "S",
				"count": 1
			}]
		}
		"""
	Then marry3成功创建订单
		"""
		{
			"status": "待支付",
			"ship_name": "marry3",
			"ship_tel": "12345678913",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦3",
			"final_price": 600.0,
			"products": [{
				"name": "商品7",
				"model": "M",
				"price": 300.0,
				"count": 1
			},{
				"name": "商品7",
				"model": "S",
				"price": 300.0,
				"count": 1
			},{
				"name": "商品赠品",
				"price": 0.0,
				"count": 2
			}]
		}
		"""

	#金牌会员等级的会员marry4,购买全部会员等级买赠活动，有会员价商品"商品7"，整体数量达到买赠数量条件，单规格达到买赠数量条件，按照原价购买，有赠品
	When marry4访问jobs的webapp
	And marry4购买jobs的商品
		"""
		{
			"ship_name": "marry4",
			"ship_tel": "12345678914",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦4",
			"products": [{
				"name": "商品7",
				"model": "M",
				"count": 3
			},{
				"name": "商品7",
				"model": "S",
				"count": 3
			}]
		}
		"""
	Then marry4成功创建订单
		"""
		{
			"status": "待支付",
			"ship_name": "marry4",
			"ship_tel": "12345678914",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦4",
			"final_price": 1800.0,
			"products": [{
				"name": "商品7",
				"model": "M",
				"price": 300.0,
				"grade_discounted_money":0.00,
				"count": 3
			},{
				"name": "商品7",
				"model": "S",
				"price": 300.0,
				"grade_discounted_money":0.00,
				"count": 3
			},{
				"name": "商品赠品",
				"price": 0.0,
				"count": 6
			}]
		}
		"""

# __edit__ : "benchi"
#editor: 新新 2015.10.16

Feature: 在webapp中购买参与积分应用活动的商品
"""
	用户能在webapp中购买"参与积分应用活动的商品"

	# __edit__ : 王丽
	1、积分活动设置规则
		1）【广告语】：在商品名称后红字显示
		2）【比例设置】：设置商品的积分抵扣上限，积分抵扣金额：【抵扣金额】=【商品数量】*【商品单价】*【抵扣上限】
			（1）统一设置：
				为全部等级的会员设置统一的积分抵扣上限
			（2）分级设置：
				为系统中所有等级的会员分别设置积分抵扣上限
		3）【活动时间】：开始结束时间只能选择今天及其之后的时间，结束时间必须在开始时间之后
			勾选"永久"，清空活动时间，此活动永久有效，除非手动结束活动

	2、结束积分活动
		‘进行中’的积分活动，可以手动的结束
		‘永久’和‘非永久’的积分活动，一旦结束在购买时就不能使用了
	3、删除积分活动
		‘结束’和‘未开始’的积分活动才可以删除
	4、积分使用规则
		1）积分和优惠券不能在同一个订单中同时使用，即使两个活动针对的是不同的商品
		2）一个订单包含多个具有积分活动的商品，每个商品分别使用自己的积分活动
		3）会员既具有会员等级价又具有会员积分活动权限的，会员看到的商品显示会员价，购买时会员价下单，并在会员价的基础上使用积分抵扣，
			积分抵扣的上限，按照会员价计算
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
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"stock_type": "有限",
						"stocks": 2
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
						"price": 40.00,
						"stock_type": "无限"
					},
					"S": {
						"price": 40.00,
						"stock_type": "无限"
					}
				}
			}
		}]
		"""
	Given jobs设定会员积分策略
		"""
		{
			"integral_each_yuan": 2
		}
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
	When jobs创建积分应用活动
		"""
		[{
			"name": "商品1积分应用",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品1",
			"is_permanant_active": false,
			"rules": [{
				"member_grade": "全部",
				"discount": 70,
				"discount_money": 70.0
			}]
		}, {
			"name": "商品3积分应用",
			"start_date": "今天",
			"end_date": "2天后",
			"product_name": "商品3",
			"is_permanant_active": true,
			"rules": [{
				"member_grade": "全部",
				"discount": 50,
				"discount_money": 25.0
			}]
		}, {
			"name": "商品5积分应用",
			"start_date": "今天",
			"end_date": "2天后",
			"product_name": "商品5",
			"is_permanant_active": true,
			"rules": [{
				"member_grade": "全部",
				"discount": 50,
				"discount_money": 20.0
			}]
		}]
		"""
	Given bill关注jobs的公众号

@mall2 @promotion @mall.promotion @mall.webapp.promotion @mall.promotion.integral
Scenario: 1 购买单个积分折扣商品，积分金额小于最大折扣金额

	When bill访问jobs的webapp
	When bill获得jobs的50会员积分
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1,
				"integral": 50
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 75.0,
			"product_price": 100.00,
			"promotion_saved_money": 0.00,
			"postage": 0.00,
			"integral_money":25.00,
			"coupon_money":0.00,
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	Then bill在jobs的webapp中拥有0会员积分

@mall2 @promotion @mall.promotion @mall.webapp.promotion @mall.promotion.integral 
Scenario: 2 购买单个积分折扣商品，积分金额等于最大折扣金额

	When bill访问jobs的webapp
	When bill获得jobs的150会员积分
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1,
				"integral": 140
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 30.0,
			"product_price": 100.00,
			"promotion_saved_money": 0.00,
			"postage": 0.00,
			"integral_money":70.00,
			"coupon_money":0.00,
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	Then bill在jobs的webapp中拥有10会员积分

@mall2 @promotion @mall.promotion @mall.webapp.promotion @mall.promotion.integral
Scenario: 3 购买单个积分折扣商品，积分金额大于最大折扣金额

	When bill访问jobs的webapp
	When bill获得jobs的150会员积分
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1,
				"integral": 150
			}]
		}
		"""
	Then bill获得创建订单失败的信息'使用积分不能大于促销限额'
	Then bill在jobs的webapp中拥有150会员积分

@mall2 @promotion @mall.promotion @mall.webapp.promotion @mall.promotion.integral
Scenario: 4 购买多个积分折扣商品，总积分金额小于最大折扣金额

	When bill访问jobs的webapp
	When bill获得jobs的150会员积分
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1,
				"integral": 100
			}, {
				"name": "商品3",
				"count": 1,
				"integral": 50
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 75.0,
			"product_price": 150.00,
			"promotion_saved_money": 0.00,
			"postage": 0.00,
			"integral_money":75.00,
			"coupon_money":0.00,
			"products": [{
				"name": "商品1",
				"count": 1
			}, {
				"name": "商品3",
				"count": 1
			}]
		}
		"""
	Then bill在jobs的webapp中拥有0会员积分

@mall2 @promotion @mall.promotion @mall.webapp.promotion @mall.promotion.integral 
Scenario: 5 购买单个积分折扣商品，积分活动还未开始
	积分活动还未开始，按原价下单

	Given jobs登录系统
	When jobs创建积分应用活动
		"""
		[{
			"name": "商品4积分应用",
			"start_date": "1天后",
			"end_date": "2天后",
			"product_name": "商品4",
			"is_permanant_active": false,
			"rules": [{
				"member_grade": "全部",
				"discount": 50,
				"discount_money": 20.0
			}]
		}]
		"""
	When bill访问jobs的webapp
	When bill获得jobs的150会员积分

	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品4",
				"count": 1,
				"integral": 0
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 40.0,
			"product_price": 40.00,
			"promotion_saved_money": 0.00,
			"postage": 0.00,
			"integral_money":0.00,
			"coupon_money":0.00,
			"products": [{
				"name": "商品4",
				"count": 1
			}]
		}
		"""
	Then bill在jobs的webapp中拥有150会员积分

@mall2 @promotion @mall.promotion @mall.webapp.promotion @mall.promotion.integral
Scenario: 6 购买单个积分折扣商品，积分活动已结束，积分活动不是永久有效
	积分活动还未开始，按原价下单

	Given jobs登录系统
	When jobs创建积分应用活动
		"""
		[{
			"name": "商品4积分应用",
			"start_date": "昨天",
			"end_date": "今天",
			"product_name": "商品4",
			"is_permanant_active": false,
			"rules": [{
				"member_grade": "全部",
				"discount": 50,
				"discount_money": 20.0
			}]
		}]
		"""
	When bill访问jobs的webapp
	When bill获得jobs的150会员积分
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品4",
				"count": 1,
				"integral": 40
			}]
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
			"detail": [{
				"id": "商品4",
				"msg": "积分折扣已经过期",
				"short_msg": "已经过期"
			}]
		}
		"""
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品4",
				"count": 1,
				"integral": 0
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 40.0,
			"product_price": 40.00,
			"integral_money": 0.00,
			"products": [{
				"name": "商品4"
			}]
		}
		"""
	Then bill在jobs的webapp中拥有150会员积分

@mall2 @promotion @mall.promotion @mall.webapp.promotion @mall.promotion.integral
Scenario: 7 购买单个积分折扣商品，积分活动时间已结束，但积分活动设置为永久有效
	积分活动永久有效，按积分折扣后的价格下单

	Given jobs登录系统
	When jobs创建积分应用活动
		"""
		[{
			"name": "商品4积分应用",
			"start_date": "2天前",
			"end_date": "1天前",
			"product_name": "商品4",
			"is_permanant_active": true,
			"rules": [{
				"member_grade": "全部",
				"discount": 50,
				"discount_money": 20.0
			}]
		}]
		"""
	When bill访问jobs的webapp
	When bill获得jobs的150会员积分
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品4",
				"count": 1,
				"integral": 40
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 20.0,
			"product_price": 40.00,
			"integral_money": 20.00,
			"products": [{
				"name": "商品4",
				"count": 1
			}]
		}
		"""
	Then bill在jobs的webapp中拥有110会员积分

@mall2 @promotion @mall.promotion @mall.webapp.promotion @mall.promotion.integral
Scenario: 8 购买单个积分折扣商品，超出库存限制 后台进行库存数量验证
	第一次购买1个，成功；第二次购买2个，超出商品库存，确保缓存更新

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
			"status": "待支付"
		}
		"""
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 2
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

@mall2 @promotion @mall.promotion @mall.webapp.promotion @mall.promotion.integral 
Scenario: 9 购买单个,多规格积分折扣商品，积分活动已结束，但积分活动设置为永久有效
	积分活动永久有效，按积分折扣后的价格下单

	Given jobs登录系统
	When jobs创建积分应用活动
		"""
		[{
			"name": "商品5积分应用",
			"start_date": "昨天",
			"end_date": "今天",
			"product_name": "商品5",
			"is_permanant_active": true,
			"rules": [{
				"member_grade": "全部",
				"discount": 50,
				"discount_money": 20.0
			}]
		}]
		"""
	When bill访问jobs的webapp
	When bill获得jobs的150会员积分
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品5",
				"count": 1,
				"integral": 40,
				"model": "S"
			}, {
				"name": "商品5",
				"count": 1,
				"integral": 40,
				"model": "M"
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 40.0,
			"product_price": 80.00,
			"integral_money": 40.00,
			"products": [{
				"name": "商品5",
				"count": 1,
				"model": "S"
			}, {
				"name": "商品5",
				"count": 1,
				"model": "M"
			}]
		}
		"""
	Then bill在jobs的webapp中拥有70会员积分

@mall2 @promotion @mall.promotion @mall.webapp.promotion
Scenario: 10 购买单个积分应用活动商品，购买时活动进行中，提交订单时，该活动被商家手工结束

	Given jobs登录系统
	When jobs创建积分应用活动
		"""
		[{
			"name": "商品4积分应用",
			"start_date": "2天前",
			"end_date": "1天前",
			"product_name": "商品4",
			"is_permanant_active": true,
			"rules": [{
				"member_grade": "全部",
				"discount": 50,
				"discount_money": 20.0
			}]
		}]
		"""
	When bill访问jobs的webapp
	When bill获得jobs的150会员积分

	Given jobs登录系统
	When jobs"结束"促销活动"商品4积分应用"
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品4",
				"count": 1,
				"integral": 40
			}]
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
			"detail": [{
				"id": "商品4",
				"msg": "积分折扣已经过期",
				"short_msg": "已经过期"
			}]
		}
		"""
	When bill访问jobs的webapp
	Then bill在jobs的webapp中拥有150会员积分

#补充：张三香
@mall2 @promotion @integral @meberGrade
Scenario: 11 不同等级的会员购买有会员价同时有积分统一设置抵扣5的商品
	#会员价和积分抵扣可以同时使用，会员价后再算积分抵扣的比例
	When tom1关注jobs的公众号
	And tom2关注jobs的公众号
	And tom3关注jobs的公众号
	And tom4关注jobs的公众号
	Given jobs登录系统
	And jobs已添加商品
		"""
		[{
			"name": "商品10",
			"price": 100.00,
			"is_member_product": "on"
		},{
			"name": "商品11",
			"price": 100.00,
			"is_member_product": "on"
		}]
		"""
	When jobs创建积分应用活动
		"""
		[{
			"name": "商品11积分应用",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品11",
			"is_permanant_active": false,
			"rules": [{
				"member_grade": "全部",
				"discount": 50,
				"discount_money": 50.0
				}]
		}]
		"""
	When jobs添加会员等级
		"""
		[{
			"name": "铜牌会员",
			"discount": "9"
		},{
			"name": "银牌会员",
			"discount": "8"
		},{
			"name": "金牌会员",
			"discount": "7"
		}]
		"""
	When jobs更新"tom2"的会员等级
		"""
		{
			"name": "tom2",
			"member_rank": "铜牌会员"
		}
		"""
	When jobs更新"tom3"的会员等级
		"""
		{
			"name": "tom4",
			"member_rank": "银牌会员"
		}
		"""
	When jobs更新"tom4"的会员等级
		"""
		{
			"name": "tom4",
			"member_rank": "金牌会员"
		}
		"""
	Then jobs可以获得会员列表
		"""
		[{
			"name": "tom4",
			"member_rank": "金牌会员"
		}, {
			"name": "tom3",
			"member_rank": "银牌会员"
		}, {
			"name": "tom2",
			"member_rank": "铜牌会员"
		}, {
			"name": "tom1",
			"member_rank": "普通会员"
		}, {
			"name": "bill",
			"member_rank": "普通会员"
		}]
		"""

	#1101会员tom1购买商品11，使用积分抵扣最高：50元，订单金额：50元
	When tom1访问jobs的webapp
	When tom1获得jobs的100会员积分
	When tom1购买jobs的商品
		"""
		{
			"products": [{
				"integral_money":50.00,
				"integral":100.00,
				"name": "商品11",
				"count": 1
			}]
		}
		"""
	Then tom1成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 50.0,
			"product_price": 100.00,
			"promotion_saved_money": 0.00,
			"postage": 0.00,
			"coupon_money":0.00,
			"integral_money":50.00,
			"integral":100.00,
			"products": [{
				"name": "商品11",
				"price": 100.0,
				"grade_discounted_money": 0.0,
				"count": 1
			}]
		}
		"""
	Then tom1在jobs的webapp中拥有0会员积分

	#1102会员tom2购买商品11，使用积分抵扣最高：45元，订单金额：45元
	When tom2访问jobs的webapp
	When tom2获得jobs的200会员积分
	When tom2购买jobs的商品
		"""
		{
			"products": [{
				"integral_money":45.00,
				"integral":90.00,
				"name": "商品11",
				"count": 1
			}]
		}
		"""
	Then tom2成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 45.0,
			"product_price": 90.00,
			"promotion_saved_money": 0.00,
			"postage": 0.00,
			"integral_money":45.00,
			"integral":90.00,
			"coupon_money":0.00,
			"products": [{
				"name": "商品11",
				"price": 90.0,
				"grade_discounted_money": 10.0,
				"count": 1
			}]
		}
		"""
	Then tom2在jobs的webapp中拥有110会员积分

	#1103会员tom4购买商品10+商品11，使用积分抵扣最高：35元，订单金额：105元
	When tom4访问jobs的webapp
	When tom4获得jobs的400会员积分
	When tom4购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品10",
				"count": 1
			},{
			    "name": "商品11",
				"count": 1,
				"integral_money":35.00,
				"integral":70.00
			}]
		}
		"""
	Then tom4成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 105.0,
			"product_price": 140.00,
			"promotion_saved_money": 0.00,
			"postage": 0.00,
			"integral_money":35.00,
			"integral":70.00,
			"coupon_money":0.00,
			"products": [{
				"name": "商品10",
				"price": 70.0,
				"grade_discounted_money": 30.0,
				"count": 1
			},{
				"name": "商品11",
				"price": 70.0,
				"grade_discounted_money": 30.0,
				"count": 1
			}]
		}
		"""
	Then bill在jobs的webapp中拥有330会员积分

@mall2 @promotion
Scenario: 12 不同等级的会员购买有会员价同时有根据等级设置积分抵扣的商品
	#会员价和积分抵扣可以同时使用，会员价后再算积分抵扣的比例

	Given bill1关注jobs的公众号
	And bill2关注jobs的公众号
	And bill3关注jobs的公众号
	And bill4关注jobs的公众号
	And jobs登录系统
	And jobs已添加商品
		"""
		[{
			"name": "商品12",
			"price": 100.00,
			"is_member_product": "on"
		}]
		"""

	When jobs添加会员等级
		"""
		[{
			"name": "铜牌会员",
			"discount": "9"
		}, {
			"name": "银牌会员",
			"discount": "8"
		}, {
			"name": "金牌会员",
			"discount": "7"
		}]
		"""
	When jobs更新"bill2"的会员等级
		"""
		{
			"name": "bill2",
			"member_rank": "铜牌会员"
		}
		"""
	When jobs更新"bill3"的会员等级
		"""
		{
			"name": "bill3",
			"member_rank": "银牌会员"
		}
		"""
	When jobs更新"bill4"的会员等级
		"""
		{
			"name": "bill4",
			"member_rank": "金牌会员"
		}
		"""
	Then jobs可以获得会员列表
		"""
		[{
			"name": "bill4",
			"member_rank": "金牌会员"
		}, {
			"name": "bill3",
			"member_rank": "银牌会员"
		}, {
			"name": "bill2",
			"member_rank": "铜牌会员"
		}, {
			"name": "bill1",
			"member_rank": "普通会员"
		}, {
			"name": "bill",
			"member_rank": "普通会员"
		}]
		"""
	When jobs创建积分应用活动
		"""
		[{
			"name": "商品12积分应用",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品12",
			"is_permanant_active": false,
			"rules": 
			[{
				"member_grade": "普通会员",
				"discount": 100,
				"discount_money": 100.0
			},{
				"member_grade": "铜牌会员",
				"discount": 90,
				"discount_money": 90.0
			},{
				"member_grade": "银牌会员",
				"discount": 80,
				"discount_money": 80.0
			},{
				"member_grade": "金牌会员",
				"discount": 70,
				"discount_money": 70.0
			}]
		}]
		"""

	#1201会员bill1购买商品12，使用积分抵扣最高：100元，订单金额：0元
	When bill1访问jobs的webapp
	When bill1获得jobs的200会员积分
	When bill1购买jobs的商品
		"""
		{
			"products": [{
				"integral_money":100.00,
				"integral":200.00,
				"name": "商品12",
				"count": 1
			}]
		}
		"""
	Then bill1成功创建订单
		"""
		{
			"status": "待发货",
			"final_price": 0.00,
			"product_price": 100.00,
			"promotion_saved_money": 0.00,
			"postage": 0.00,
			"coupon_money":0.00,
			"integral_money":100.00,
			"integral":200.00,
			"products": [{
				"price": 100.0,
				"grade_discounted_money": 0.0,
				"name": "商品12",
				"count": 1
			}]
		}
		"""
	Then bill1在jobs的webapp中拥有0会员积分

	#1202会员bill2购买商品12，使用积分抵扣最高：81元，订单金额：9元
	When bill2访问jobs的webapp
	When bill2获得jobs的300会员积分
	When bill2购买jobs的商品
		"""
		{
			"products": [{
				"integral_money":81.00,
				"integral":162.00,
				"name": "商品12",
				"count": 1
			}]
		}
		"""
	Then bill2成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 9.00,
			"product_price": 90.00,
			"promotion_saved_money": 0.00,
			"postage": 0.00,
			"coupon_money":0.00,
			"integral_money":81.00,
			"integral":162.00,
			"products": [{
				"price": 90.0,
				"grade_discounted_money": 10.0,
				"name": "商品12",
				"count": 1
			}]
		}
		"""
	Then bill2在jobs的webapp中拥有138会员积分

	#1203会员bill3购买商品12，使用积分抵扣最高：64元，订单金额：16元
	When bill3访问jobs的webapp
	When bill3获得jobs的400会员积分
	When bill3购买jobs的商品
		"""
		{
			"products": [{
				"integral_money":64.00,
				"integral":128.00,
				"name": "商品12",
				"count": 1
			}]
		}
		"""
	Then bill3成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 16.00,
			"product_price": 80.00,
			"promotion_saved_money": 0.00,
			"postage": 0.00,
			"coupon_money":0.00,
			"integral_money":64.00,
			"integral":128.00,
			"products": [{
				"price": 80.0,
				"grade_discounted_money": 20.0,
				"name": "商品12",
				"count": 1
			}]
		}
		"""
	Then bill3在jobs的webapp中拥有272会员积分

	#1204会员bill4购买商品12，使用积分抵扣最高：49元，订单金额：21元
	When bill4访问jobs的webapp
	When bill4获得jobs的500会员积分
	When bill4购买jobs的商品
		"""
		{
			"products": [{
				"integral_money":49.00,
				"integral":98.00,
				"name": "商品12",
				"count": 1
			}]
		}
		"""
	Then bill4成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 21.00,
			"product_price": 70.00,
			"promotion_saved_money": 0.00,
			"postage": 0.00,
			"coupon_money":0.00,
			"integral_money":49.00,
			"integral":98.00,
			"products": [{
				"price": 70.0,
				"grade_discounted_money": 30.0,
				"name": "商品12",
				"count": 1
			}]
		}
		"""
	Then bill4在jobs的webapp中拥有402会员积分

@mall2 @promotion 
Scenario: 13 不同等级的会员购买原价同时有根据等级设置积分抵扣的商品

	Given bill1关注jobs的公众号
	And bill2关注jobs的公众号
	And bill3关注jobs的公众号
	And bill4关注jobs的公众号
	And jobs登录系统
	And jobs已添加商品
		"""
		[{
			"name": "商品13",
			"price": 100.00,
			"is_member_product": "no"
		}]
		"""
	When jobs添加会员等级
		"""
		[{
			"name": "铜牌会员",
			"discount": "9.8"
		}, {
			"name": "银牌会员",
			"discount": "8"
		}, {
			"name": "金牌会员",
			"discount": "7"
		}]
		"""
	When jobs更新"bill2"的会员等级
		"""
		{
			"name": "bill2",
			"member_rank": "铜牌会员"
		}
		"""
	When jobs更新"bill3"的会员等级
		"""
		{
			"name": "bill3",
			"member_rank": "银牌会员"
		}
		"""
	When jobs更新"bill4"的会员等级
		"""
		{
			"name": "bill4",
			"member_rank": "金牌会员"
		}
		"""
	Then jobs可以获得会员列表
		"""
		[{
			"name": "bill4",
			"member_rank": "金牌会员"
		}, {
			"name": "bill3",
			"member_rank": "银牌会员"
		}, {
			"name": "bill2",
			"member_rank": "铜牌会员"
		}, {
			"name": "bill1",
			"member_rank": "普通会员"
		}, {
			"name": "bill",
			"member_rank": "普通会员"
		}]
		"""

	When jobs创建积分应用活动
		"""
		[{
			"name": "商品13积分应用",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品13",
			"is_permanant_active": false,
			"rules": 
			[{
				"member_grade": "普通会员",
				"discount": 100,
				"discount_money": 100.0
			},{
				"member_grade": "铜牌会员",
				"discount": 90,
				"discount_money": 90.0
			},{
				"member_grade": "银牌会员",
				"discount": 80,
				"discount_money": 80.0
			},{
				"member_grade": "金牌会员",
				"discount": 70,
				"discount_money": 70.0
			}]
		}]
		"""

	#1301会员bill1购买商品13，使用积分抵扣最高：100元，订单金额：0元
	When bill1访问jobs的webapp
	When bill1获得jobs的200会员积分
	When bill1购买jobs的商品
		"""
		{
			"products": [{
				"integral_money":100.00,
				"integral":200.00,
				"name": "商品13",
				"count": 1
			}]
		}
		"""
	Then bill1成功创建订单
		"""
		{
			"status": "待发货",
			"final_price": 0.00,
			"product_price": 100.00,
			"promotion_saved_money": 0.00,
			"postage": 0.00,
			"integral_money":100.00,
			"integral":200.00,
			"coupon_money":0.00,
			"products": [{
				"price": 100.0,
				"grade_discounted_money": 0.0,
				"name": "商品13",
				"count": 1
			}]
		}
		"""
	Then bill1在jobs的webapp中拥有0会员积分

	#1302会员bill2购买商品13，使用积分抵扣最高：90元，订单金额：10元
	When bill2访问jobs的webapp
	When bill2获得jobs的300会员积分
	When bill2购买jobs的商品
		"""
		{
			"products": [{
				"integral_money":90.00,
				"integral":180.00,
				"name": "商品13",
				"count": 1
			}]
		}
		"""
	Then bill2成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 10.00,
			"product_price": 100.00,
			"promotion_saved_money": 0.00,
			"postage": 0.00,
			"integral_money":90.00,
			"integral":180.00,
			"coupon_money":0.00,
			"products": [{
				"price": 100.0,
				"grade_discounted_money": 0.0,
				"name": "商品13",
				"count": 1
			}]
		}
		"""
	Then bill2在jobs的webapp中拥有120会员积分

	#1303会员bill3购买商品13，使用积分抵扣最高：80元，订单金额：20元
	When bill3访问jobs的webapp
	When bill3获得jobs的400会员积分
	When bill3购买jobs的商品
		"""
		{
			"products": [{
				"integral_money":80.00,
				"integral":160.00,
				"name": "商品13",
				"count": 1
			}]
		}
		"""
	Then bill3成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 20.00,
			"product_price": 100.00,
			"promotion_saved_money": 0.00,
			"postage": 0.00,
			"integral_money":80.00,
			"integral":160.00,
			"coupon_money":0.00,
			"products": [{
				"price": 100.0,
				"grade_discounted_money": 0.0,
				"name": "商品13",
				"count": 1
			}]
		}
		"""
	Then bill3在jobs的webapp中拥有240会员积分

	#1304会员bill4购买商品13，使用积分抵扣最高：70元，订单金额：30元
	When bill4访问jobs的webapp
	When bill4获得jobs的500会员积分
	When bill4购买jobs的商品
		"""
		{
			"products": [{
				"integral_money":70.00,
				"integral":140.00,
				"name": "商品13",
				"count": 1
			}]
		}
		"""
	Then bill4成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 30.00,
			"product_price": 100.00,
			"promotion_saved_money": 0.00,
			"postage": 0.00,
			"integral_money":70.00,
			"integral":140.00,
			"coupon_money":0.00,
			"products": [{
				"price": 100.0,
				"grade_discounted_money": 0.0,
				"name": "商品13",
				"count": 1
			}]
		}
		"""
	Then bill4在jobs的webapp中拥有360会员积分

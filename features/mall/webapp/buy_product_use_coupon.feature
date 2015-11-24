#editor : "benchi"
#editor : "新新"
@func:webapp.modules.mall.views.list_products

Feature: 在webapp中使用优惠券购买商品（使用全局优惠劵）
	"""
		bill能在webapp中使用优惠券购买jobs添加的"商品"

		#editor: 王丽
		1、优惠券活动设置规则
			1）【优惠券名称】：优惠券的名称
			2）【优惠券金额】：单位"元"，单张优惠券的金额
			3）【会员限制】：设置什么等级的会员可以领取此优惠券，下拉选项为：全部会员、会员等级中设置会员等级列表；选择"全部会员"或者单选一级会员
			4）【每人限领】：单位"张",设置每人限制领取的张数，下拉选项：1、3、5、8、不限制，默认值"1"
					这里只限制的单人领取优惠券的张数，不限制使用优惠码方式使用优惠券的数量
			5）【购买金额】：购买多少可以使用优惠券
				满额使用：购买优惠券商品（全店通用优惠券是判断本店商品；单品优惠券是判断本单品）满多少钱之后才能使用，不包含运费和赠品商品
				1）不限制：使用优惠券不对购买商品的金额限制
				2）满（？）元可以使用：设置购买必须满多少元才能使用优惠券
					全店通用优惠券：只要整个订单满足满额使用的金额，就可以使用全店通用优惠券，多规格商品不区分规格计算
					单品优惠券：只有订单的购买此单品的金额满足满额使用的金额。才能使用单品优惠券，多规格商品不区分规格计算
			6）【发放总量】：单位"张"，此次优惠券发放的总量
			7）【使用说明】：此优惠券的使用说明描述
			8）【优惠券类型】：
				1）全店通用：购买全店的商品都可以使用
				2）部分商品：只能制定一个单品，购买此单品才能使用此优惠券，多规格商品不区分规格计算
			9）进行中的优惠券活动可以增加【追加数量】，即增加码库的数量

		2、优惠券使用规则
			1）领取的优惠券在使用期限内按照优惠券的规则，满足规则可以使用，直接抵扣现金，不能抵扣运费
			2）优惠券活动在设置的活动期间内手动结束活动之后，已经领用的优惠券仍然可以使用，未领用的优惠券不能再领用，优惠码不能再使用
			3）订单提交了，订单中使用的优惠券就处于"已使用状态"
			4）订单经过处理处于"已取消"、"退款完成"状态后，订单中的优惠券回复到"未使用"状态
			5）不同等级的会员购买有会员价同时使用全体券的商品（全体券和会员价可以同时使用，但是满多少钱可以使用计算的是会员价）
			6）不同等级的会员购买有会员价同时有单品券的商品（单品券和会员价不能同时使用）交互：选择单品券，商品价格变回原价，取消使用单品券，价格变回会员价，和有会员价的商品同时购买，不影响其他会员价的商品

		3、发放优惠券
			1）可以正对会员发放优惠券活动的优惠券，设置每人发放的数量和制定发放的人，批量发放优惠券
			2）优惠券发放完成后，此优惠券就就会自动进入被发放会员的个人中的优惠券中，会员购买商品的时候就可以使用

		4、设置了“限时抢购”的商品，不能再设置“买赠”“优惠券活动”，三个活动是互斥的，只要设置了其中的一个活动，就不能再设置其他两个活动
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
	#商品6是新加的
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
		}, {
			"name": "商品6",
			"price": 20.00,
			"weight": 1,
			"postage": 10.00
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
	Given jobs已添加了优惠券规则
		"""
		[{
			"name": "优惠券1",
			"money": 1,
			"start_date": "今天",
			"end_date": "1天后",
			"coupon_id_prefix": "coupon1_id_"
		}, {
			"name": "优惠券2",
			"money": 100,
			"start_date": "今天",
			"end_date": "1天后",
			"coupon_id_prefix": "coupon2_id_"
		}, {
			"name": "优惠券3",
			"money": 1,
			"start_date": "今天",
			"end_date": "2天后",
			"using_limit": "满50元可以使用",
			"coupon_id_prefix": "coupon3_id_"
		}, {
			"name": "优惠券4",
			"money": 10,
			"start_date": "前天",
			"end_date": "昨天",
			"coupon_id_prefix": "coupon4_id_"
		}, {
			"name": "优惠券5",
			"money": 10,
			"start_date": "今天",
			"end_date": "2天后",
			"using_limit": "满50元可以使用",
			"coupon_id_prefix": "coupon5_id_"
		}]
		"""
	When bill关注jobs的公众号
	When bill访问jobs的webapp
	When bill领取jobs的优惠券
		"""
		[{
			"name": "优惠券1",
			"coupon_ids": ["coupon1_id_2", "coupon1_id_1"]
		}, {
			"name": "优惠券2",
			"coupon_ids": ["coupon2_id_2", "coupon2_id_1"]
		}, {
			"name": "优惠券3",
			"coupon_ids": ["coupon3_id_2", "coupon3_id_1"]
		}, {
			"name": "优惠券4",
			"coupon_ids": ["coupon4_id_2", "coupon4_id_1"]
		}, {
			"name": "优惠券5",
			"coupon_ids": ["coupon5_id_2", "coupon5_id_1"]
		}]
		"""
	When tom关注jobs的公众号
	When tom访问jobs的webapp
	When tom领取jobs的优惠券
		"""
		[{
			"name": "优惠券1",
			"coupon_ids": ["coupon1_id_3", "coupon1_id_4"]
		}]
		"""

@mall2 @mall.webapp @mall.coupon @bc1
Scenario:1 使用少于商品价格的优惠券金额进行购买
	bill购买jobs的商品时，能使用少于商品价格的优惠券
	1. 创建订单成功，订单状态为“等待支付”
	2. 优惠券状态变为“被bill使用”
	3. 再次使用优惠券码，购物失败

	Given jobs登录系统
	Then jobs能获得优惠券'优惠券1'的码库
		"""
		{
			"coupon1_id_1": {
				"money": 1.0,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			},
			"coupon1_id_2": {
				"money": 1.0,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			},
			"coupon1_id_3": {
				"money": 1.0,
				"status": "未使用",
				"consumer": "",
				"target": "tom"
			},
			"coupon1_id_4": {
				"money": 1.0,
				"status": "未使用",
				"consumer": "",
				"target": "tom"
			}
		}
		"""
	When bill访问jobs的webapp
	#第一次使用
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 2
			}],
			"coupon": "coupon1_id_1"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 199.0,
			"product_price": 200.0,
			"coupon_money": 1.0,
			"promotion_saved_money": 0.0,
			"postage": 0.00,
			"integral_money":0.00
		}
		"""
	#第二次使用
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品3",
				"count": 1
			}],
			"coupon": "coupon1_id_1"
		}
		"""
	Then bill获得创建订单失败的信息'该优惠券已使用'
	Given jobs登录系统
	Then jobs能获得优惠券'优惠券1'的码库
		"""
		{
			"coupon1_id_1": {
				"money": 1.0,
				"status": "已使用",
				"consumer": "bill",
				"target": "bill"
			},
			"coupon1_id_2": {
				"money": 1.0,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""

@mall2 @mall.webapp @mall.coupon
Scenario:2 使用多于商品价格的优惠券金额进行购买
	bill购买jobs的商品时，能使用多于商品价格的优惠券
	1. 订单状态直接变为'等待发货'
	2. 优惠券状态变为“被bill使用”
	
	Given jobs登录系统
	Then jobs能获得优惠券'优惠券2'的码库
		"""
		{
			"coupon2_id_1": {
				"money": 100.0,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			},
			"coupon2_id_2": {
				"money": 100.0,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品3",
				"count": 1
			}],
			"coupon": "coupon2_id_1"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待发货",
			"final_price": 0.0,
			"product_price": 50.0,
			"coupon_money": 50.0
		}
		"""
	Given jobs登录系统
	Then jobs能获得优惠券'优惠券2'的码库
		"""
		{
			"coupon2_id_1": {
				"money": 100.0,
				"status": "已使用",
				"consumer": "bill",
				"target": "bill"
			},
			"coupon2_id_2": {
				"money": 100.0,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""

@mall2 @mall.webapp @mall.coupon
Scenario:3 使用等于商品价格的优惠券金额进行购买
	bill购买jobs的商品时，能使用等于商品价格的优惠券
	1. 订单状态直接变为'等待发货'
	2. 优惠券状态变为“被bill使用”
	
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1
			}],
			"coupon": "coupon2_id_1"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待发货",
			"final_price": 0.0,
			"product_price": 100.0,
			"coupon_money": 100.0
		}
		"""
	Given jobs登录系统
	Then jobs能获得优惠券'优惠券2'的码库
		"""
		{
			"coupon2_id_1": {
				"money": 100.0,
				"status": "已使用",
				"consumer": "bill",
				"target": "bill"
			},
			"coupon2_id_2": {
				"money": 100.0,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""

@mall2 @mall.webapp @mall.coupon
Scenario:4 输入错误的优惠券码进行购买
	bill购买jobs的商品时，输入错误的优惠券码
	1. 创建订单失败
	2. 优惠券状态不变
	
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1
			}],
			"coupon": "coupon_23"
		}
		"""
	Then bill获得创建订单失败的信息'请输入正确的优惠券号'
	Given jobs登录系统
	Then jobs能获得优惠券'优惠券1'的码库
		"""
		{
			"coupon1_id_1": {
				"status": "未使用"
			},
			"coupon1_id_2": {
				"status": "未使用"
			}
		}
		"""
	Then jobs能获得优惠券'优惠券2'的码库
		"""
		{
			"coupon2_id_1": {
				"status": "未使用"
			},
			"coupon2_id_2": {
				"status": "未使用"
			}
		}
		"""
	Then jobs能获得优惠券'优惠券3'的码库
		"""
		{
			"coupon3_id_1": {
				"status": "未使用"
			},
			"coupon3_id_2": {
				"status": "未使用"
			}
		}
		"""

@mall2 @mall.webapp @mall.coupon
Scenario:5 输入未领取的可用优惠券码进行购买，bill创建订单成功，优惠券状态变为已使用
	
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1
			}],
			"coupon": "coupon3_id_4"
		}
		"""
	# Then bill获得创建订单失败的信息'请输入正确的优惠券号'

	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 99.0,
			"product_price": 100.0,
			"coupon_money": 1.0,
			"promotion_saved_money": 0.0,
			"postage": 0.00,
			"integral_money":0.00
		}
		"""

	Given jobs登录系统
	Then jobs能获得优惠券'优惠券1'的码库
		"""
		{
			"coupon1_id_1": {
				"status": "未使用"
			},
			"coupon1_id_2": {
				"status": "未使用"
			}
		}
		"""
	Then jobs能获得优惠券'优惠券2'的码库
		"""
		{
			"coupon2_id_1": {
				"status": "未使用"
			},
			"coupon2_id_2": {
				"status": "未使用"
			}
		}
		"""
	Then jobs能获得优惠券'优惠券3'的码库
		"""
		{
			"coupon3_id_1": {
				"status": "未使用"
			},
			"coupon3_id_2": {
				"status": "未使用"
			},
			"coupon3_id_4": {
				"money": 1.0,
				"status": "已使用",
				"consumer": "bill",
				"target": ""
			}
		}
		"""

@mall2 @mall.webapp @mall.coupon
Scenario:6 输入已过期的优惠券码进行购买
	bill购买jobs的商品时，使用已过期的优惠券进行购买
	1. 购物失败
	
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1
			}],
			"coupon": "coupon4_id_1"
		}
		"""
	Then bill获得创建订单失败的信息'该优惠券已过期'
	Given jobs登录系统
	Then jobs能获得优惠券'优惠券4'的码库
		"""
		{
			"coupon4_id_1": {
				"money": 10.0,
				"status": "已过期",
				"consumer": "",
				"target": "bill"
			},
			"coupon4_id_2": {
				"money": 10.0,
				"status": "已过期",
				"consumer": "",
				"target": "bill"
			}
		}
		"""

@mall2 @mall.webapp @mall.coupon
Scenario:7 输入别人的优惠券码进行购买
	bill购买jobs的商品时，能使用tom的优惠券进行购买
	1. 购物失败
	
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1
			}],
			"coupon": "coupon1_id_3"
		}
		"""
	Then bill获得创建订单失败的信息'该优惠券已被他人领取不能使用'
	Given jobs登录系统
	Then jobs能获得优惠券'优惠券1'的码库
		"""
		{
			"coupon1_id_3": {
				"status": "未使用",
				"consumer": "",
				"target": "tom"
			},
			"coupon1_id_4": {
				"status": "未使用",
				"consumer": "",
				"target": "tom"
			}
		}
		"""

@mall2 @mall.webapp @mall.coupon
Scenario:8 使用满金额条件的优惠券，购买小于金额条件的商品
	bill购买jobs的商品时，商品金额小于优惠券使用金额
	1.购物失败

	Given jobs登录系统
	Then jobs能获得优惠券'优惠券3'的码库
		"""
		{
			"coupon3_id_1": {
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品4",
				"count": 1
			}],
			"coupon": "coupon3_id_1"
		}
		"""
	Then bill获得创建订单失败的信息'该优惠券不满足使用金额限制'
	Given jobs登录系统
	Then jobs能获得优惠券'优惠券3'的码库
		"""
		{
			"coupon3_id_1": {
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""

@mall2 @mall.webapp @mall.coupon
Scenario:9 使用满金额条件的优惠券，购买等于金额条件的商品
	bill购买jobs的商品时，商品金额等于优惠券使用金额
	1. 购物成功

	Given jobs登录系统
	Then jobs能获得优惠券'优惠券3'的码库
		"""
		{
			"coupon3_id_1": {
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品3",
				"count": 1
			}],
			"coupon": "coupon3_id_1"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 49.0,
			"product_price": 50.0,
			"coupon_money": 1.0
		}
		"""
	Given jobs登录系统
	Then jobs能获得优惠券'优惠券3'的码库
		"""
		{
			"coupon3_id_1": {
				"status": "已使用",
				"consumer": "bill",
				"target": "bill"
			}
		}
		"""

@mall2 @mall.webapp @mall.coupon
Scenario:10 使用满金额条件的优惠券，购买大于金额条件的商品
	bill购买jobs的商品时，商品金额大于优惠券使用金额

	Given jobs登录系统
	Then jobs能获得优惠券'优惠券3'的码库
		"""
		{
			"coupon3_id_1": {
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品4",
				"count": 2
			}],
			"coupon": "coupon3_id_1"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 79.0,
			"product_price": 80.0,
			"coupon_money": 1.0
		}
		"""
	Given jobs登录系统
	Then jobs能获得优惠券'优惠券3'的码库
		"""
		{
			"coupon3_id_1": {
				"status": "已使用",
				"consumer": "bill",
				"target": "bill"
			}
		}
		"""

@mall2 @mall.webapp @mall.coupon
Scenario:11 购买多规格商品，买1个商品的两个规格，总价格满足优惠劵使用条件

	Given jobs登录系统
	Then jobs能获得优惠券'优惠券5'的码库
		"""
		{
			"coupon5_id_1": {
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品5",
				"count": 1,
				"model": "M"
			},{
				"name": "商品5",
				"count": 1,
				"model": "S"
			}],
			"coupon": "coupon5_id_1"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 70.0,
			"product_price": 80.0,
			"coupon_money": 10.0
		}
		"""
	Given jobs登录系统
	Then jobs能获得优惠券'优惠券5'的码库
		"""
		{
			"coupon5_id_1": {
				"status": "已使用",
				"consumer": "bill",
				"target": "bill"
			}
		}
		"""

@mall2 @mall.webapp @mall.coupon
Scenario:12 使用多于商品价格的优惠券进行购买，且不能抵扣运费
	bill购买jobs的商品时，优惠券金额大于商品金额时
	1.只抵扣商品金额，不能抵扣运费

	Given jobs登录系统
	Then jobs能获得优惠券'优惠券2'的码库
		"""
		{
			"coupon2_id_1": {
				"money": 100.0,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			},
			"coupon2_id_2": {
				"money": 100.0,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品6",
				"count": 1
			}],
			"coupon": "coupon2_id_1"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 10.00,
			"product_price": 20.00,
			"postage": 10.00,
			"coupon_money": 20.00
		}
		"""
	Given jobs登录系统
	Then jobs能获得优惠券'优惠券2'的码库
		"""
		{
			"coupon2_id_1": {
				"status": "已使用",
				"consumer": "bill",
				"target": "bill"
			}
		}
		"""

#editor: "新新" "雪静"
@mall2 @meberGrade @coupon
Scenario:13 不同等级的会员购买有会员价同时使用全体券的商品
	#（全体券和会员价可以同时使用，但是满多少钱可以使用计算的是会员价）
	Given jobs登录系统
	And jobs已添加商品
		"""
		[{
			"name": "商品9",
			"price": 100.00,
			"is_member_product": "on",
			"weight": 1,
			"postage": "系统"
		},{
			"name": "商品10",
			"price": 100.00,
			"is_member_product": "on",
			"weight": 1,
			"postage": "系统"
		}]
		"""
	When jobs添加会员等级
		"""
		[{
			"name": "铜牌会员",
			"upgrade": "手动升级",
			"discount": "9"
		}, {
			"name": "金牌会员",
			"upgrade": "手动升级",
			"discount": "7"
		}]
		"""
	Then jobs能获取会员等级列表
		"""
		[{
			"name": "普通会员",
			"upgrade": "自动升级",
			"discount": "10"
		}, {
			"name": "铜牌会员",
			"upgrade": "手动升级",
			"discount": "9"
		}, {
			"name": "金牌会员",
			"upgrade": "手动升级",
			"discount": "7"
		}]
		"""
	When nokia关注jobs的公众号
	Given jobs登录系统
	When jobs更新"nokia"的会员等级
		"""
		{
			"name": "nokia",
			"member_rank": "金牌会员"
		}
		"""
	When jobs更新"bill"的会员等级
		"""
		{
			"name": "bill",
			"member_rank": "铜牌会员"
		}
		"""
	Then jobs可以获得会员列表
		"""
		[{
			"name": "nokia",
			"member_rank": "金牌会员"
		}, {
			"name": "tom",
			"member_rank": "普通会员"
		}, {
			"name": "bill",
			"member_rank": "铜牌会员"
		}]
		"""
	Given jobs已添加了优惠券规则
		"""
		[{
			"name": "全体券1",
			"money": 20,
			"limit_counts": 10,
			"start_date": "2天前",
			"end_date": "2天后",
			"using_limit": "满100元可以使用",
			"coupon_id_prefix": "coupon9_id_"
		}]
		"""
	When tom访问jobs的webapp
	When tom领取jobs的优惠券
		"""
		[{
			"name": "全体券1",
			"coupon_ids": ["coupon9_id_1"]
		}]
		"""
	When bill访问jobs的webapp
	When bill领取jobs的优惠券
		"""
		[{
			"name": "全体券1",
			"coupon_ids": ["coupon9_id_2"]
		}]
		"""	
	When nokia访问jobs的webapp
	When nokia领取jobs的优惠券
		"""
		[{
			"name": "全体券1",
			"coupon_ids": ["coupon9_id_3"]
		}]
		"""
	Given jobs登录系统
	Then jobs能获得优惠券'全体券1'的码库
		"""
		{
			"coupon9_id_1": {
				"money": 20.0,
				"status": "未使用",
				"consumer": "",
				"target": "tom"
			},
			"coupon9_id_2": {
				"money": 20.0,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			},
			"coupon9_id_3": {
				"money": 20.0,
				"status": "未使用",
				"consumer": "",
				"target": "nokia"
			},
			"coupon9_id_4": {
				"money": 20.0,
				"status": "未领取",
				"consumer": "",
				"target": ""
			}
		}
		"""
		#可以使用全体券(满100元,会员价后也是100)
	When tom访问jobs的webapp
	When tom购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品9",
				"count": 1
			}],
			"coupon": "coupon9_id_1"
		}
		"""
	Then tom成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 80.00,
			"product_price": 100.0,
			"postage": 0.00,
			"integral_money":0.00,
			"coupon_money":20.00,
			"products": [{
				"name": "商品9",
				"count": 1
			}]
		}
		"""
	#不可以使用全体券(会员价后也是90,没有满足100元可使用条件)
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品9",
				"count": 1
			}],
			"coupon": "coupon9_id_2"
		}
		"""
	Then bill获得错误提示'该优惠券不满足使用金额限制'
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
			"final_price": 90.00,
			"product_price": 90.00,
			"postage": 0.00,
			"integral_money":0.00,
			"coupon_money":0.00,
			"products": [{
				"name": "商品9",
				"count": 1
			}]
		}
		"""
		#购买多种会员价使用全体券
	When nokia访问jobs的webapp
	And nokia设置jobs的webapp的收货地址
		"""
		{
			"ship_name": "nokia",
			"ship_tel": "13811223344",
			"area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦"
		}
		"""
	When nokia加入jobs的商品到购物车
		"""
		[{
			"name": "商品9",
			"count": 1
		}, {
			"name": "商品10",
			"count": 1
		}]
		"""
	Then nokia能获得购物车
		"""
		{
			"product_groups": [{
				"products": [{
					"name": "商品9",
					"price": 70.00,
					"count": 1
				}, {
					"name": "商品10",
					"price": 70.00,
					"count": 1
				}]
			}],
			"invalid_products": []
		}
		"""
	When nokia从购物车发起购买操作
		"""
		{
			"action": "pay",
			"context": [{
				"name": "商品9"
			}, {
				"name": "商品10"
			}],
			"coupon": "coupon9_id_3"
		}
		"""
	And nokia在购物车订单编辑中点击提交订单
		"""
		{
			"pay_type": "微信付款"
		}
		"""
	Then nokia成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 120.00,
			"product_price": 140.0,
			"coupon_money": 20.0,
			"postage": 0.00,
			"integral_money":0.00,
			"products": [{
				"name": "商品9",
				"price": 70.00,
				"count": 1
			}, {
				"name": "商品10",
				"price": 70.00,
				"count": 1
			}]
		}
		"""
	Given jobs登录系统
	Then jobs能获得优惠券'全体券1'的码库
		"""
		{
			"coupon9_id_1": {
				"money": 20.0,
				"status": "已使用",
				"consumer": "tom",
				"target": "tom"
			},
			"coupon9_id_2": {
				"money": 20.0,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			},
			"coupon9_id_3": {
				"money": 20.0,
				"status": "已使用",
				"consumer": "nokia",
				"target": "nokia"
			},
			"coupon9_id_4": {
				"money": 20.0,
				"status": "未领取",
				"consumer": "",
				"target": ""
			}
		}
		"""

#editor: "王丽"
@meberGrade @coupon @mall2
Scenario:14 【优惠券】-未到使用日期，不能使用
	Given jobs登录系统
	And jobs已添加了优惠券规则
		"""
		[{
			"name": "优惠券-未开始",
			"money": 1.0,
			"start_date": "1天后",
			"end_date": "2天后",
			"coupon_id_prefix": "coupon6_id_"
		}]
		"""
	When bill关注jobs的公众号
	When bill访问jobs的webapp
	When bill领取jobs的优惠券
		"""
		[{
			"name": "优惠券-未开始",
			"coupon_ids": ["coupon6_id_1"]
		}]
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1
			}],
			"coupon": "coupon6_id_1"
		}
		"""
	Then bill获得创建订单失败的信息'该优惠券活动尚未开始'

	Given jobs登录系统
	Then jobs能获得优惠券'优惠券-未开始'的码库
		"""
		{
			"coupon6_id_1": {
				"money": 1.0,
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			},
			"coupon6_id_2": {
				"money": 1.0,
				"status": "未领取",
				"consumer": "",
				"target": ""
			},
			"coupon6_id_3": {
				"money": 1.0,
				"status": "未领取",
				"consumer": "",
				"target": ""
			},
			"coupon6_id_4": {
				"money": 1.0,
				"status": "未领取",
				"consumer": "",
				"target": ""
			}
		}
		"""

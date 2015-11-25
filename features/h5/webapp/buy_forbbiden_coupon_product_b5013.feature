#author: 张三香
#editor: 师帅 2015.10.19

Feature:在webapp中购买禁用优惠券商品
	"""
		说明：
		1、针对线上bug5013(微商城项目编号bug5014)补充feature
		2、bug出现场景描述：
			1、数据情况：
				商品1，价格7.8 参与限时抢购(限时抢购价1.5 限购数量20 )，参与禁用优惠券商品
				商品2，价格49
				商品3，价格78
				优惠券：全店通用券，满100元可以使用，金额50元
			2、手机端购买（商品1x20+商品2x1+商品3x1）时，优惠券金额抵扣错误（只抵扣了1元）
		3、bug出现原因：
			优惠券抵扣金额=商品2+商品3-商品1限时抢购带来的总优惠金额
			优惠券抵扣金额=商品2+商品3-商品1会员折扣带来的总优惠金额

	"""

Background:
	Given jobs登录系统
	When jobs添加会员等级
		"""
		[{
			"name": "铜牌会员",
			"upgrade": "手动升级",
			"discount": "7"
		}, {
			"name": "银牌会员",
			"upgrade": "自动升级",
			"discount": "6"
		}, {
			"name": "金牌会员",
			"upgrade": "自动升级",
			"discount": "5"
		}]
		"""
	Given bill关注jobs的公众号
	And jobs登录系统
	And jobs已添加商品
		"""
			[{
				"name": "商品1",
				"price": 100.00,
				"status":"在售"
			},{
				"name": "商品2",
				"price": 50.00,
				"status":"在售"
			},{
				"name": "商品3",
				"price": 60.00,
				"status":"在售"
			}]
		"""
	And jobs已添加了优惠券规则
		"""
		[{
			"name": "全体券1",
			"money": 50.00,
			"count":10,
			"limit_counts":10,
			"start_date": "今天",
			"end_date": "10天后",
			"using_limit": "满100元可以使用",
			"coupon_id_prefix": "coupon1_id_"
		}]
		"""
	When jobs为会员发放优惠券
		"""
		{
			"name": "全体券1",
			"count": 5,
			"members": ["bill"]
		}
		"""
	When jobs添加禁用优惠券商品
		"""
		[{
			"products":[{
				"name":"商品1"
			}],
			"start_date": "今天",
			"end_date": "2天后",
			"is_permanant_active": false
		}]
		"""

@mall2 @promotion @promotionForbiddenCoupon @online_bug
Scenario:1 购买禁用优惠券商品和非禁用优惠券商品,禁用优惠券商品同时参与限时抢购
	#非禁用优惠券商品的价格和-限时抢购带来的总优惠金额<优惠券金额(50+60-70=40)
	Given jobs登录系统
	When jobs创建限时抢购活动
		"""
		[{
			"name": "商品1限时抢购01",
			"promotion_title":"",
			"start_date": "今天",
			"end_date": "2天后",
			"product_name":"商品1",
			"member_grade": "全部会员",
			"count_per_purchase": 2,
			"promotion_price": 30
		}]
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1
			},{
				"name": "商品2",
				"count": 1
			},{
				"name": "商品3",
				"count": 1
			}],
			"coupon": "coupon1_id_1"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 90.0,
			"product_price": 140.0,
			"coupon_money": 50.0,
			"products": [{
				"name": "商品1",
				"count": 1,
				"promotion": {
					"promotioned_product_price": 30,
					"type": "flash_sale"
					}
				},{
					"name": "商品2",
					"price":50.00,
					"count": 1
				},{
					"name": "商品3",
					"price":60.00,
					"count": 1
				}]
		}
		"""

	#非禁用优惠券商品的价格和-限时抢购带来的总优惠金额=优惠券金额(50+60-60=50)
	Given jobs登录系统
	When jobs"结束"促销活动"商品1限时抢购01"
	When jobs创建限时抢购活动
		"""
		[{
			"name": "商品1限时抢购02",
			"promotion_title":"",
			"start_date": "今天",
			"end_date": "2天后",
			"product_name":"商品1",
			"member_grade": "全部会员",
			"count_per_purchase": 2,
			"promotion_price": 70
		}]
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 2
			},{
				"name": "商品2",
				"count": 1
			},{
				"name": "商品3",
				"count": 1
			}],
			"coupon": "coupon1_id_2"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 200.0,
			"product_price": 250.0,
			"coupon_money": 50.0,
			"products": [{
				"name": "商品1",
				"count": 2,
				"promotion": {
					"promotioned_product_price": 70,
					"type": "flash_sale"
					}
				},{
					"name": "商品2",
					"price":50.00,
					"count": 1
				},{
					"name": "商品3",
					"price":60.00,
					"count": 1
				}]
		}
		"""

	#非禁用优惠券商品的价格和-限时抢购带来的总优惠金额>优惠券金额(50+60-40=70)
	Given jobs登录系统
	When jobs"结束"促销活动"商品1限时抢购02"
	When jobs创建限时抢购活动
		"""
		[{
			"name": "商品1限时抢购03",
			"promotion_title":"",
			"start_date": "今天",
			"end_date": "2天后",
			"product_name":"商品1",
			"member_grade": "全部会员",
			"count_per_purchase": 2,
			"promotion_price": 60
		}]
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1
			},{
				"name": "商品2",
				"count": 1
			},{
				"name": "商品3",
				"count": 1
			}],
			"coupon": "coupon1_id_3"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 120.0,
			"product_price": 170.0,
			"coupon_money": 50.0,
			"products": [{
				"name": "商品1",
				"count": 1,
				"promotion": {
					"promotioned_product_price": 60,
					"type": "flash_sale"
					}
				},{
					"name": "商品2",
					"price":50.00,
					"count": 1
				},{
					"name": "商品3",
					"price":60.00,
					"count": 1
				}]
		}
		"""

	#非禁用优惠券商品的价格和-限时抢购带来的总优惠金额<优惠券金额(50+60-120=-10)
	Given jobs登录系统
	When jobs"结束"促销活动"商品1限时抢购03"
	When jobs更新商品'商品1'
		"""
		{
			"price":200.00
		}
		"""
	When jobs创建限时抢购活动
		"""
		[{
			"name": "商品1限时抢购04",
			"promotion_title":"",
			"start_date": "今天",
			"end_date": "2天后",
			"product_name":"商品1",
			"member_grade": "全部会员",
			"count_per_purchase": 2,
			"promotion_price": 80
		}]
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1
			},{
				"name": "商品2",
				"count": 1
			},{
				"name": "商品3",
				"count": 1
			}],
			"coupon": "coupon1_id_4"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 140.0,
			"product_price": 190.0,
			"coupon_money": 50.0,
			"products": [{
				"name": "商品1",
				"count": 1,
				"promotion": {
					"promotioned_product_price": 80,
					"type": "flash_sale"
					}
				},{
					"name": "商品2",
					"price":50.00,
					"count": 1
				},{
					"name": "商品3",
					"price":60.00,
					"count": 1
				}]
		}
		"""

@mall2 @promotion @promotionForbiddenCoupon @online_bug
Scenario:2 购买禁用优惠券商品和非禁用优惠券商品,禁用优惠券商品同时参与会员折扣
	#非禁用优惠券商品的价格和-会员折扣带来的总优惠金额<优惠券金额(50+60-70=40)
	Given jobs登录系统
	When jobs更新商品'商品1'
		"""
		{
			"name":"商品1",
			"price":100.00,
			"is_member_product": "on"
		}
		"""
	When jobs更新"bill"的会员等级
		"""
		{
			"name": "bill",
			"member_rank": "金牌会员"
		}
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1
			},{
				"name": "商品2",
				"count": 1
			},{
				"name": "商品3",
				"count": 1
			}],
			"coupon": "coupon1_id_1"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 110.0,
			"product_price": 160.0,
			"coupon_money": 50.0,
			"products": [{
				"name": "商品1",
				"count": 1,
				"price": 50.0,
				"grade_discounted_money": 50.0
			},{
				"name": "商品2",
				"price":50.00,
				"count": 1
			},{
				"name": "商品3",
				"price":60.00,
				"count": 1
			}]
		}
		"""

	#非禁用优惠券商品的价格和-会员折扣带来的总优惠金额=优惠券金额(50+60-60=50)
	Given jobs登录系统
	When jobs更新"bill"的会员等级
		"""
		{
			"name": "bill",
			"member_rank": "铜牌会员"
		}
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 2
			},{
				"name": "商品2",
				"count": 1
			},{
				"name": "商品3",
				"count": 1
			}],
			"coupon": "coupon1_id_2"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 200.0,
			"product_price": 250.0,
			"coupon_money": 50.0,
			"products": [{
				"name": "商品1",
				"count": 2,
				"price": 70.0,
				"grade_discounted_money": 60.0
			},{
				"name": "商品2",
				"price":50.00,
				"count": 1
			},{
				"name": "商品3",
				"price":60.00,
				"count": 1
			}]
		}
		"""

	#非禁用优惠券商品的价格和-会员折扣带来的总优惠金额>优惠券金额(50+60-40=70)
	Given jobs登录系统
	When jobs更新"bill"的会员等级
		"""
		{
			"name": "bill",
			"member_rank": "银牌会员"
		}
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1
			},{
				"name": "商品2",
				"count": 1
			},{
				"name": "商品3",
				"count": 1
			}],
			"coupon": "coupon1_id_3"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 120.0,
			"product_price": 170.0,
			"coupon_money": 50.0,
			"products": [{
				"name": "商品1",
				"count": 1,
				"price": 60.0,
				"grade_discounted_money": 40.0
			},{
				"name": "商品2",
				"price":50.00,
				"count": 1
			},{
				"name": "商品3",
				"price":60.00,
				"count": 1
			}]
		}
		"""

	#非禁用优惠券商品的价格和-会员折扣带来的总优惠金额<优惠券金额(50+60-120=-10)
	Given jobs登录系统
	When jobs更新商品'商品1'
		"""
		{
			"name":"商品1",
			"price":200.00,
			"is_member_product": "on"
		}
		"""
	When jobs更新"bill"的会员等级
		"""
		{
			"name": "bill",
			"member_rank": "铜牌会员"
		}
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 2
			},{
				"name": "商品2",
				"count": 1
			},{
				"name": "商品3",
				"count": 1
			}],
			"coupon": "coupon1_id_4"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 340.0,
			"product_price": 390.0,
			"coupon_money": 50.0,
			"products": [{
				"name": "商品1",
				"count": 2,
				"price": 140.0,
				"grade_discounted_money": 120.0
			},{
				"name": "商品2",
				"price":50.00,
				"count": 1
			},{
				"name": "商品3",
				"price":60.00,
				"count": 1
			}]
		}
		"""
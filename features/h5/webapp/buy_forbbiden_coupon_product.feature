#_author_:张三香

Feature:在webapp中购买禁用优惠券商品
	"""
		1、禁用优惠券商品只禁用全店通用券,不禁用单品券
		2、购买包含禁用优惠券商品在内的多个商品时,其余商品仍可使用全店通用券，禁用优惠券商品不参与通用券使用条件的计算
			示例数据：
					商品1（100元）-禁用优惠券商品,
					商品2（100元）-禁用优惠券商品+单品券,
					商品3（100元）-不禁用优惠券商品,
					全体券1(300)-满200元可使用,
					单品券2（10）-不限制使用,
					全体券2(200)-不限制使用
					bill:1张全体券1和1张单品券2
					tom:1张全体券2
			bill购买：
				a1.购买"商品1,2" --不能使用'全体券1'
				a2.购买"商品2,2" --不能使用'全体券1',可以使用'单品券2'
				b1.购买"商品3,1+商品2,1" -- 不能使用'全体券1',可以使用'单品券2'
				b2.购买"商品3,1+商品1,1" -- 不能使用'全体券1'
				c.购买"商品1,1+商品2,1+商品3,2" -- 可以使用'全体券1'和'单品券2',但二者不能同时使用
			tom购买：
				d.购买"商品1,1+商品3,1" -- 可以使用'全体券2',只针对商品3可抵扣100元
	"""

Background:
	Given jobs登录系统
	When jobs添加会员等级
		"""
		[{
			"name": "铜牌会员",
			"upgrade": "手动升级",
			"discount": "9"
		}, {
			"name": "银牌会员",
			"upgrade": "自动升级",
			"discount": "8"
		}]
		"""
	Given jobs设定会员积分策略
		"""
		{
			"integral_each_yuan": 2
		}
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
				"price": 100.00,
				"status":"在售"
			},{
				"name": "商品3",
				"price": 100.00,
				"status":"在售"
			}]
		"""
	And jobs已添加了优惠券规则
		"""
		[{
			"name": "全体券1",
			"money": 300.00,
			"counts":5,
			"limit_counts": 1,
			"start_date": "今天",
			"end_date": "2天后",
			"using_limit": "满200元可以使用",
			"coupon_id_prefix": "coupon1_id_"
		}, {
			"name": "单品券2",
			"money": 110.00,
			"counts":5,
			"limit_counts": 1,
			"start_date": "今天",
			"end_date": "1天后",
			"coupon_id_prefix": "coupon2_id_",
			"coupon_product": "商品2"
		}]
		"""
	When jobs为会员发放优惠券
		"""
		{
			"name": "全体券1",
			"count": 1,
			"members": ["bill"]
		}
		"""
	When jobs为会员发放优惠券
		"""
		{
			"name": "单品券2",
			"count": 1,
			"members": ["bill"]
		}
		"""
	When jobs添加禁用优惠券商品
		"""
		[{
			"products":[{
				"name":"商品1"
			},{
				"name":"商品2"
			}],
			"start_date": "今天",
			"end_date": "2天后",
			"is_permanant_active": false
		}]
		"""

@mall2 @promotion @promotionForbiddenCoupon
Scenario:1 购买单个禁用优惠券商品,该商品无单品券
	#购买商品1,数量2,全体券1不可使用
	When bill访问jobs的webapp
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
	Then bill获得创建订单失败的信息'该优惠券不能购买订单中的商品'
	Given jobs登录系统
	Then jobs能获得优惠券'全体券1'的码库
		"""
		{
			"coupon1_id_1": {
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""

@mall2 @promotion @promotionForbiddenCoupon
Scenario:2 购买单个禁用优惠券商品,该商品有单品券
	#购买商品2,数量2,全体券1不可使用,单品券2可以使用
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品2",
				"count": 2
			}],
			"coupon": "coupon2_id_1"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 90.0,
			"product_price": 200.0,
			"coupon_money": 110.0
		}
		"""
	Given jobs登录系统
	Then jobs能获得优惠券'全体券1'的码库
		"""
		{
			"coupon1_id_1": {
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""
	And jobs能获得优惠券'单品券2'的码库
		"""
		{
			"coupon2_id_1": {
				"status": "已使用",
				"consumer": "bill",
				"target": "bill"
			}
		}
		"""

@mall2 @promotion @promotionForbiddenCoupon
Scenario:3 购买多个商品,包含禁用优惠券商品,不满足全体券使用条件
	#购买商品1和商品3,全体券1不可使用
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1
			},{
				"name": "商品3",
				"count": 1
			}],
			"coupon": "coupon1_id_1"
		}
		"""
	Then bill获得创建订单失败的信息'该优惠券不满足使用金额限制'
	Given jobs登录系统
	Then jobs能获得优惠券'全体券1'的码库
		"""
		{
			"coupon1_id_1": {
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""
	#购买商品2和商品3,全体券1不可使用,单品券2可使用
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品2",
				"count": 1
			},{
				"name": "商品3",
				"count": 1
			}],
			"coupon": "coupon2_id_1"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 100.0,
			"product_price": 200.0,
			"coupon_money": 100.0
		}
		"""
	Given jobs登录系统
	Then jobs能获得优惠券'全体券1'的码库
		"""
		{
			"coupon1_id_1": {
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""
	And jobs能获得优惠券'单品券2'的码库
		"""
		{
			"coupon2_id_1": {
				"status": "已使用",
				"consumer": "bill",
				"target": "bill"
			}
		}
		"""

@mall2 @promotion @promotionForbiddenCoupon
Scenario:4 购买多个商品,包含禁用优惠券商品,满足全体券使用条件
	#购买商品1,1+商品2,1+商品3,2(单品券2可以使用,全体券1可使用,但二者只能选择一张使用)
	#选择使用全体券1
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
					"count": 2
				}],
			"coupon": "coupon1_id_1"
			}
			"""
		Then bill成功创建订单
			"""
			{
				"status": "待支付",
				"final_price": 200.0,
				"product_price": 400.0,
				"coupon_money": 200.0
			}
			"""
		Given jobs登录系统
		Then jobs能获得优惠券'全体券1'的码库
			"""
			{
				"coupon1_id_1": {
					"status": "已使用",
					"consumer": "bill",
					"target": "bill"
				}
			}
			"""
		And jobs能获得优惠券'单品券2'的码库
			"""
			{
				"coupon2_id_1": {
					"status": "未使用",
					"consumer": "",
					"target": "bill"
				}
			}
			"""

	#选择使用单品券2
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
						"count": 2
					}],
				"coupon": "coupon2_id_1"
				}
			"""
		Then bill成功创建订单
			"""
			{
				"status": "待支付",
				"final_price": 300.0,
				"product_price": 400.0,
				"coupon_money": 100.0
			}
			"""
		Given jobs登录系统
		Then jobs能获得优惠券'全体券1'的码库
			"""
			{
				"coupon1_id_1": {
					"status": "已使用",
					"consumer": "bill",
					"target": "bill"
				}
			}
			"""
		And jobs能获得优惠券'单品券2'的码库
			"""
			{
				"coupon2_id_1": {
					"status": "已使用",
					"consumer": "bill",
					"target": "bill"
				}
			}
			"""

@mall2 @promotion @promotionForbiddenCoupon
Scenario:5 购买多个商品,包含禁用优惠券商品,全体券使用金额无限制
	#购买商品1和商品3,200元通用券只能抵扣商品3的100元
	Given tom关注jobs的公众号
	Given jobs登录系统
	When jobs添加优惠券规则
		"""
		[{
			"name": "全体券2",
			"money": 200.00,
			"counts":5,
			"limit_counts": 1,
			"start_date": "今天",
			"end_date": "2天后",
			"coupon_id_prefix": "coupon3_id_"
		}]
		"""
	When jobs为会员发放优惠券
		"""
		{
			"name": "全体券2",
			"count": 1,
			"members": ["tom"]
		}
		"""
	When tom访问jobs的webapp
	When tom购买jobs的商品
			"""
			{
				"products": [{
					"name": "商品1",
					"count": 1
				},{
					"name": "商品3",
					"count": 1
				}],
			"coupon": "coupon3_id_1"
			}
			"""
	Then tom成功创建订单
		"""
			{
				"status": "待支付",
				"final_price": 100.0,
				"product_price": 200.0,
				"coupon_money": 100.0
			}
		"""
	Given jobs登录系统
	Then jobs能获得优惠券'全体券2'的码库
		"""
		{
			"coupon3_id_1": {
				"status": "已使用",
				"consumer": "tom",
				"target": "tom"
			}
		}
		"""

@mall2 @promotion @promotionForbiddenCoupon
Scenario:6 购买禁用优惠券商品,该商品同时参与会员折扣
	Given jobs登录系统
	When jobs更新商品'商品1'
		"""
		{
			"name": "商品1",
			"price": 100.00,
			"status":"在售",
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
				"count": 3
			}],
			"coupon": "coupon1_id_1"
		}
		"""
	Then bill获得创建订单失败的信息'该优惠券不能购买订单中的商品'
	Given jobs登录系统
	Then jobs能获得优惠券'全体券1'的码库
		"""
		{
			"coupon1_id_1": {
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""

@mall2 @promotion @promotionForbiddenCoupon
Scenario:7 购买禁用优惠券商品,该商品同时参与限时抢购
	Given jobs登录系统
	When jobs创建限时抢购活动
		"""
		[{
			"name": "限时抢购活动",
			"promotion_title":"",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name":"商品1",
			"member_grade": "铜牌会员",
			"count_per_purchase": 2,
			"promotion_price": 99.00
		}]
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
				"count": 3
			}],
			"coupon": "coupon1_id_1"
		}
		"""
	Then bill获得创建订单失败的信息'该优惠券不能购买订单中的商品'
	Given jobs登录系统
	Then jobs能获得优惠券'全体券1'的码库
		"""
		{
			"coupon1_id_1": {
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""

@mall2 @promotion @promotionForbiddenCoupon
Scenario:8 购买禁用优惠券商品,该商品同时参与买赠
	Given jobs登录系统
	When jobs创建买赠活动
		"""
		[{
			"name": "买赠活动",
			"promotion_title":"",
			"start_date": "今天",
			"end_date": "1天后",
			"member_grade": "全部会员",
			"product_name": "商品1",
			"premium_products": 
			[{
				"name": "商品3",
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
				"name": "商品1",
				"count": 2
			}],
			"coupon": "coupon1_id_1"
		}
		"""
	Then bill获得创建订单失败的信息'该优惠券不能购买订单中的商品'
	Given jobs登录系统
	Then jobs能获得优惠券'全体券1'的码库
		"""
		{
			"coupon1_id_1": {
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""

@mall2 @promotion @promotionForbiddenCoupon
Scenario:9 购买禁用优惠券商品,该商品同时参与积分应用
	Given jobs登录系统
	When jobs创建积分应用活动
		"""
		[{
			"name": "积分应用活动",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品1",
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
				}]
		}]
		"""
	When jobs更新"bill"的会员等级
		"""
		{
			"name": "bill",
			"member_rank": "银牌会员"
		}
		"""
	#选择使用积分抵扣,优惠券入口消失,积分和优惠券不能同时使用
	When bill访问jobs的webapp
	When bill获得jobs的400会员积分
	Then bill在jobs的webapp中拥有400会员积分
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 2,
				"integral_money":160.00,
				"integral":320
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 40.0,
			"product_price": 200.0,
			"coupon_money": 0.0,
			"integral_money":160.00,
			"integral":320
		}
		"""
	And bill在jobs的webapp中拥有80会员积分
	#不使用积分抵扣,全体券1不可使用
	When bill访问jobs的webapp
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
	Then bill获得创建订单失败的信息'该优惠券不能购买订单中的商品'
	Given jobs登录系统
	Then jobs能获得优惠券'全体券1'的码库
		"""
		{
			"coupon1_id_1": {
				"status": "未使用",
				"consumer": "",
				"target": "bill"
			}
		}
		"""

@mall2 @promotion @promotionForbiddenCoupon
Scenario:10 购买禁用优惠券多规格商品,一个商品的2个规格,总价格满足单品券使用
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
			"name": "多规格禁用",
			"is_enable_model": "启用规格",
			"model": {
				"models":{
					"M": {
						"price": 50.00,
						"stock_type": "无限"
					},
					"S": {
						"price": 50.00,
						"stock_type": "无限"
					}
				}
			}
		}]
		"""
	And jobs已添加了优惠券规则
		"""
		[{
			"name": "多规格单品券",
			"money": 10.00,
			"counts":5,
			"limit_counts": 1,
			"start_date": "今天",
			"end_date": "1天后",
			"using_limit": "满100元可以使用",
			"coupon_id_prefix": "coupon4_id_",
			"coupon_product": "多规格禁用"
		}]
		"""
	When jobs为会员发放优惠券
		"""
		{
			"name": "多规格单品券",
			"count": 1,
			"members": ["bill"]
		}
		"""
	When jobs添加禁用优惠券商品
		"""
		[{
			"products":[{
				"name":"多规格禁用"
			}],
			"start_date": "今天",
			"end_date": "2天后",
			"is_permanant_active": false
		}]
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "多规格禁用",
				"count": 1,
				"model": "M"
			},{
				"name": "多规格禁用",
				"count": 1,
				"model": "S"
			}],
			"coupon": "coupon4_id_1"
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 90.0,
			"product_price": 100.0,
			"coupon_money": 10.0
		}
		"""
	Given jobs登录系统
	Then jobs能获得优惠券'多规格单品券'的码库
		"""
		{
			"coupon4_id_1": {
				"status": "已使用",
				"consumer": "bill",
				"target": "bill"
			}
		}
		"""

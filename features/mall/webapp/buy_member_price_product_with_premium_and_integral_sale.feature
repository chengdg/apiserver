
#author: 张三香

Feature:手机端购买同时参与会员折扣,买赠和单品积分抵扣活动的商品
	#针对线上bug4305补充feature
	#bug4305-手机端购买参与“会员价+买赠+积分应用”商品时，提交订单不成功（只提示正在提交订单，页面不跳转）

Background:
	Given jobs登录系统
	Given jobs设定会员积分策略
		"""
		{
			"integral_each_yuan": 2
		}
		"""
	
	When jobs添加会员等级
		"""
		[{
			"name": "铜牌会员",
			"upgrade": "手动升级",
			"discount": "9"
		},{
			"name": "银牌会员",
			"upgrade": "手动升级",
			"discount": "8"
		}]
		"""
	When bill关注jobs的公众号
	And bill2关注jobs的公众号
	And bill3关注jobs的公众号

	Given jobs登录系统
	When jobs更新"bill2"的会员等级
		"""
		{
			"name":"bill2",
			"member_rank":"铜牌会员"
		}
		"""
	When jobs更新"bill3"的会员等级
		"""
		{
			"name":"bill3",
			"member_rank":"银牌会员"
		}
		"""
	Then jobs可以获得会员列表
		"""
		[{
			"name":"bill3",
			"member_rank":"银牌会员"
		}, {
			"name":"bill2",
			"member_rank":"铜牌会员"
		}, {
			"name":"bill",
			"member_rank":"普通会员"
		}]
		"""
	When jobs已添加商品
		"""
		[{
			"name": "商品1",
			"is_member_product": "on",
			"price":100.00
		},{
			"name": "赠品",
			"price":100
		}]
		"""

@mall2
Scenario:1 购买会员价，买赠（全部会员）和积分抵扣（分级设置）活动的商品
	Given jobs登录系统
	When jobs创建买赠活动
		"""
		[{
			"name": "商品1买一赠二",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品1",
			"premium_products": [{
				"name": "赠品",
				"count": 2
			}],
			"count": 1,
			"member_grade":"全部",
			"is_enable_cycle_mode": true
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
	When bill访问jobs的webapp
	When bill获得jobs的200会员积分
	Then bill在jobs的webapp中拥有200会员积分
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"integral_money":100.00,
				"integral":200,
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待发货",
			"final_price": 0.00,
			"product_price": 100.00,
			"integral_money":100.00,
			"integral":200,
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"grade_discounted_money": 0.0,
				"count": 1
			},{
				"name": "赠品",
				"price": 0.0,
				"count": 2
			}]
		}
		"""
	Then bill在jobs的webapp中拥有0会员积分

@mall2
Scenario:2 购买会员价，买赠（全部会员）和积分抵扣（统一设置）活动的商品
	Given jobs登录系统
	When jobs创建买赠活动
		"""
		[{
			"name": "商品1买一赠二",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品1",
			"premium_products": [{
				"name": "赠品",
				"count": 2
			}],
			"count": 1,
			"member_grade":"全部",
			"is_enable_cycle_mode": true
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
				"discount": 50,
				"discount_money": 50.0
				}]
		}]
		"""
	When bill2访问jobs的webapp
	When bill2获得jobs的200会员积分
	Then bill2在jobs的webapp中拥有200会员积分
	When bill2购买jobs的商品
		"""
		{
			"products": [{
				"integral_money":50.00,
				"integral":100,
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	Then bill2成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 50.00,
			"product_price": 100.00,
			"integral_money":50.00,
			"integral":100,
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"grade_discounted_money": 0.0,
				"count": 1
			},{
				"name": "赠品",
				"price": 0.0,
				"count": 2
			}]
		}
		"""
	Then bill2在jobs的webapp中拥有100会员积分

@mall2
Scenario:3 购买会员价，买赠（某一等级）和积分抵扣（分级设置）活动的商品
	Given jobs登录系统
	When jobs创建买赠活动
		"""
			[{
				"name": "商品1买一赠一",
				"start_date": "今天",
				"end_date": "1天后",
				"product_name": "商品1",
				"premium_products": [{
					"name": "赠品",
					"count": 1
				}],
				"count": 1,
				"member_grade":"铜牌会员",
				"is_enable_cycle_mode": true
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
	#铜牌会员购买商品（符合买赠,买赠优先,按原价购买,可抵扣90）
		When bill2访问jobs的webapp
		When bill2获得jobs的200会员积分
		Then bill2在jobs的webapp中拥有200会员积分
		When bill2购买jobs的商品
			"""
			{
				"products": [{
					"integral_money":90.00,
					"integral":180,
					"name": "商品1",
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
				"integral_money":90.00,
				"integral":180,
				"products": [{
					"name": "商品1",
					"price": 100.00,
					"grade_discounted_money": 0.0,
					"count": 1
				},{
					"name": "赠品",
					"price": 0.0,
					"count": 1
				}]
			}
			"""
		Then bill2在jobs的webapp中拥有20会员积分
	#银牌会员购买商品（不符合买赠,按会员价80购买,可抵扣64）
		When bill3访问jobs的webapp
		When bill3获得jobs的200会员积分
		Then bill3在jobs的webapp中拥有200会员积分
		When bill3购买jobs的商品
			"""
			{
				"products": [{
					"integral_money":64.00,
					"integral":128,
					"name": "商品1",
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
				"integral_money":64.00,
				"integral":128,
				"products": [{
					"name": "商品1",
					"price": 80.00,
					"grade_discounted_money": 20.0,
					"count": 1
				}]
			}
			"""
		Then bill3在jobs的webapp中拥有72会员积分

@mall2
Scenario:4 购买会员价，买赠（某一等级）和积分抵扣（统一设置）活动的商品
	Given jobs登录系统
	When jobs创建买赠活动
		"""
			[{
				"name": "商品1买一赠一",
				"start_date": "今天",
				"end_date": "1天后",
				"product_name": "商品1",
				"premium_products": [{
					"name": "赠品",
					"count": 1
				}],
				"count": 1,
				"member_grade":"铜牌会员",
				"is_enable_cycle_mode": true
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
				"discount": 50,
				"discount_money": 50.0
				}]
		}]
		"""

	#铜牌会员购买商品（符合买赠,买赠优先,按原价购买,可抵扣50元）
		When bill2访问jobs的webapp
		When bill2获得jobs的200会员积分
		Then bill2在jobs的webapp中拥有200会员积分
		When bill2购买jobs的商品
			"""
			{
				"products": [{
					"integral_money":50.00,
					"integral":100,
					"name": "商品1",
					"count": 1
				}]
			}
			"""
		Then bill2成功创建订单
			"""
			{
				"status": "待支付",
				"final_price": 50.00,
				"product_price": 100.00,
				"integral_money":50.00,
				"integral":100,
				"products": [{
					"name": "商品1",
					"price": 100.00,
					"grade_discounted_money": 0.0,
					"count": 1
				},{
					"name": "赠品",
					"price": 0.0,
					"count": 1
				}]
			}
			"""
		Then bill2在jobs的webapp中拥有100会员积分
	#银牌会员购买商品（不符合买赠,按会员价80购买,可抵扣40元）
		When bill3访问jobs的webapp
		When bill3获得jobs的200会员积分
		Then bill3在jobs的webapp中拥有200会员积分
		When bill3购买jobs的商品
			"""
			{
				"products": [{
					"integral_money":40.00,
					"integral":80,
					"name": "商品1",
					"count": 1
				}]
			}
			"""
		Then bill3成功创建订单
			"""
			{
				"status": "待支付",
				"final_price": 40.00,
				"product_price": 80.00,
				"integral_money":40.00,
				"integral":80,
				"products": [{
					"name": "商品1",
					"price": 80.00,
					"grade_discounted_money": 20.0,
					"count": 1
				}]
			}
			"""
		Then bill3在jobs的webapp中拥有120会员积分

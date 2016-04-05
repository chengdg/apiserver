# watcher: zhangsanxiang@weizoom.com,benchi@weizoom.com
#_author_:张三香 2016.03.30

Feature:手机端购买参与限时抢购活动并设置购买次数的商品
	"""
		2016.03.30新增需求8619-限时抢购添加限购购买次数的限定
			1.新建限时抢购活动页面中添加字段"购买次数"
			2.默认"购买次数"不勾选;
			3.勾选"购买次数"后显示输入框且为必填项，验证为正整数
			4.如不勾选"购买次数",则限购逻辑保持原有不变
			5.若勾选"购买次数":
				未设置"限购周期",设置"购买次数"的情况下,指活动时间内，每人可购买x次
				设置"限购周期",且设置"购买次数",指限购周期内,每人可购买x次
			6.限时抢购活动详情页:
				购买次数不勾选,活动详情页则不显示该字段
				购买次数勾选,并设置为x,活动详情页则显示"购买次数:x次"
	"""

Background:
	Given jobs登录系统:weapp
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
			"price": 100.00
		},{
			"name": "商品2",
			"is_enable_model": "启用规格",
			"model":
			{
				"models":
				{
					"M": {
						"price": 100.00,
						"stock_type": "无限"
					},
					"S": {
						"price": 200.00,
						"stock_typee": "无限"
					}
				}
			}
		}]
		"""
	Given jobs已添加支付方式:weapp
		"""
		[{
			"type": "微信支付",
			"is_active": "启用"
		}, {
			"type": "货到付款",
			"is_active": "启用"
		}]
		"""
	#会员等级
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
		}]
		"""

	Given bill关注jobs的公众号
	Given tom关注jobs的公众号
	Given jobs登录系统:weapp
	When jobs更新'tom'的会员等级:weapp
		"""
		{
			"name": "tom",
			"member_rank": "铜牌会员"
		}
		"""

@promotion
Scenario:1 购买活动期间内有购买次数限制的促销商品
	#1、商品1限时抢购活动
		#单人单次购买:不限制
		#限购周期:不限制
		#购买次数:1
		#活动时间:今天至5天后
		#会员等级:全部会员
	#2、bill在活动期间内只能购买1次

	Given jobs登录系统:weapp
	When jobs创建限时抢购活动:weapp
		"""
		[{
			"name": "商品1限时抢购",
			"promotion_title":"",
			"start_date": "今天",
			"end_date": "5天后",
			"product_name":"商品1",
			"member_grade": "全部会员",
			"count_per_purchase":"",
			"promotion_price": 80.00,
			"limit_period":"",
			"buy_counts":1
		}]
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
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
			"final_price": 80.0
		}
		"""
	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	Then bill获得创建订单失败的信息
		"""
		{
			"detail": [{
				"id": "商品1",
				"msg": "在限购周期内不能多次购买",
				"short_msg": "限制购买"
			}]
		}
		"""

@promotion
Scenario:2 购买限购周期内有购买次数限制的促销商品
	#1、商品2限时抢购活动
		#单人单次购买:2
		#限购周期:1天
		#购买次数:2次
		#活动时间:今天至5天后
		#会员等级:铜牌会员
	#2、tom在限购周期(1天)内只能购买2次

	Given jobs登录系统:weapp
	When jobs创建限时抢购活动:weapp
		"""
		[{
			"name": "商品2限时抢购",
			"promotion_title":"",
			"start_date": "今天",
			"end_date": "5天后",
			"product_name":"商品2",
			"member_grade": "铜牌会员",
			"count_per_purchase":2,
			"promotion_price": 80.00,
			"limit_period":1,
			"buy_counts":2
		}]
		"""

	When tom访问jobs的webapp
	#tom第一次购买,成功下单
	When tom购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品2",
				"model":"M",
				"count": 1
			}]
		}
		"""
	Then tom成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 80.0
		}
		"""
	#tom第二次购买,成功下单
	When tom购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品2",
				"count": 1,
				"model":"M"
			},{
				"name": "商品2",
				"count": 1,
				"model":"S"

			}]
		}
		"""
	Then tom成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 160.0
		}
		"""
	#tom第三次购买,下单失败
	When tom购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品2",
				"model":"M",
				"count": 1
			}]
		}
		"""
	Then tom获得创建订单失败的信息
		"""
		{
			"detail": [{
				"id": "商品1",
				"msg": "在限购周期内不能多次购买",
				"short_msg": "限制购买"
			}]
		}
		"""

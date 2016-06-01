# watcher: zhangsanxiang@weizoom.com,benchi@weizoom.com
#_author_：张三香 2015.12.14
#_editor_: 三香 2016-02-02 
#根据需求【7512-未到使用时间内的优惠券显示在'未使用'中，下单时显示在'不可用'中】修改场景1

Feature:个人中心（我的优惠券、微众卡余额查询）

Background:
	Given 重置'weapp'的bdd环境
	Given jobs登录系统::weapp
	And jobs已添加商品::weapp
		"""
		[{
			"name": "商品1",
			"price": 200.00
		}]
		"""
	And jobs已添加了优惠券规则::weapp
		"""
		[{
			"name": "单品券1",
			"money": 10.00,
			"limit_counts": 1,
			"start_date": "今天",
			"end_date": "1天后",
			"coupon_id_prefix": "coupon1_id_",
			"coupon_product": "商品1"
		}, {
			"name": "全体券2",
			"money": 100.00,
			"limit_counts": 1,
			"start_date": "今天",
			"end_date": "2天后",
			"using_limit": "满50元可以使用",
			"coupon_id_prefix": "coupon2_id_"
		}, {
			"name": "未开始3",
			"money": 100.00,
			"start_date": "明天",
			"end_date": "2天后",
			"using_limit": "满50元可以使用",
			"coupon_id_prefix": "coupon3_id_"
		}]
		"""
	And jobs已有微众卡支付权限::weapp
	And jobs已添加支付方式::weapp
		"""
		[{
			"type": "微众卡支付"
		}, {
			"type": "货到付款"
		}, {
			"type": "微信支付"
		}]
		"""
	Given bill关注jobs的公众号
	Given tom关注jobs的公众号

@personCenter @myCoupon @ztq @mall3
Scenario:1 个人中心-我的优惠券
	Given jobs登录系统::weapp
	When jobs为会员发放优惠券::weapp
		"""
		{
			"name": "单品券1",
			"count": 1,
			"members": ["bill"],
			"coupon_ids": ["coupon1_id_1"]
		}
		"""
	When jobs为会员发放优惠券::weapp
		"""
		{
			"name": "全体券2",
			"count": 1,
			"members": ["bill"],
			"coupon_ids": ["coupon2_id_1"]
		}
		"""
	When jobs为会员发放优惠券::weapp
		"""
		{
			"name": "未开始3",
			"count": 1,
			"members": ["bill"],
			"coupon_ids": ["coupon3_id_1"]
		}
		"""
	When bill访问jobs的webapp
	Then bill能获得优惠券列表
		"""
		{
			"unused_coupons":
				[{
					"coupon_id": "coupon3_id_1",
					"money": 100.00,
					"status": "未使用"
				},{
					"coupon_id": "coupon2_id_1",
					"money": 100.00,
					"status": "未使用"
				},{
					"coupon_id": "coupon1_id_1",
					"money": 10.00,
					"status": "未使用"
				}],
			"used_coupons":[],
			"expired_coupons":[]
		}
		"""

	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
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
			"status": "待支付",
			"final_price": 100.00,
			"product_price": 200.00,
			"coupon_money": 100.00
		}
		"""
	Then bill能获得优惠券列表
		"""
		{
			"unused_coupons":
				[{
					"coupon_id": "coupon3_id_1",
					"money": 100.00,
					"status": "未使用"
				},{
					"coupon_id": "coupon1_id_1",
					"money": 10.00,
					"status": "未使用"
				}],
			"used_coupons":
				[{
					"coupon_id": "coupon2_id_1",
					"money": 100.00,
					"status": "已使用"
				}],
			"expired_coupons":[]
		}
		"""


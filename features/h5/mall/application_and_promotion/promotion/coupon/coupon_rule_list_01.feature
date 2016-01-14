#_author_:张三香 2016.01.14

#针对bug补充：（功能问题）通过分享红包领取优惠券后，后台优惠券的'领取人/次'统计不对

Feature:后台优惠列表中"领取人/次"的验证

Background:
	Given jobs登录系统
	And jobs已添加支付方式
		"""
		[{
			"type":"货到付款"
		},{
			"type":"微信支付"
		},{
			"type":"支付宝"
		}]
		"""
	And jobs已添加商品
		"""
		[{
			"name": "商品1",
			"price": 100.00
		}]
		"""
	And bill关注jobs的公众号
	And tom关注jobs的公众号
	When jobs添加优惠券规则
		"""
		[{
			"name": "优惠券1",
			"money": 100.00,
			"count": 5,
			"limit_counts":"无限",
			"start_date": "今天",
			"end_date": "1天后",
			"coupon_id_prefix": "coupon1_id_"
		}, {
			"name": "优惠券2",
			"money": 200.00,
			"count": 5,
			"limit_counts": 1,
			"start_date": "今天",
			"end_date": "1天后",
			"coupon_id_prefix": "coupon2_id_",
			"coupon_product": "商品1"
		}]
		"""

@promotion @promotionCoupon
Scenario:1 后台给会员发放优惠券，查看优惠列表中的"领取人/次"
	#校验无领取限制的优惠券1
	Given jobs登录系统
	Then jobs能获得优惠券规则列表
		"""
		[{
			"name": "优惠券2",
			"remained_count": 5,
			"limit_counts": 1,
			"get_person_count":0,
			"get_number":0,
			"start_date": "今天",
			"end_date": "1天后"
		}, {
			"name": "优惠券1",
			"remained_count": 5,
			"limit_counts":"无限",
			"get_person_count":0,
			"get_number":0,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""
	When jobs为会员发放优惠券
		"""
		{
			"name": "优惠券1",
			"count": 1,
			"members": ["bill"],
			"coupon_ids": ["coupon1_id_1"]
		}
		"""
	Then jobs能获得优惠券规则列表
		"""
		[{
			"name": "优惠券2",
			"remained_count": 5,
			"limit_counts": 1,
			"get_person_count":0,
			"get_number":0,
			"start_date": "今天",
			"end_date": "1天后"
		}, {
			"name": "优惠券1",
			"remained_count": 4,
			"limit_counts":"无限",
			"get_person_count":1,
			"get_number":1,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""
	When jobs为会员发放优惠券
		"""
		{
			"name": "优惠券1",
			"count": 1,
			"members": ["bill","tom"],
			"coupon_ids": ["coupon1_id_3","coupon1_id_2"]
		}
		"""
	Then jobs能获得优惠券规则列表
		"""
		[{
			"name": "优惠券2",
			"remained_count": 5,
			"limit_counts": 1,
			"get_person_count":0,
			"get_number":0,
			"start_date": "今天",
			"end_date": "1天后"
		}, {
			"name": "优惠券1",
			"remained_count": 2,
			"limit_counts":"无限",
			"get_person_count":2,
			"get_number":3,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""

	#校验有领取限制的优惠券2
	When jobs为会员发放优惠券
		"""
		{
			"name": "优惠券2",
			"count": 1,
			"members": ["bill", "tom"],
			"coupon_ids": ["coupon2_id_2", "coupon2_id_1"]
		}
		"""
	Then jobs能获得优惠券规则列表
		"""
		[{
			"name": "优惠券2",
			"remained_count": 3,
			"limit_counts": 1,
			"get_person_count":2,
			"get_number":2,
			"start_date": "今天",
			"end_date": "1天后"
		}, {
			"name": "优惠券1",
			"remained_count": 2,
			"limit_counts":"无限",
			"get_person_count":2,
			"get_number":3,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""
	When jobs为会员发放优惠券
		"""
		{
			"name": "优惠券2",
			"count": 1,
			"members": ["bill"],
			"coupon_ids": ["coupon2_id_3"]
		}
		"""
	Then jobs能获得优惠券规则列表
		"""
		[{
			"name": "优惠券2",
			"remained_count": 3,
			"limit_counts": 1,
			"get_person_count":2,
			"get_number":2,
			"start_date": "今天",
			"end_date": "1天后"
		}, {
			"name": "优惠券1",
			"remained_count": 2,
			"limit_counts":"无限",
			"get_person_count":2,
			"get_number":3,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""

@promotion @promotionCoupon
Scenario:2 会员购买时输入未领取的优惠券码后，查看优惠列表中的"领取人/次"
	Given jobs登录系统
	Then jobs能获得优惠券规则列表
		"""
		[{
			"name": "优惠券2",
			"remained_count": 5,
			"limit_counts": 1,
			"get_person_count":0,
			"get_number":0,
			"start_date": "今天",
			"end_date": "1天后"
		}, {
			"name": "优惠券1",
			"remained_count": 5,
			"limit_counts":"无限",
			"get_person_count":0,
			"get_number":0,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"001",
			"pay_type": "支付宝",
			"products":[{
				"name":"商品1",
				"price":100.00,
				"count":1
			}],
			"coupon": "coupon1_id_1"
		}
		"""
	Given jobs登录系统
	Then jobs能获得优惠券规则列表
		"""
		[{
			"name": "优惠券2",
			"remained_count": 5,
			"limit_counts": 1,
			"get_person_count":0,
			"get_number":0,
			"start_date": "今天",
			"end_date": "1天后"
		}, {
			"name": "优惠券1",
			"remained_count": 4,
			"limit_counts":"无限",
			"get_person_count":0,
			"get_number":0,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""

	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"002",
			"pay_type": "微信支付",
			"products":[{
				"name":"商品1",
				"price":100.00,
				"count":1
			}],
			"coupon": "coupon1_id_2"
		}
		"""
	Given jobs登录系统
	Then jobs能获得优惠券规则列表
		"""
		[{
			"name": "优惠券2",
			"remained_count": 5,
			"limit_counts": 1,
			"get_person_count":0,
			"get_number":0,
			"start_date": "今天",
			"end_date": "1天后"
		}, {
			"name": "优惠券1",
			"remained_count": 3,
			"limit_counts":"无限",
			"get_person_count":0,
			"get_number":0,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""

	When tom访问jobs的webapp
	When tom购买jobs的商品
		"""
		{
			"order_id":"003",
			"pay_type": "微信支付",
			"products":[{
				"name":"商品1",
				"price":100.00,
				"count":1
			}],
			"coupon": "coupon1_id_3"
		}
		"""
	Given jobs登录系统
	Then jobs能获得优惠券规则列表
		"""
		[{
			"name": "优惠券2",
			"remained_count": 5,
			"limit_counts": 1,
			"get_person_count":0,
			"get_number":0,
			"start_date": "今天",
			"end_date": "1天后"
		}, {
			"name": "优惠券1",
			"remained_count": 2,
			"limit_counts":"无限",
			"get_person_count":0,
			"get_number":0,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""

@promotion @promotionCoupon
Scenario:3 通过分享红包（下单领取）领取优惠券后,查看优惠列表中的"领取人/次"
	Given jobs登录系统
	When jobs添加分享红包
		"""
		[{
			"name": "红包1",
			"prize_info": "优惠券1",
			"is_permanant_active": false,
			"start_date": "今天",
			"end_date": "2天后",
			"limit_money": "100",
			"receive_method": "下单领取",
			"detail": "活动说明",
			"share_pic": "/static/upload/6_20140710/1404981209095_5.jpg",
			"remark": "分享有礼"
		}]
		"""
	When jobs'开启'分享红包'红包1'
	When bill访问jobs的webapp
	And bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	And bill使用支付方式'货到付款'进行支付
	Then bill'能够'领取分享红包
	When bill把jobs的分享红包链接分享到朋友圈
	Given jobs登录系统
	Then jobs能获得优惠券规则列表
		"""
		[{
			"name": "优惠券2",
			"remained_count": 5,
			"limit_counts": 1,
			"get_person_count":0,
			"get_number":0,
			"start_date": "今天",
			"end_date": "1天后"
		}, {
			"name": "优惠券1",
			"remained_count": 4,
			"limit_counts":"无限",
			"get_person_count":1,
			"get_number":1,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""

	When tom访问jobs的webapp
	When tom点击bill分享红包链接
	Given jobs登录系统
	Then jobs能获得优惠券规则列表
		"""
		[{
			"name": "优惠券2",
			"remained_count": 5,
			"limit_counts": 1,
			"get_person_count":0,
			"get_number":0,
			"start_date": "今天",
			"end_date": "1天后"
		}, {
			"name": "优惠券1",
			"remained_count": 3,
			"limit_counts":"无限",
			"get_person_count":2,
			"get_number":2,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""

	When tom访问jobs的webapp
	And tom购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1
			}],
			"coupon": "coupon1_id_2"
		}
		"""
	Then tom'能够'领取分享红包
	When tom把jobs的分享红包链接分享到朋友圈
	Given jobs登录系统
	Then jobs能获得优惠券规则列表
		"""
		[{
			"name": "优惠券2",
			"remained_count": 5,
			"limit_counts": 1,
			"get_person_count":0,
			"get_number":0,
			"start_date": "今天",
			"end_date": "1天后"
		}, {
			"name": "优惠券1",
			"remained_count": 2,
			"limit_counts":"无限",
			"get_person_count":2,
			"get_number":3,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""

	When bill访问jobs的webapp
	When bill点击tom分享红包链接
	Given jobs登录系统
	Then jobs能获得优惠券规则列表
		"""
		[{
			"name": "优惠券2",
			"remained_count": 5,
			"limit_counts": 1,
			"get_person_count":0,
			"get_number":0,
			"start_date": "今天",
			"end_date": "1天后"
		}, {
			"name": "优惠券1",
			"remained_count": 1,
			"limit_counts":"无限",
			"get_person_count":2,
			"get_number":4,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""

@promotion @promotionCoupon
Scenario:4 通过分享红包（图文领取）领取优惠券后,查看优惠列表中的"领取人/次"
	Given jobs登录系统
	When jobs添加分享红包
		"""
		[{
			"name": "红包1",
			"prize_info": "优惠券1",
			"is_permanant_active": true,
			"limit_money": "无限制",
			"receive_method":"图文领取",
			"detail": "图文领取领红包1",
			"share_pic": "/static/upload/6_20140710/1404981209095_5.jpg",
			"remark":"分享描述1"
		}]
		"""
	When jobs已添加单图文
		"""
		[{
			"title":"红包1单图文",
			"cover": [{
				"url": "/standard_static/test_resource_img/hangzhou3.jpg"
			}],
			"cover_in_the_text":"false",
			"summary":"红包1图文文本摘要",
			"content":"红包1图文文本内容",
			"jump_url":"分享红包-红包1"
		}]
		"""
	When jobs已添加关键词自动回复规则
		"""
		[{
			"rules_name":"规则1",
			"keyword": [{
					"keyword": "红包1",
					"type": "equal"
				}],
			"keyword_reply": [{
					"reply_content":"红包1单图文",
					"reply_type":"text_picture"
				}]
		}]
		"""

	When 清空浏览器
	When bill在微信中向jobs的公众号发送消息'红包1'
	Then bill收到自动回复'红包1单图文'
	When bill点击图文"红包1单图文"
	Given jobs登录系统
	Then jobs能获得优惠券规则列表
		"""
		[{
			"name": "优惠券2",
			"remained_count": 5,
			"get_person_count":0,
			"get_number":0,
			"start_date": "今天",
			"end_date": "1天后"
		}, {
			"name": "优惠券1",
			"remained_count": 4,
			"get_person_count":1,
			"get_number":1,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""
	When bill把jobs的分享红包链接分享到朋友圈

	When 清空浏览器
	When tom访问jobs的webapp
	When tom点击bill分享红包链接

	When tom在微信中向jobs的公众号发送消息'红包1'
	Then tom收到自动回复'红包1单图文'
	When tom点击图文"红包1单图文"
	When tom把jobs的分享红包链接分享到朋友圈

	When 清空浏览器
	When bill访问jobs的webapp
	When bill点击tom分享红包链接
	Given jobs登录系统
	Then jobs能获得优惠券规则列表
		"""
		[{
			"name": "优惠券2",
			"remained_count": 5,
			"get_person_count":0,
			"get_number":0,
			"start_date": "今天",
			"end_date": "1天后"
		}, {
			"name": "优惠券1",
			"remained_count": 1,
			"get_person_count":2,
			"get_number":4,
			"start_date": "今天",
			"end_date": "1天后"
		}]
		"""
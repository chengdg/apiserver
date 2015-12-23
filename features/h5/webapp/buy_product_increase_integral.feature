#author: 冯雪静
#author: 王丽
#editor: 张三香 2015.10.16

Feature:用户通过分享链接购买商品，给分享者增加积分
"""
	tom通过bill分享jobs商品的链接购买商品，给bill增加积分


	关于 "jobs设置会员积分策略" 的说明
	1、"be_member_increase_count"：关注公众账号
	2、"click_shared_url_increase_count_before_buy":分享链接给好友点击
	3、"buy_award_count_for_buyer":购买商品返积分
		"order_money_percentage_for_each_buy":购买商品返积分额外积分奖励
	4、"buy_via_shared_url_increase_count_for_author":分享链接购买
	5、"buy_via_offline_increase_count_for_author":推荐关注的好友购买奖励
		"buy_via_offline_increase_count_percentage_for_author":推荐关注的好友购买奖励额外积分奖励
	6、订单积分抵扣上限设置
	7、商品好评送积分
"""

Background:
	Given jobs登录系统
	And jobs已添加支付方式
		"""
		[{
			"type": "货到付款",
			"is_active": "启用"
		},{
			"type": "微信支付",
			"is_active": "启用"
		},{
			"type": "支付宝",
			"is_active": "启用"
		}]
		"""
	And jobs已添加商品
		"""
		[{
			"name":"商品1",
			"price":100.00
		},{
			"name":"商品2",
			"price":100.00
		}]	
		"""
	And jobs设定会员积分策略
		"""
		{
			"be_member_increase_count":20,
			"click_shared_url_increase_count":11, 
			"buy_award_count_for_buyer":21,
			"order_money_percentage_for_each_buy":0.5,
			"buy_via_shared_url_increase_count_for_author":31, 
			"buy_via_offline_increase_count_for_author":30,
			"buy_via_offline_increase_count_percentage_for_author":0.2,
			"buy_increase_count_for_father":10
		}
		"""

	And bill关注jobs的公众号
	And 开启手动清除cookie模式

@mall2 @member @member.shared_integral 
Scenario:1 点击给未购买的分享者增加积分
	bill没有购买jobs的商品1，把商品1的链接分享到朋友圈
	1.nokia点击bill分享的链接后，给bill增加积分
	2.nokia再次点击bill分享的链接后，不给bill增加积分
	3.tom点击bill分享的链接后，给bill增加积分
	4.tom再次点击bill分享的链接后，不给bill增加积分

	When 清空浏览器
	When bill访问jobs的webapp
	When bill获得jobs的20会员积分
	Then bill在jobs的webapp中拥有20会员积分
	Then bill在jobs的webapp中获得积分日志
		"""
		[{
			"content":"首次关注",
			"integral":20
		}]
		"""
	#When bill把jobs的微站链接分享到朋友圈
	When bill把jobs的商品"商品1"的链接分享到朋友圈
	
	#nokia多次点击bill分享的统一链接，只奖励一次积分
	When 清空浏览器
	When nokia点击bill分享链接
	When nokia点击bill分享链接
	When 清空浏览器
	When bill访问jobs的webapp
	Then bill在jobs的webapp中拥有31会员积分
	Then bill在jobs的webapp中获得积分日志
		"""
		[{
			"content":"好友点击分享链接奖励",
			"integral":11
		},{
			"content":"首次关注",
			"integral":20
		}]
		"""
	#清空cookie，Nokia再次点击之前已点击的bill的分享链接，获得积分奖励
	When 清空浏览器
	When nokia点击bill分享链接
	When 清空浏览器
	When bill访问jobs的webapp
	Then bill在jobs的webapp中拥有42会员积分
	Then bill在jobs的webapp中获得积分日志
		"""
		[{
			"content":"好友点击分享链接奖励",
			"integral":11
		},{
			"content":"好友点击分享链接奖励",
			"integral":11
		},{
			"content":"首次关注",
			"integral":20
		}]
		"""
	When 清空浏览器
	When tom点击bill分享链接
	When tom点击bill分享链接
	When bill访问jobs的webapp
	Then bill在jobs的webapp中拥有53会员积分
	Then bill在jobs的webapp中获得积分日志
		"""
		[{
			"content":"好友点击分享链接奖励",
			"integral":11
		},{
			"content":"好友点击分享链接奖励",
			"integral":11
		},{
			"content":"好友点击分享链接奖励",
			"integral":11
		},{
			"content":"首次关注",
			"integral":20
		}]
		"""

@mall2 @member @member.shared_integral 
Scenario:2 点击给已购买的分享者增加积分
	bill购买jobs的商品1后，把商品1的链接分享到朋友圈
	1.nokia点击bill分享的链接后，给bill增加积分
	2.nokia再次点击bill分享的链接后，不给bill增加积分
	3.tom点击bill分享的链接后，给bill增加积分
	4.tom再次点击bill分享的链接后，不给bill增加积分

	When 清空浏览器
	When bill访问jobs的webapp
	When bill获得jobs的20会员积分
	Then bill在jobs的webapp中拥有20会员积分
	Then bill在jobs的webapp中获得积分日志
		"""
		[{
			"content":"首次关注",
			"integral":20
		}]
		"""
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"count": 1
			}],
			"customer_message": "bill的订单备注1"
		}
		"""
	When bill使用支付方式'货到付款'进行支付
	Then bill支付订单成功
		"""
		{
			"status": "待发货",
			"final_price": 100.00,
			"products": [{
				"name": "商品1",
				"price":100.00,
				"count": 1
			}]
		}
		"""
	When bill把jobs的商品"商品1"的链接分享到朋友圈
	When 清空浏览器
	When bill访问jobs的webapp
	Then bill在jobs的webapp中拥有20会员积分
	Then bill在jobs的webapp中获得积分日志
		"""
		[{
			"content":"首次关注",
			"integral":20
		}]
		"""

	When 清空浏览器
	Given jobs登录系统
	When jobs对最新订单进行发货
	When jobs'完成'最新订单
	When 清空浏览器
	When bill访问jobs的webapp
	Then bill在jobs的webapp中拥有91会员积分
	Then bill在jobs的webapp中获得积分日志
		"""
		[{
			"content":"购物返利",
			"integral":50
		},{
			"content":"购物返利",
			"integral":21
		},{
			"content":"首次关注",
			"integral":20
		}]
		"""

	When 清空浏览器
	When nokia点击bill分享链接
	When nokia点击bill分享链接
	When bill访问jobs的webapp
	Then bill在jobs的webapp中拥有102会员积分
	Then bill在jobs的webapp中获得积分日志
		"""
		[{
			"content":"好友点击分享链接奖励",
			"integral":11
		},{
			"content":"购物返利",
			"integral":50
		},{
			"content":"购物返利",
			"integral":21
		},
		{
			"content":"首次关注",
			"integral":20
		}]
		"""
	When 清空浏览器
	When tom点击bill分享链接
	When tom点击bill分享链接
	When bill访问jobs的webapp
	Then bill在jobs的webapp中拥有113会员积分
	Then bill在jobs的webapp中获得积分日志
		"""
		[{
			"content":"好友点击分享链接奖励",
			"integral":11
		},{
			"content":"好友点击分享链接奖励",
			"integral":11
		},{
			"content":"购物返利",
			"integral":50
		},{
			"content":"购物返利",
			"integral":21
		},{
			"content":"首次关注",
			"integral":20
		}]
		"""

@mall2 @member @member.shared_integral
Scenario:3 通过分享链接购买后给分享者增加积分
	bill把jobs的商品2的链接分享到朋友圈
	1.nokia点击bill分享的链接并购买，给bill增加积分
	2.nokia再次点击bill分享的链接并购买，不给bill增加积分
	3.tom点击bill分享的链接并购买，给bill增加积分

	When 清空浏览器
	When bill访问jobs的webapp
	When bill获得jobs的20会员积分
	Then bill在jobs的webapp中拥有20会员积分
	Then bill在jobs的webapp中获得积分日志
		"""
		[{
			"content":"首次关注",
			"integral":20
		}]
		"""
	When bill把jobs的商品"商品2"的链接分享到朋友圈

	When 清空浏览器
	When nokia点击bill分享链接
	When nokia通过bill分享的链接购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品2",
				"count": 1
			}]
		}
		"""
	When nokia使用支付方式'货到付款'进行支付
	Then nokia支付订单成功
		"""
		{
			"status": "待发货",
			"final_price": 100.00,
			"products": [{
				"name": "商品2",
				"price":100.00,
				"count": 1
			}]
		}
		"""

	When 清空浏览器
	When bill访问jobs的webapp
	Then bill在jobs的webapp中拥有31会员积分
	Then bill在jobs的webapp中获得积分日志
		"""
		[{
			"content":"好友点击分享链接奖励",
			"integral":11
		},{
			"content":"首次关注",
			"integral":20
		}]
		"""

	When 清空浏览器
	Given jobs登录系统
	When jobs对最新订单进行发货
	When jobs'完成'最新订单

	When 清空浏览器
	When bill访问jobs的webapp
	Then bill在jobs的webapp中拥有62会员积分
	Then bill在jobs的webapp中获得积分日志
		"""
		[{
			"content":"好友通过分享链接购买奖励",
			"integral":31
		},{
			"content":"好友点击分享链接奖励",
			"integral":11
		},{
			"content":"首次关注",
			"integral":20
		}]
		"""

	#nolia再次点击bill分享的链接并购买，再次增加积分奖励
	#清空了cookie
	When 清空浏览器
	When nokia点击bill分享链接
	When nokia通过bill分享的链接购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品2",
				"count": 1
			}],
			"customer_message": "nokia的订单备注1"
		}
		"""
	When nokia使用支付方式'货到付款'进行支付
	Then nokia支付订单成功
		"""
		{
			"status": "待发货",
			"final_price": 100.00,
			"products": [{
				"name": "商品2",
				"price":100.00,
				"count": 1
			}]
		}
		"""

	When 清空浏览器
	Given jobs登录系统
	When jobs对最新订单进行发货
	When jobs'完成'最新订单

	When 清空浏览器
	When bill访问jobs的webapp
	Then bill在jobs的webapp中拥有104会员积分
	Then bill在jobs的webapp中获得积分日志
		"""
		[{
			"content":"好友通过分享链接购买奖励",
			"integral":31
		},{
			"content":"好友点击分享链接奖励",
			"integral":11
		},{
			"content":"好友通过分享链接购买奖励",
			"integral":31
		},{
			"content":"好友点击分享链接奖励",
			"integral":11
		},{
			"content":"首次关注",
			"integral":20
		}]
		"""
	#tom点击bill分享的链接并购买，获得积分奖励
	When 清空浏览器
	When tom点击bill分享链接
	When tom通过bill分享的链接购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品2",
				"count": 1
			}],
			"customer_message": "tom的订单备注1"
		}
		"""
	When tom使用支付方式'货到付款'进行支付
	Then tom支付订单成功
		"""
		{
			"status": "待发货",
			"final_price": 100.00,
			"products": [{
				"name": "商品2",
				"price":100.00,
				"count": 1
			}]
		}
		"""
	When 清空浏览器
	Given jobs登录系统
	When jobs对最新订单进行发货
	When jobs'完成'最新订单

	When 清空浏览器
	When bill访问jobs的webapp
	Then bill在jobs的webapp中拥有146会员积分
	Then bill在jobs的webapp中获得积分日志
		"""
		[{
			"content":"好友通过分享链接购买奖励",
			"integral":31
		},{
			"content":"好友点击分享链接奖励",
			"integral":11
		},{
			"content":"好友通过分享链接购买奖励",
			"integral":31
		},{
			"content":"好友点击分享链接奖励",
			"integral":11
		},{
			"content":"好友通过分享链接购买奖励",
			"integral":31
		},{
			"content":"好友点击分享链接奖励",
			"integral":11
		},{
			"content":"首次关注",
			"integral":20
		}]
		"""

@mall2 @member @member.shared_integral
Scenario:4 每次购买给邀请者增加积分
	1.bill是tom的邀请者
	2.tom每次购买jobs的商品，给bill增加积分

	When 清空浏览器
	When bill关注jobs的公众号
	When bill访问jobs的webapp
	When bill把jobs的微站链接分享到朋友圈
	
	When 清空浏览器
	When tom点击bill分享链接
	When tom关注jobs的公众号
	When tom访问jobs的webapp
	When 清空浏览器
	Given jobs登录系统
	Then jobs能获取到bill的好友
		"""
		[{
			"name": "tom",
			"source": "会员分享",
			"is_fans": "是"
		}]
		"""
	When 清空浏览器
	When tom访问jobs的webapp
	When tom购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品2",
				"count": 1
			}]
		}
		"""

	When 清空浏览器
	Given jobs登录系统
	When jobs'支付'最新订单
	When jobs对最新订单进行发货
	When jobs'完成'最新订单

	When 清空浏览器
	When bill访问jobs的webapp
	Then bill在jobs的webapp中拥有81会员积分
	Then bill在jobs的webapp中获得积分日志
		"""
		[{
			"content":"推荐关注的好友购买奖励",
			"integral":20
		},{
			"content":"推荐关注的好友购买奖励",
			"integral":30
		},{
			"content":"好友点击分享链接奖励",
			"integral":11
		},{
			"content":"首次关注",
			"integral":20
		}]
		"""

@mall2 @member @member.shared_integral
Scenario:5 购买商品返积分 基础积分设为0，额外积分奖励不为零，此项整体积分奖励没有

	Given jobs登录系统
	And jobs已添加商品
		"""
		[{
			"name":"商品3",
			"price":150.00
		}]
		"""
	And jobs设定会员积分策略
		"""
		{
			"buy_award_count_for_buyer":0,
			"order_money_percentage_for_each_buy":0.01
		}
		"""
	When 清空浏览器
	When bill关注jobs的公众号
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品3",
				"count": 1
			}]
		}
		"""

	When 清空浏览器
	Given jobs登录系统
	When jobs'支付'最新订单
	When jobs对最新订单进行发货
	When jobs'完成'最新订单
	When 清空浏览器
	When bill访问jobs的webapp
	Then bill在jobs的webapp中拥有21会员积分
	Then bill在jobs的webapp中获得积分日志
		"""
		[{
			"content":"购物返利",
			"integral":1
		},{
			"content":"首次关注",
			"integral":20
		}]
		"""

@mall2 @member @member.shared_integral
Scenario:6 基础积分不为0，额外积分奖励，小数部分直接舍掉，最后积分为零的，没有积分明细奖励记录

	Given jobs登录系统
	And jobs已添加商品
		"""
		[{
			"name":"商品4",
			"price":50.00
		}]	
		"""
	And jobs设定会员积分策略
		"""
		{
			"buy_award_count_for_buyer":10,
			"order_money_percentage_for_each_buy":0.01
		}
		"""
	When 清空浏览器
	When bill关注jobs的公众号
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品4",
				"count": 1
			}]
		}
		"""

	When 清空浏览器
	Given jobs登录系统
	When jobs'支付'最新订单
	When jobs对最新订单进行发货
	When jobs'完成'最新订单
	When 清空浏览器
	When bill访问jobs的webapp
	Then bill在jobs的webapp中拥有30会员积分
	Then bill在jobs的webapp中获得积分日志
		"""
		[{
			"content":"购物返利",
			"integral":10
		},{
			"content":"首次关注",
			"integral":20
		}]
		"""

@mall2 @member @member.shared_integral
Scenario:7 推荐关注的好友购买奖励 基础积分设为0，额外积分奖励不为零，此项整体积分奖励没有
	1.bill是tom的邀请者
	2.tom每次购买jobs的商品，给bill增加积分

	Given jobs登录系统
	And jobs设定会员积分策略
		"""
		{
			"buy_via_offline_increase_count_for_author":0,
			"buy_via_offline_increase_count_percentage_for_author":0.01
		}
		"""

	When 清空浏览器
	When bill关注jobs的公众号
	When bill访问jobs的webapp
	When bill把jobs的微站链接分享到朋友圈
	
	When 清空浏览器
	When tom点击bill分享链接
	When tom关注jobs的公众号
	When tom访问jobs的webapp
	When 清空浏览器
	Given jobs登录系统
	Then jobs能获取到bill的好友
		"""
		[{
			"name": "tom",
			"source": "会员分享",
			"is_fans": "是"
		}]
		"""
	When 清空浏览器
	When tom访问jobs的webapp
	When tom购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品2",
				"count": 1
			}]
		}
		"""
	
	When 清空浏览器
	Given jobs登录系统
	When jobs'支付'最新订单
	When jobs对最新订单进行发货
	When jobs'完成'最新订单
	When 清空浏览器
	When bill访问jobs的webapp
	Then bill在jobs的webapp中拥有21会员积分
	Then bill在jobs的webapp中获得积分日志
		"""
		[{
			"content":"推荐关注的好友购买奖励",
			"integral":1
		},{
			"content":"首次关注",
			"integral":20
		}]
		"""
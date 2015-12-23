#author: 崔帅帅
#author: 王丽
#editor: 张三香 2015.10.16

Feature: 微信用户关注公众号成为系统会员
"""
	# __author__ : "王丽"
	2015-9新增需求
	1、会员分组默认有个分组："未分组"，不能修改（没有修改框）、不能删除（没有删除按钮）
	2、新增会员和调整没有分组的会员，默认进入"未分组"
"""

Background:
	Given jobs登录系统
	And 开启手动清除cookie模式
	And jobs设定会员积分策略
		"""
		{
			"be_member_increase_count": 20
		}
		"""
	And jobs添加会员等级
		"""
		[{
			"name": "银牌会员",
			"upgrade": "手动升级",
			"shop_discount": "1"
		},{
			"name": "金牌会员",
			"upgrade": "手动升级",
			"shop_discount": "9.8"
		}]
		"""
	And jobs添加会员分组
		"""
		{
			"tag_id_1": "分组1",
			"tag_id_2": "分组2",
			"tag_id_3": "分组3"
		}
		"""
	And jobs已添加商品
		"""
		[{
			"name":"商品1",
			"price":100.00
		}]
		"""
	When jobs添加支付方式
		"""
		[{
			"type": "货到付款",
			"description": "我的货到付款",
			"is_active": "启用"
		}]
		"""

@mall2 @member @memberList   @crm
Scenario:1 微信用户关注公众号成为会员
	微信用户关注jobs公众号成为jobs的会员
	1.bill直接关注jobs的公众号,生成会员列表
	2.tom通过bill分享的链接关注jobs的公众号,生成会员列表
	3.nokia通过bill分享的链接关注jobs的公众号,生成会员列表
	4.tom1通过tom推荐扫码关注jobs的公众号,生成会员列表

	When bill关注jobs的公众号
	When bill访问jobs的webapp
	When bill获得jobs的20会员积分
	Then bill在jobs的webapp中拥有20会员积分
	Given jobs登录系统
	Then jobs可以获得会员列表
		"""
		[{
			"name": "bill",
			"member_rank": "普通会员",
			"pay_money": 0.00,
			"unit_price": 0.00,
			"integral": 20,
			"friend_count": 0,
			"pay_times": 0,
			"source": "直接关注",
			"tags": ["未分组"],
			"status": "已关注"
		}]
		"""
	And jobs能获得bill的积分日志
		"""
		[{
			"content": "首次关注",
			"integral": 20
		}]
		"""
	#When bill把jobs的微站链接分享到朋友圈
	When bill把jobs的商品"商品1"的链接分享到朋友圈
	When bill获得db中在jobs公众号中的mt为'mt_{bill_jobs}'

	When 清空浏览器
	When tom点击bill分享链接
	Then tom在jobs公众号中有uuid对应的webapp_user
	Then 浏览器cookie包含"[fmt, uuid]"
	Then 浏览器cookie等于
		"""
		{"fmt":"mt_{bill_jobs}"}
		"""
	When tom关注jobs的公众号
	When tom访问jobs的webapp
	When tom获得jobs的20会员积分
	Then tom在jobs的webapp中拥有20会员积分
	Given jobs登录系统
	Then jobs可以获得会员列表
		"""
		[{
			"name": "tom",
			"member_rank": "普通会员",
			"pay_money": 0.00,
			"unit_price": 0.00,
			"pay_times": 0,
			"integral": 20,
			"friend_count": 1,
			"source": "会员分享",
			"tags": ["未分组"],
			"status": "已关注"
		},{
			"name": "bill",
			"member_rank": "普通会员",
			"pay_money": 0.00,
			"unit_price": 0.00,
			"integral": 20,
			"friend_count": 1,
			"pay_times": 0,
			"source": "直接关注",
			"tags": ["未分组"],
			"status": "已关注"
		}]
		"""
	And jobs能获得tom的积分日志
		"""
		[{
			"content": "首次关注",
			"integral": 20
		}]
		"""

	When 清空浏览器
	When nokia点击bill分享链接
	Then nokia在jobs公众号中有uuid对应的webapp_user
	Then 浏览器cookie包含"[fmt, uuid]"
	Then 浏览器cookie等于
		"""
		{"fmt":"mt_{bill_jobs}"}
		"""
	When nokia关注jobs的公众号
	When nokia访问jobs的webapp
	When nokia获得jobs的20会员积分
	Then nokia在jobs的webapp中拥有20会员积分
	Given jobs登录系统
	Then jobs可以获得会员列表
		"""
		[{
			"name": "nokia",
			"member_rank": "普通会员",
			"pay_money": 0.00,
			"unit_price": 0.00,
			"integral": 20,
			"friend_count": 1,
			"pay_times": 0,
			"source": "会员分享",
			"tags": ["未分组"],
			"status": "已关注"
		},{
			"name": "tom",
			"member_rank": "普通会员",
			"pay_money": 0.00,
			"unit_price": 0.00,
			"pay_times": 0,
			"integral": 20,
			"friend_count": 1,
			"source": "会员分享",
			"tags": ["未分组"],
			"status": "已关注"
		},{
			"name": "bill",
			"member_rank": "普通会员",
			"pay_money": 0.00,
			"unit_price": 0.00,
			"integral": 20,
			"friend_count": 2,
			"pay_times": 0,
			"source": "直接关注",
			"tags": ["未分组"],
			"status": "已关注"
		}]
		"""
	And jobs能获得nokia的积分日志
		"""
		[{
			"content": "首次关注",
			"integral": 20
		}]
		"""
	#tom把jobs的微站二维码推广给tom1
	When tom访问jobs的webapp
	#When tom把jobs的二维码推广给tom1
	When tom1关注jobs的公众号
	When tom1访问jobs的webapp
	When tom1获得jobs的20会员积分
	Then tom1在jobs的webapp中拥有20会员积分
	Given jobs登录系统
	Then jobs可以获得会员列表
		"""
		[{
			"name": "tom1",
			"member_rank": "普通会员",
			"pay_money": 0.00,
			"unit_price": 0.00,
			"integral": 20,
			"friend_count": 0,
			"pay_times": 0,
			"source": "直接关注",
			"tags": ["未分组"],
			"status": "已关注"
		},{
			"name": "nokia",
			"member_rank": "普通会员",
			"pay_money": 0.00,
			"unit_price": 0.00,
			"integral": 20,
			"friend_count": 1,
			"pay_times": 0,
			"source": "会员分享",
			"tags": ["未分组"],
			"status": "已关注"
		},{
			"name": "tom",
			"member_rank": "普通会员",
			"pay_money": 0.00,
			"unit_price": 0.00,
			"pay_times": 0,
			"integral": 20,
			"friend_count": 1,
			"source": "会员分享",
			"tags": ["未分组"],
			"status": "已关注"
		},{
			"name": "bill",
			"member_rank": "普通会员",
			"pay_money": 0.00,
			"unit_price": 0.00,
			"integral": 20,
			"friend_count": 2,
			"pay_times": 0,
			"source": "直接关注",
			"tags": ["未分组"],
			"status": "已关注"
		}]
		"""
	And jobs能获得tom1的积分日志
		"""
		[{
			"content": "首次关注",
			"integral": 20
		}]
		"""


	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1
			}]
		}
		"""
	When bill使用支付方式'货到付款'进行支付
	Given jobs登录系统
	When jobs对最新订单进行发货
	When jobs'完成'最新订单
	Then jobs可以获得会员列表
		"""
		[{
			"name": "tom1",
			"member_rank": "普通会员",
			"pay_money": 0.00,
			"unit_price": 0.00,
			"integral": 20,
			"friend_count": 0,
			"pay_times": 0,
			"source": "直接关注",
			"tags": ["未分组"],
			"status": "已关注"
		},{
			"name": "nokia",
			"member_rank": "普通会员",
			"pay_money": 0.00,
			"unit_price": 0.00,
			"integral": 20,
			"friend_count": 1,
			"pay_times": 0,
			"source": "会员分享",
			"tags": ["未分组"],
			"status": "已关注"
		},{
			"name": "tom",
			"member_rank": "普通会员",
			"pay_money": 0.00,
			"unit_price": 0.00,
			"pay_times": 0,
			"integral": 20,
			"friend_count": 1,
			"source": "会员分享",
			"tags": ["未分组"],
			"status": "已关注"
		},{
			"name": "bill",
			"member_rank": "普通会员",
			"pay_money": 100.00,
			"unit_price": 100.00,
			"integral": 20,
			"friend_count": 2,
			"pay_times": 1,
			"source": "直接关注",
			"tags": ["未分组"],
			"status": "已关注"
		}]
		"""
	When tom1访问jobs的webapp
	When tom1购买jobs的商品
		"""
		{
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1
			}]
		}
		"""
	When tom1使用支付方式'货到付款'进行支付
	Given jobs登录系统
	When jobs对最新订单进行发货
	When jobs'完成'最新订单
	Then jobs可以获得会员列表
		"""
		[{
			"name": "tom1",
			"member_rank": "普通会员",
			"pay_money": 100.00,
			"unit_price": 100.00,
			"integral": 20,
			"friend_count": 0,
			"pay_times": 1,
			"source": "直接关注",
			"tags": ["未分组"],
			"status": "已关注"
		},{
			"name": "nokia",
			"member_rank": "普通会员",
			"pay_money": 0.00,
			"unit_price": 0.00,
			"integral": 20,
			"friend_count": 1,
			"pay_times": 0,
			"source": "会员分享",
			"tags": ["未分组"],
			"status": "已关注"
		},{
			"name": "tom",
			"member_rank": "普通会员",
			"pay_money": 0.00,
			"unit_price": 0.00,
			"pay_times": 0,
			"integral": 20,
			"friend_count": 1,
			"source": "会员分享",
			"tags": ["未分组"],
			"status": "已关注"
		},{
			"name": "bill",
			"member_rank": "普通会员",
			"pay_money": 100.00,
			"unit_price": 100.00,
			"integral": 20,
			"friend_count": 2,
			"pay_times": 1,
			"source": "直接关注",
			"tags": ["未分组"],
			"status": "已关注"
		}]
		"""

	When bill取消关注jobs的公众号
	Given jobs登录系统
	Then jobs可以获得会员列表
		"""
		[{
			"name": "tom1",
			"member_rank": "普通会员",
			"pay_money": 100.00,
			"unit_price": 100.00,
			"integral": 20,
			"friend_count": 0,
			"pay_times": 1,
			"source": "直接关注",
			"tags": ["未分组"],
			"status": "已关注"
		},{
			"name": "nokia",
			"member_rank": "普通会员",
			"pay_money": 0.00,
			"unit_price": 0.00,
			"integral": 20,
			"friend_count": 1,
			"pay_times": 0,
			"source": "会员分享",
			"tags": ["未分组"],
			"status": "已关注"
		},{
			"name": "tom",
			"member_rank": "普通会员",
			"pay_money": 0.00,
			"unit_price": 0.00,
			"pay_times": 0,
			"integral": 20,
			"friend_count": 1,
			"source": "会员分享",
			"tags": ["未分组"],
			"status": "已关注"
		}]
		"""

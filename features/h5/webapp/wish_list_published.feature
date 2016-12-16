# __author__ : "冯雪静"

Feature: 在webapp中发表我想买
	"""
	发表我想买
		1.成功开通会员卡，就可以发起我想买心愿单
		2.我想买-上传图片最多5张（必填项），商品名称选填，商品来自哪个网站（京东/天猫 必选），不接受同类其他品牌 项目默认未勾选，勾选后，在列表页显示文字“注：不接受同类其他品牌”
		3.发表成功显示在我想买我发表的列表页和我想买全部列表页，以时间倒序显示
		4.开通会员卡的用户就可以看到我想买列表页，可以支持一下其他会员发表的我想买心愿单，两个会员支持/两个以上就可以达成心愿单
		5.我支持一下需要填写原因，5到30个字，在我想买的详情页也是以会员支持的倒序显示
	"""

Background:
	Given 重置'weapp'的bdd环境
	Given 设置jobs为自营平台账号::weapp
	Given jobs登录系统::weapp
	When jobs已添加支付方式::weapp
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
	When jobs开通使用微众卡权限::weapp
	When jobs添加支付方式::weapp
		"""
		[{
			"type": "微众卡支付",
			"description": "我的微众卡支付",
			"is_active": "启用"
		}]
		"""
	#添加会员卡套餐
	Given test登录管理系统::weizoom_card
	#套餐名称 套餐类型 套餐返款次数
	#开通支付费用 首次购卡金额 VIP会员返款每隔几天返多少钱 套餐总价值
	When test添加会员卡套餐::weizoom_card
		"""
		{
			"package_name": "年卡1",
			"package_type": "年卡",
			"package_refund_number": "12",
			"open_pay_cost": "365.00",
			"first_purchase_amount": "100.00",
			"VIP_member_refund": {
				"every_other_days": "30",
				"refund_amount": "100.00"
			},
			"package_value": "1200.00"
		}
		"""
	When test新建会员卡::weizoom_card
		"""
		{
			"name": "年卡会员卡",
			"prefix_value": "777",
			"card_package": "年卡1",
			"exclusive_stores": ["jobs"],
			"num":"100",
			"remark":"会员卡"
		}
		"""
	When test下订单::weizoom_card
			"""
			[{
				"card_info":[{
					"name":"年卡会员卡",
					"order_num":"10",
					"start_date":"2016-11-23 00:00",
					"end_date":"2020-11-23 00:00"
				}],
				"order_info":{
					"order_id":"0003"
				}
			}]
			"""
	And test批量激活订单'0003'的卡::weizoom_card
	When bill关注jobs的公众号
	When bill访问jobs的webapp
	When bill获取手机绑定验证码'15194857825'
	When bill使用验证码绑定手机
		"""
		{
			"phone": 15194857825
		}
		"""
	When bill开通会员卡
		"""
		{
			"pay_type":"微信支付",
			"name": "年卡会员卡",
			"id": "777000001"
		}
		"""
	Then bill成功开通会员卡
		"""
		{
			"payment_amount": "365.00",
			"refund_number": "12"
		}
		"""
	When tom关注jobs的公众号



Scenario: 1 发表我想买(填图片、商品名称、来源、勾选-不接受同类其他品牌)发表成功
	1.内容包含--图片、名称、来源、勾选-不接受同类其他品牌

	When bill访问jobs的webapp
	When bill浏览jobs的webapp的会员卡
	When bill发表我想买
		"""
		{
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品1",
			"product_source": "京东",
			"reject_same_other_brands": true,
			"time": "2016-12-07 09:10",
			"id": "001"
		}
		"""
	Then bill查看我发表的我想买'001'
		"""
		{
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品1",
			"product_source": "京东",
			"time": "2016-12-07 09:10",
			"reject_same_other_brands": true
		}
		"""
	Then bill查看我发表的我想买列表
		"""
		[{
			"member": "bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品1",
			"product_source": "京东",
			"time": "2016-12-07 09:10",
			"reject_same_other_brands": true,
			"progress": "0%"
		}]
		"""



Scenario: 2 发表我想买(填图片、来源、不勾选-不接受同类其他品牌)发表成功
	1.内容包含--图片、来源、不勾选-不接受同类其他品牌

	When bill访问jobs的webapp
	When bill浏览jobs的webapp的会员卡
	When bill发表我想买
		"""
		{
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "",
			"product_source": "天猫",
			"reject_same_other_brands": false,
			"time": "2016-12-07 10:10",
			"id": "001"
		}
		"""
	Then bill查看我发表的我想买'001'
		"""
		{
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "",
			"product_source": "天猫",
			"time": "2016-12-07 10:10",
			"reject_same_other_brands": false
		}
		"""
	Then bill查看我发表的我想买列表
		"""
		[{
			"member": "bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "",
			"product_source": "天猫",
			"time": "2016-12-07 10:10",
			"reject_same_other_brands": false,
			"progress": "0%"
		}]
		"""


Scenario: 3 发表我想买不填图片-发表失败
	1.内容包含--名称、来源、勾选-不接受同类其他品牌

	When bill访问jobs的webapp
	When bill浏览jobs的webapp的会员卡
	When bill发表我想买
		"""
		{
			"picture_list": "",
			"product_name": "商品1",
			"product_source": "天猫",
			"reject_same_other_brands": false,
			"time": "2016-12-07 11:10",
			"id": "001"
		}
		"""
	Then bill获得错误提示信息'请上传图片！'
	Then bill查看我发表的我想买'001'
		"""
		[]
		"""
	Then bill查看我发表的我想买列表
		"""
		[]
		"""



Scenario: 4 发表我想买不选来源-发表失败
	1.内容包含--图片、名称、勾选-不接受同类其他品牌

	When bill访问jobs的webapp
	When bill浏览jobs的webapp的会员卡
	When bill发表我想买
		"""
		{
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "商品1",
			"product_source": "",
			"reject_same_other_brands": false,
			"time": "2016-12-07 11:10",
			"id": "001"
		}
		"""
	Then bill获得错误提示信息'请选商品来源！'
	Then bill查看我发表的我想买'001'
		"""
		[]
		"""
	Then bill查看我发表的我想买列表
		"""
		[]
		"""



Scenario: 5 发表我想买获得列表

	When bill访问jobs的webapp
	When bill浏览jobs的webapp的会员卡
	When bill发表我想买
		"""
		{
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品1",
			"product_source": "京东",
			"reject_same_other_brands": true,
			"time": "2016-12-07 10:10",
			"id": "001"
		}
		"""
	When bill发表我想买
		"""
		{
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品2",
			"product_source": "天猫",
			"reject_same_other_brands": false,
			"time": "2016-12-07 11:10",
			"id": "002"
		}
		"""
	When bill发表我想买
		"""
		{
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品3",
			"product_source": "京东",
			"reject_same_other_brands": true,
			"time": "2016-12-07 12:10",
			"id": "003"
		}
		"""
	Then bill查看我发表的我想买列表
		"""
		[{
			"member": "bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品3",
			"product_source": "京东",
			"reject_same_other_brands": true,
			"time": "2016-12-07 12:10",
			"progress": "0%"
		}, {
			"member": "bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品2",
			"product_source": "天猫",
			"reject_same_other_brands": false,
			"time": "2016-12-07 11:10",
			"progress": "0%"
		}, {
			"member": "bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品1",
			"product_source": "京东",
			"reject_same_other_brands": true,
			"time": "2016-12-07 10:10",
			"progress": "0%"
		}]
		"""
	Then bill查看全部我想买列表
		"""
		[{
			"member": "bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品3",
			"product_source": "京东",
			"reject_same_other_brands": true,
			"time": "2016-12-07 12:10",
			"progress": "0%"
		}, {
			"member": "bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品2",
			"product_source": "天猫",
			"reject_same_other_brands": false,
			"time": "2016-12-07 11:10",
			"progress": "0%"
		}, {
			"member": "bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品1",
			"product_source": "京东",
			"reject_same_other_brands": true,
			"time": "2016-12-07 10:10",
			"progress": "0%"
		}]
		"""



Scenario: 6 获得我支持的我想买列表

	When tom访问jobs的webapp
	When tom获取手机绑定验证码'15394857825'
	When tom使用验证码绑定手机
		"""
		{
			"phone": 15394857825
		}
		"""
	When tom开通会员卡
		"""
		{
			"pay_type":"微信支付",
			"name": "年卡会员卡",
			"id": "777000002"
		}
		"""
	Then tom成功开通会员卡
		"""
		{
			"payment_amount": "365.00",
			"refund_number": "12"
		}
		"""
	When bill访问jobs的webapp
	When bill浏览jobs的webapp的会员卡
	When bill发表我想买
		"""
		{
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品1",
			"product_source": "京东",
			"reject_same_other_brands": true,
			"time": "2016-12-07 10:10",
			"id": "001"
		}
		"""
	When bill发表我想买
		"""
		{
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品2",
			"product_source": "天猫",
			"reject_same_other_brands": false,
			"time": "2016-12-07 11:10",
			"id": "002"
		}
		"""
	When bill发表我想买
		"""
		{
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品3",
			"product_source": "京东",
			"reject_same_other_brands": true,
			"time": "2016-12-07 12:10",
			"id": "003"
		}
		"""
	When tom访问jobs的webapp
	When tom浏览jobs的webapp的会员卡
	Then tom查看全部我想买列表
		"""
		[{
			"member": "bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品3",
			"product_source": "京东",
			"reject_same_other_brands": true,
			"time": "2016-12-07 12:10",
			"progress": "0%"
		}, {
			"member": "bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品2",
			"product_source": "天猫",
			"reject_same_other_brands": false,
			"time": "2016-12-07 11:10",
			"progress": "0%"
		}, {
			"member": "bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品1",
			"product_source": "京东",
			"reject_same_other_brands": true,
			"time": "2016-12-07 10:10",
			"progress": "0%"
		}]
		"""
	#支持描述5-30个字
	When tom支持会员'bill'发表的我想买'001'
		"""
		{
			"description": "我也很想买~啦啦~",
			"time": "2016-12-07 13:10"
		}
		"""
	Then tom查看我支持的我想买'001'
		"""
		{
			"member": "bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品1",
			"product_source": "京东",
			"reject_same_other_brands": true,
			"time": "2016-12-07 10:10",
			"all_supporters": [{
				"member": "tom",
				"time": "2016-12-07 13:10",
				"description": "我也很想买~啦啦~"
				}]
		}
		"""
	Then tom查看我支持的我想买列表
		"""
		{
			"member": "bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品1",
			"product_source": "京东",
			"reject_same_other_brands": true,
			"time": "2016-12-07 10:10",
			"progress": "50%"
		}
		"""
	Then tom查看全部我想买列表
		"""
		[{
			"member": "bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品3",
			"product_source": "京东",
			"reject_same_other_brands": true,
			"time": "2016-12-07 12:10",
			"progress": "0%"
		}, {
			"member": "bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品2",
			"product_source": "天猫",
			"reject_same_other_brands": false,
			"time": "2016-12-07 11:10",
			"progress": "0%"
		}, {
			"member": "bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "我想买商品1",
			"product_source": "京东",
			"reject_same_other_brands": true,
			"time": "2016-12-07 10:10",
			"progress": "0%"
		}]
		"""
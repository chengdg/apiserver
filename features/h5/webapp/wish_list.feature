Feature:我想买列表
	"""

	我想买列表：
		1、你需我猜入口是在会员卡会员钱包下方“我想买”
		2、首次进入我想买，展示功能介绍引导层，默认在全部列表页面，列表默认为空；列表有数据按照发表时间倒序排列
		3、列表和详情页，点击图片支持查看大图
		4、我发表的列表：
			（1）会员自己发表的我想买
			（2）无“支持一下”的按钮
			（3）内容包括：会员名称，发表时间（多少分钟前），来源网站，商品名称，备注（发表时勾选有备注），
			图片，进度条，支持进度百分比，操作（查看支持，采购进度）
			（4）当支持进度为0%时，不能看到“查看支持”和“采购进度”操作
			（5）当支持进度大于等于50%时，显示“查看支持”操作，点击可进入详情页，全部列表和我支持的列表一致
			（6）当支持进度大于等于100%时，显示“采购进度”操作，点击可进入进度详情，全部列表和我支持的列表一致
			（7）目前规定，支持人数达到2人，进度即为100%
			（8）商品采购完成，且上架后，如果该条数据是会员自己发表的，在我发表的列表中显示，且无“支持一下”按钮；
			如果该条数据是会员支持过的，在我支持的列表中显示该条数据，且无“支持一下”按钮；在全部列表中不显示该条数据
		5、我支持的列表：
			（1）会员支持过的我想买
			（2）无“支持一下”的按钮
			（3）数据内容同“我发表的”列表
			（4）“查看支持”和“采购进度”同“我发表的”列表规律
		6、全部列表：
			（1）全部我想买的列表，包含会员自己发表的我想买和会员支持过的我想买
			（2）会员发表的和会员支持过的我想买，均不显示“支持一下”按钮
			（3）数据内容同“我发表的”列表
			（4）“查看支持”和“采购进度”同“我发表的”列表规律
		7、会员发表我想买：
			（1）发表页面内置截图示例图片，点击“查看截图示例规范”可弹出，再次点击图片回到发表页面
			（2）提示语“您要的商品在哪个网站有卖的？可截图发给我们！”
			（3）图片为必填项，最多上传5张，可添加和删除图片（类似商品评价功能）
			（4）商品名称为选填，文本框中有默认文字：填写商品名称让我想买更快达成！
			（5）选择商品来自哪个网站：天猫、京东
			（6）备注内容，不接受同类其他品牌，可勾选，勾选后显示在我想买详情页面，不勾选不显示
			（7）点击提交后，直接跳转到我想买详情页面，提示：提交成功！
			（8）详情页只显示会员头像、名称、发表时间、来源网站、商品名称、（备注）、图片，全部支持（无数据时显示空或提示语）、
			无“支持一下”和“查看采购进度”操作

		8、会员点击“支持一下”进入支持页面编辑：
			（1）显示详情页数据和会员支持的数据（会员名称、会员发表支持时间、会员发表的内容）
			（2）显示“支持一下”按钮，如果支持进度大于等于100%时，显示“采购进度”操作，如果未达到，不显示
			（3）编辑时，文本框字数5-30个字，默认文字：说说为啥你要支持ta，5-30个字！
			（4）点击“支持一下”按钮，提示“支持成功！”
			（5）全部支持记录按支持时间倒序排列

	采销后台：（无feature）
		1、心愿单列表：
			（1）可根据会员手机号、心愿单状态、发表时间、集赞成功时间、心愿达成时间进行查询
			（2）心愿单状态：集赞中；集赞成功，待采购；采购完成，待上架；心愿达成；采购失败（后期做）
			（3）列表包括：编号、手机号、所属平台、集赞人数、状态、发表时间、商品名称、来源网站、操作
			（4）商品名称为非必填项，如果没有填，默认为--
			（5）来源网站只包括京东和天猫，手机端限制
			（6）操作：查看大图、详情
			（7）点击手机号或详情可进入心愿单详情页
		2、心愿单详情：
			（1）进度条：用户发表、集赞成功、客户签约、商品上架
			（2）数据包括：会员手机号、截图图片（可放大吗？）、商品名称（没有为--吗？）、来源网站、集赞记录
			（3）集赞记录包括会员手机号和支持时间，按支持时间倒序排列
			（4）处于集赞成功进度的心愿单详情，可点击“采购完成，等待上架”操作，进度到客户签约
			（5）如果进度条处于用户发表进度，即未集赞成功，无“采购完成，等待上架”操作？？
			（6）处于客户签约进度的心愿单详情，可点击“商品已上架”，进度到商品商家，进度完成，无操作


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
					"order_id":"0001"
				}
			}]
			"""
	And test批量激活订单'0001'的卡::weizoom_card

	Given bill关注jobs的公众号
	Given tom关注jobs的公众号
	Given tom1关注jobs的公众号
#会员购买VIP年卡，首次充值100元，会员钱包月100元
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

	When tom访问jobs的webapp
	When tom获取手机绑定验证码'13812345678'
	When tom使用验证码绑定手机
		"""
		{
			"phone": 13812345678
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

	When tom1访问jobs的webapp
	When tom1获取手机绑定验证码'13812345679'
	When tom1使用验证码绑定手机
		"""
		{
			"phone": 13812345679
		}
		"""
	When tom1开通会员卡
		"""
		{
			"pay_type":"微信支付",
			"name": "年卡会员卡",
			"id": "777000003"
		}
		"""

Scenario:1 会员查看我想买列表-无数据
	When bill访问jobs的webapp
	When bill浏览jobs的webapp的会员卡
	Then bill查看我想买全部列表
		"""
		[]
		"""
	Then bill查看我发表的我想买列表
		"""
		[]
		"""
	Then bill查看我支持的我想买列表
		"""
		[]
		"""
Scenario:2 会员查看我想买全部列表和我发表的列表-有数据
	When bill访问jobs的webapp
	When bill浏览jobs的webapp的会员卡
	When bill发表我想买
		"""
		{
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "抱枕",
			"product_source": "天猫",
			"reject_same_other_brands": true,
			"id": "001"
		}
		"""
	When tom访问jobs的webapp
	When tom浏览jobs的webapp的会员卡
	When tom发表我想买
		"""
		{
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "电视机",
			"product_source": "京东",
			"reject_same_other_brands": false,
			"id": "002"
		}
		"""

	When bill访问jobs的webapp
	When bill浏览jobs的webapp的会员卡
	Then bill查看我想买全部列表
		"""
		[{
			"member":"tom",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "电视机",
			"product_source": "京东",
			"reject_same_other_brands": false,
			"progress": "0%",
			"id": "002"
		},{
			"member":"bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "抱枕",
			"product_source": "天猫",
			"reject_same_other_brands": true,
			"progress": "0%",
			"id": "001"
		}]
		"""
	Then bill查看我发表的我想买列表
		"""
		[{
			"member":"bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "抱枕",
			"product_source": "天猫",
			"reject_same_other_brands": true,
			"progress": "0%",
			"id": "001"
		}]
		"""

Scenario:3 会员支持我想买
	When bill访问jobs的webapp
	When bill浏览jobs的webapp的会员卡
	When bill发表我想买
		"""
		{
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "抱枕",
			"product_source": "天猫",
			"reject_same_other_brands": true,
			"id": "001"
		}
		"""
	When tom访问jobs的webapp
	When tom浏览jobs的webapp的会员卡
	When tom支持会员'bill'发表的我想买'001'
		"""
		{
			"description":"我也想买，非常想买！",
			"time":"今天"
		}
		"""
	Then tom查看我支持的我想买列表
		"""
		[{
			"member":"bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "抱枕",
			"product_source": "天猫",
			"reject_same_other_brands": true,
			"progress": "50%",
			"actions":["查看支持"],
			"id": "001"
		}]
		"""
	When bill访问jobs的webapp
	When bill浏览jobs的webapp的会员卡
	Then bill查看我想买全部列表
		"""
		[{
			"member":"bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "抱枕",
			"product_source": "天猫",
			"reject_same_other_brands": true,
			"progress": "50%",
			"actions":["查看支持"],
			"id": "001"
		}]
		"""
	Then bill查看我发表的我想买列表
		"""
		[{
			"member":"bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "抱枕",
			"product_source": "天猫",
			"reject_same_other_brands": true,
			"progress": "50%",
			"actions":["查看支持"],
			"id": "001"
		}]
		"""

	When tom1访问jobs的webapp
	When tom1浏览jobs的webapp的会员卡
	When tom1支持会员'bill'发表的我想买'001'
		"""
		{
			"description":"我也想买，非常想买too！",
			"time":"今天"
		}
		"""
	When tom访问jobs的webapp
	When tom浏览jobs的webapp的会员卡
	Then tom查看我支持的我想买列表
		"""
		[{
			"member":"bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "抱枕",
			"product_source": "天猫",
			"reject_same_other_brands": true,
			"progress": "100%",
			"actions":["查看支持","采购进度"],
			"id": "001"
		}]
		"""

	When bill访问jobs的webapp
	When bill浏览jobs的webapp的会员卡
	Then bill查看我想买全部列表
		"""
		[{
			"member":"bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "抱枕",
			"product_source": "天猫",
			"reject_same_other_brands": true,
			"progress": "100%",
			"actions":["查看支持","采购进度"],
			"id": "001"
		}]
		"""
	Then bill查看我发表的我想买列表
		"""
		[{
			"member":"bill",
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "抱枕",
			"product_source": "天猫",
			"reject_same_other_brands": true,
			"progress": "100%",
			"actions":["查看支持","采购进度"],
			"id": "001"
		}]
		"""

Scenario:4 会员查看采购进度

	When bill访问jobs的webapp
	When bill浏览jobs的webapp的会员卡
	When bill发表我想买
		"""
		{
			"picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']",
			"product_name": "抱枕",
			"product_source": "天猫",
			"reject_same_other_brands": true,
			"id": "001"
		}
		"""
	When tom访问jobs的webapp
	When tom浏览jobs的webapp的会员卡
	When tom支持会员'bill'发表的我想买'001'
		"""
		{
			"description":"我也想买，非常想买！",
			"time":"今天"
		}
		"""
	When tom1访问jobs的webapp
	When tom1浏览jobs的webapp的会员卡
	When tom1支持会员'bill'发表的我想买'001'
		"""
		{
			"description":"我也想买，非常想买too！",
			"time":"今天"
		}
		"""

	When bill访问jobs的webapp
	When bill浏览jobs的webapp的会员卡
	Then bill查看会员'bill'发表的我想买'001'的采购进度
		"""
		{
			"status":"人气达标，采购中",
			"time":"今天"
		}
		"""

	When 采销人员标记会员'bill'发表的我想买'001'状态为'采购完成，等待上架'

	When bill访问jobs的webapp
	When bill浏览jobs的webapp的会员卡
	Then bill查看会员'bill'发表的我想买'001'的采购进度
		"""
		{
			"status":"采购完成，等待上架",
			"time":"今天"
		}
		"""
	When 采销人员标记会员'bill'发表的我想买'001'状态为'商品已上架'

	When bill访问jobs的webapp
	When bill浏览jobs的webapp的会员卡
	Then bill查看会员'bill'发表的我想买'001'的采购进度
		"""
		{
			"status":"上架完成，心愿达成,可以购买啦！",
			"time":"今天"
		}
		"""
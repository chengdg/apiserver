#watcher: zhangsanxiang@weizoom.com,benchi@weizoom.com
#_author_: "张三香" 2016.06.28

Feature:会员绑定微众卡
	"""
		1、会员绑定微众卡有以下2个入口:
			a、编辑订单页点击'使用微众卡'，弹窗中选择'绑定新卡'
			b、个人中心-我的卡包-绑定新卡
		2、输入正确的卡号和密码，弹窗提示'恭喜您 绑定成功'，弹窗按钮-继续绑定和去查看，关闭弹窗的x或点击【继续绑定】，绑定页面清空卡号或密码
		3、输入已过期、未激活、余额为0、其他商家的专属卡、已绑定过的卡时会有校验，不允许绑定
		4、同一张卡，在同一商家只允许同一个人绑定一次
		5、同一张卡，允许多人绑定使用
		6、一个人一天（自然天）只能输错10次，超过10次，今天不能再绑定卡
		7、校验时错误提示语:
			卡号或密码错误！
			该微众卡已经添加！
			该微众卡余额为0！
			微众卡已过期！
			微众卡未激活！
			该专属卡不能在此商家使用！
			已锁定，一人一天最多可输错10次密码
	"""

Background:
	Given 重置'weapp'的bdd环境
	Given 重置'weizoom_card'的bdd环境
	Given 设置jobs为自营平台账号::weapp
	Given jobs登录系统::weapp
	And jobs已添加供货商::weapp
		"""
		[{
			"name": "供货商 a",
			"responsible_person": "张大众",
			"supplier_tel": "15211223344",
			"supplier_address": "北京市海淀区海淀科技大厦",
			"remark": "备注"
		}]
		"""
	And jobs已添加支付方式::weapp
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
	Given jobs已添加商品::weapp
		"""
		[{
			"name":"商品1",
			"product_type":"普通商品",
			"supplier": "供货商a",
			"purchase_price": 9.99,
			"price": 10.00,
			"weight": 1.0,
			"stock_type": "无限",
			"pay_interfaces":
				[{
					"type": "在线支付"
				},{
					"type": "货到付款"
				}],
			"detail":"普通商品1的详情",
			"status":"在售"
		}]
		"""

	#普通商家nokia
	Given nokia登录系统::weapp
	And nokia已添加支付方式::weapp
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
	When nokia开通使用微众卡权限::weapp
	Given nokia已添加商品::weapp
		"""
		[{
			"name":"nokia商品1",
			"price": 10.00
		}]
		"""

	When bill关注jobs的公众号
	When bill关注nokia的公众号
	When tom关注jobs的公众号

	#创建微众卡
	Given test登录管理系统::weizoom_card
	When test新建通用卡::weizoom_card
		"""
		[{
			"name":"10元微众卡",
			"prefix_value":"101",
			"type":"virtual",
			"money":"10.00",
			"num":"3",
			"comments":"微众卡"
		},{
			"name":"20元微众卡",
			"prefix_value":"102",
			"type":"virtual",
			"money":"20.00",
			"num":"1",
			"comments":"微众卡"
		}]
		"""
	When test新建限制卡::weizoom_card
		"""
		[{
			"name":"风暴卡1",
			"prefix_value":"666",
			"type":"property",
			"vip_shop":"nokia",
			"use_limit":{
				"is_limit":"off"
			},
			"money":"50.00",
			"num":"1",
			"comments":""
		}]
		"""
	#微众卡审批出库
	When test下订单::weizoom_card
		"""
		[{
			"card_info":[{
				"name":"10元微众卡",
				"order_num":"3",
				"start_date":"2016-06-16 00:00",
				"end_date":"2026-06-16 00:00"
			}],
			"order_info":{
				"order_id":"0001"
				}
		}]
		"""
	When test下订单::weizoom_card
		"""
		[{
			"card_info":[{
				"name":"20元微众卡",
				"order_num":"1",
				"start_date":"2016-06-16 00:00",
				"end_date":"2016-06-16 00:00"
			}],
			"order_info":{
				"order_id":"0002"
				}
		}]
		"""
	When test下订单::weizoom_card
		"""
		[{
			"card_info":[{
				"name":"风暴卡1",
				"order_num":"1",
				"start_date":"2016-06-16 00:00",
				"end_date":"2019-06-16 00:00"
			}],
			"order_info":{
				"order_id":"0003"
				}
		}]
		"""

	#激活微众卡
	When test批量激活订单'0001'的卡::weizoom_card
	When test批量激活订单'0003'的卡::weizoom_card

@binding_weizoon_card
Scenario:1 微众卡绑定-输入有效的微众卡号和密码
	When bill访问jobs的webapp
	When bill绑定微众卡
		"""
		{
			"binding_date":"2016-06-16",
			"binding_shop":"jobs",
			"weizoom_card_info":
				{
					"id":"101000001",
					"password":"1234567"
				}
		}
		"""
	Then bill获得提示信息'恭喜您 绑定成功'
	When bill绑定微众卡
		"""
		{
			"binding_date":"2016-06-16",
			"binding_shop":"jobs",
			"weizoom_card_info":
				{
					"id":"101000002",
					"password":"1234567"
				}
		}
		"""
	Then bill获得提示信息'恭喜您 绑定成功'
	#同一张卡，可以多人绑定
	When tom访问jobs的webapp
	When tom绑定微众卡
		"""
		{
			"binding_date":"2016-06-16",
			"binding_shop":"jobs",
			"weizoom_card_info":
				{
					"id":"101000001",
					"password":"1234567"
				}
		}
		"""
	Then tom获得提示信息'恭喜您 绑定成功'
	#同一张卡，可以在不同商家绑定
	When bill访问nokia的webapp
	When bill绑定微众卡
		"""
		{
			"binding_date":"2016-06-16",
			"binding_shop":"nokia",
			"weizoom_card_info":
				{
					"id":"101000001",
					"password":"1234567"
				}
		}
		"""
	Then bill获得提示信息'恭喜您 绑定成功'

@binding_weizoon_card
Scenario:2 微众卡绑定-输入无效的微众卡号和密码
	#该微众卡余额为0！
		When bill访问nokia的webapp
		When bill购买nokia的商品
			"""
			{
				"pay_type": "微信支付",
				"products":[{
					"name":"nokia商品1",
					"price":10.00,
					"count":1
				}],

				"weizoom_card":[{
					"card_name":"101000001",
					"card_pass":"1234567"
				}]
			}
			"""
		When bill访问jobs的webapp
		When bill绑定微众卡
			"""
			{
				"binding_date":"2016-06-16",
				"binding_shop":"jobs",
				"weizoom_card_info":
					{
						"id":"101000001",
						"password":"1234567"
					}
			}
			"""
		Then bill获得提示信息'该微众卡余额为0！'
	#该微众卡已经添加！
		When bill访问jobs的webapp
		When bill绑定微众卡
			"""
			{
				"binding_date":"2016-06-16",
				"binding_shop":"jobs",
				"weizoom_card_info":
					{
						"id":"101000002",
						"password":"1234567"
					}
			}
			"""
		When bill绑定微众卡
			"""
			{
				"binding_date":"2016-06-16",
				"binding_shop":"jobs",
				"weizoom_card_info":
					{
						"id":"101000002",
						"password":"1234567"
					}
			}
			"""
		Then bill获得提示信息'该微众卡已经添加！'
	#微众卡未激活！
		Given test登录管理系统::weizoom_card
		When test停用卡号'101000003'的卡::weizoom_card
		When bill访问jobs的webapp
		When bill绑定微众卡
			"""
			{
				"binding_date":"2016-06-16",
				"binding_shop":"jobs",
				"weizoom_card_info":
					{
						"id":"101000003",
						"password":"1234567"
					}
			}
			"""
		Then bill获得提示信息'微众卡未激活！'
	#微众卡已过期！
		When bill访问jobs的webapp
		When bill绑定微众卡
			"""
			{
				"binding_date":"2016-06-16",
				"binding_shop":"jobs",
				"weizoom_card_info":
					{
						"id":"102000001",
						"password":"1234567"
					}
			}
			"""
		Then bill获得提示信息'微众卡已过期！'
	#该专属卡不能在此商家使用！
		When bill访问jobs的webapp
		When bill绑定微众卡
			"""
			{
				"binding_date":"2016-06-17",
				"binding_shop":"jobs",
				"weizoom_card_info":
					{
						"id":"666000001",
						"password":"1234567"
					}
			}
			"""
		Then bill获得提示信息'该专属卡不能在此商家使用！'
	#卡号或密码错误！
		When bill访问jobs的webapp
		When bill绑定微众卡
			"""
			{
				"binding_date":"2016-06-17",
				"binding_shop":"jobs",
				"weizoom_card_info":
					{
						"id":"101000001",
						"password":"11"
					}
			}
			"""
		Then bill获得提示信息'卡号或密码错误！'

		When bill访问jobs的webapp
		When bill绑定微众卡
			"""
			{
				"binding_date":"2016-06-17",
				"binding_shop":"jobs",
				"weizoom_card_info":
					{
						"id":"101011",
						"password":"1234567"
					}
			}
			"""
		Then bill获得提示信息'卡号或密码错误！'
#watcher: wangli@weizoom.com,benchi@weizoom.com
#_author_: "王丽" 2016.06.29

Feature:编辑订单页使用微众-微众卡列表
	"""
		1 "使用卡"页签
		会员下单，在编辑订单页选择使用微众卡，弹出"使用卡"页签
			1）使用卡里只会显示当前可使用的卡，不能显示不可以用的卡：余额为0的，已过期，已停用
			2）在次页签中列表展示此会员在此商城下"可使用的"微众卡列表，按照绑定的卡的倒叙排列
			3）每张卡展示卡的基本信息：余额、面值、卡号、卡来源（"商城下单"或"绑定卡"或"返利活动"）
			4）页面顶端展示提示信息"您最多可以使用10张卡"
			5）页面底部显示"应付"（该订单需要用微众卡支付的金额）；"实付"（该订单选择用微众卡支付的金额，实付金额是勾选多张卡的余额累加）；"实付"小于等于"应付"
			6）可以按照任意顺序选择和取消选择使用列表中的微众卡支付订单；
				（1）只要是"应付"大于"实付"，并且已选择的微众卡小于10张，就可以选择微众卡
				（2）当"应付"等于"实付"时，没有选择的微众卡就不能选择了
				（3）当"应付"大于"实付"，并且已选择的微众卡等于10张，没有选择的微众卡就不能选择了
				（4）每次选择和取消选择微众卡，都会按照上面的规则更新"应付"和"实付",控制选择卡的勾选
			7）"确定"和"取消"按钮
				1）"确定"：点击确定，使用选择的微众卡，计算抵扣订单的金额，并且关闭使用微众卡弹窗，将使用金额显示在编辑订单页，"微众抵扣"字段更新
				2）"取消":点击取消，取消此次进入使用卡页签的操作，关闭使用微众卡弹窗，回到编辑订单页
			8）此页面没有卡，显示提示信息"暂无微众卡，请先绑定新卡再使用"和按钮"返回"；没有卡列表上的一切信息；点击"返回"，关闭弹窗，返回"编辑订单"页


		2 "绑定新卡"页签
			1）卡号，密码，输入框；返回，绑定，按钮
			2）文本框里不输入卡号的时候，会显示“请输入卡号”这个文字并且没有后面的X，当光标聚焦到输入框时，还会显示“请输入卡号”这个文字并且没有后面的X，只有当真正输入卡号数字的时候，“请输入卡号”这个文字才会消失并且显示后面的X。点击输入框后面的X，可以清空输入框里的数字。
			3）卡号和密码输入后，点击"绑定"进行校验。校验成功弹出绑定成功的弹窗，校验不成功，显示提示语
				错误提示语：
					卡号或密码错误！
					该微众卡已经添加！
					该微众卡余额为0！
					微众卡已过期！
					微众卡未激活！
					该专属卡不能在此商家使用！
					已锁定，一人一天最多可输错10次密码

				以非上述问题引起的绑定失败提示信息："系统繁忙"

			4）点击"返回"就是关闭弹窗,返回"编辑订单"页
			5）以前满额卡和新会员卡的功能这次开发不用考虑，也不用测试，南京那边后期将会去掉此功能

		3 特殊问题
			1）选择卡后，再回到"编辑订单"页；使用积分或者优惠券抵扣之后，再选择使用卡；
			使用积分或者优惠券抵扣；之前选择的卡依然是选择的，按照选择的卡的顺序，按照订单使用积分或者优惠券使用后的剩余需支付金额重新一次抵扣微众卡金额，金额抵扣完的选择的微众卡的抵扣金额是零；"编辑订单"页使用的微众卡的金额实时变化；使用卡页签是否能选择卡按照上面的统一规则进行控制
	"""

Background:
	Given 重置'weapp'的bdd环境
	Given 重置'weizoom_card'的bdd环境
	Given jobs登录系统::weapp
	When jobs开通使用微众卡权限::weapp
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
		},{
			"type": "微众卡支付",
			"description": "我的微众卡支付",
			"is_active": "启用"
		}]
		"""
	And jobs已添加商品::weapp
		"""
		[{
			"name":"商品1",
			"price": 10.00
		}]
		"""

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

	#激活微众卡
	When test批量激活订单'0001'的卡::weizoom_card

	Given bill关注jobs的公众号

@buy @compileOrder @use_weizoom_card @weizoom_card
Scenario:1 编辑订单页使用微众卡-绑定卡
	#会员在使用微众卡时绑定微众，在使用微众卡列表立即可以看到此卡
		#绑定卡
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
		Then bill获得使用卡微众卡列表
			"""
			[{
				"card_start_date":"2016-06-16 00:00",
				"card_end_date":"2026-06-16 00:00",
				"card_remain_value":10.00,
				"card_total_value":10.00,
				"id":"101000001",
				"binding_date":"2016-06-16",
				"source":"绑定卡"
			}]
			"""

@buy @compileOrder @use_weizoom_card @weizoom_card
Scenario:2 使用卡列表
	#按照微众卡的绑定顺序的倒叙排列
	#不显示，不可用的卡（已过期、已用完、已冻结）

	#不绑定微众卡，使用卡列表为空
	When bill访问jobs的webapp
	Then bill获得使用卡微众卡列表
		"""
		[]
		"""

	#绑定微众，按照绑定顺序倒序显示
		#绑定卡：101000001
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
		Then bill获得使用卡微众卡列表
			"""
			[{
				"card_start_date":"2016-06-16 00:00",
				"card_end_date":"2026-06-16 00:00",
				"card_remain_value":10.00,
				"card_total_value":10.00,
				"id":"101000002",
				"binding_date":"2016-06-16",
				"source":"绑定卡"
			}]
			"""

		#绑定卡：101000002
		When bill访问jobs的webapp
		When bill绑定微众卡
			"""
			{
				"binding_date":"2016-06-17",
				"binding_shop":"jobs",
				"weizoom_card_info":
					{
						"id":"101000002",
						"password":"1234567"
					}
			}
			"""
		Then bill获得提示信息'恭喜您 绑定成功'
		Then bill获得使用卡微众卡列表
			"""
			[{
				"card_start_date":"2016-06-17 00:00",
				"card_end_date":"2026-06-16 00:00",
				"card_remain_value":10.00,
				"card_total_value":10.00,
				"id":"101000002",
				"binding_date":"2016-06-17",
				"source":"绑定卡"
			},{
				"card_start_date":"2016-06-16 00:00",
				"card_end_date":"2026-06-16 00:00",
				"card_remain_value":10.00,
				"card_total_value":10.00,
				"id":"101000001",
				"binding_date":"2016-06-16",
				"source":"绑定卡"
			}]
			"""

		#绑定卡：101000003
		When bill访问jobs的webapp
		When bill绑定微众卡
			"""
			{
				"binding_date":"2016-06-18",
				"binding_shop":"jobs",
				"weizoom_card_info":
					{
						"id":"101000003",
						"password":"1234567"
					}
			}
			"""
		Then bill获得提示信息'恭喜您 绑定成功'
		Then bill获得使用卡微众卡列表
			"""
			[{
				"card_start_date":"2016-06-16 00:00",
				"card_end_date":"2026-06-16 00:00",
				"card_remain_value":10.00,
				"card_total_value":10.00,
				"id":"101000003",
				"binding_date":"2016-06-18",
				"source":"绑定卡"
			},{
				"card_start_date":"2016-06-16 00:00",
				"card_end_date":"2026-06-16 00:00",
				"card_remain_value":10.00,
				"card_total_value":10.00,
				"id":"101000002",
				"binding_date":"2016-06-17",
				"source":"绑定卡"
			},{
				"card_start_date":"2016-06-16 00:00",
				"card_end_date":"2026-06-16 00:00",
				"card_remain_value":10.00,
				"card_total_value":10.00,
				"id":"101000001",
				"binding_date":"2016-06-16",
				"source":"绑定卡"
			}]
			"""

		#已用完微众卡不显示
		When bill访问jobs的webapp
		When bill购买jobs的商品
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
		Then bill获得使用卡微众卡列表
			"""
			[{
				"card_start_date":"2016-06-16 00:00",
				"card_end_date":"2026-06-16 00:00",
				"card_remain_value":10.00,
				"card_total_value":10.00,
				"id":"101000003",
				"binding_date":"2016-06-18",
				"source":"绑定卡"
			},{
				"card_start_date":"2016-06-16 00:00",
				"card_end_date":"2026-06-16 00:00",
				"card_remain_value":10.00,
				"card_total_value":10.00,
				"id":"101000002",
				"binding_date":"2016-06-17",
				"source":"绑定卡"
			}]
			"""

		#已冻结的微众卡不显示
		Given test登录管理系统::weizoom_card
		When test停用卡号'101000003'的卡

		When bill访问jobs的webapp
		Then bill获得使用卡微众卡列表
			"""
			[{
				"card_start_date":"2016-06-16 00:00",
				"card_end_date":"2026-06-16 00:00",
				"card_remain_value":10.00,
				"card_total_value":10.00,
				"id":"101000002",
				"binding_date":"2016-06-17",
				"source":"绑定卡"
			}]
			"""

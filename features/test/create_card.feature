#_author_:许韦 2016.04.06

Feature:创建微众卡
"""
	微众卡管理员账号在系统中创建微众卡
	1.创建通用卡
		【卡名称】：非必填项，如果不填写，卡名称以"面值+元卡"命名，卡名称不可以重复，0-20个字符
		【卡类型】：实体卡和电子卡选项
		【面值】：大于0的正整数
		【数量】：大于0的正整数
		【备注】：非必填项，最多可输入XX个字符
	2.创建限制卡
		【卡名称】：必填项，1-20个字符
		【卡类型】：条件卡和专属卡选项
		【使用限制】：分为不限制使用和限额使用
		【面值】：大于0的正整数
		【数量】：大于0的正整数
		【备注】：非必填项，最多可输入XX个字符
"""

@weizoom_card @create_card @cl @ztqb
Scenario:1.新建通用卡-通用卡
	Given test登录管理系统:weizoom_card
	When test新建通用卡:weizoom_card
		"""
		[{
			"name":"",
			"prefix_value":"999",
			"type":"entity",
			"money":"10.00",
			"num":"5",
			"comments":""
		},{
			"name":"微众卡",
			"prefix_value":"888",
			"type":"virtual",
			"money":"10.00",
			"num":"10",
			"comments":"微众卡"
		}]
		"""
	Then test能获得通用卡规则列表:weizoom_card
		"""
		[{
			"name":"微众卡",
			"money":"10.00",
			"num":"10",
			"stock":"10",
			"type":"电子卡",
			"card_range":"888000001-888000010",
			"comments":"微众卡"
		},{
			"name":"10元卡",
			"money":"10.00",
			"num":"5",
			"stock":"5",
			"type":"实体卡",
			"card_range":"999000001-999000005",
			"comments":""
		}]
		"""
#	Then test能获得通用卡'微众卡'的库存列表:weizoom_card
#		| card_number |status| money |rest_money|comments|apply_person|apply_department|
#		|  888000001  |待出库| 10.00 |  10.00   |        |            |                |
#		|  888000002  |待出库| 10.00 |  10.00   |        |            |                |
#		|  888000003  |待出库| 10.00 |  10.00   |        |            |                |
#		|  888000004  |待出库| 10.00 |  10.00   |        |            |                |
#		|  888000005  |待出库| 10.00 |  10.00   |        |            |                |
#		|  888000006  |待出库| 10.00 |  10.00   |        |            |                |
#		|  888000007  |待出库| 10.00 |  10.00   |        |            |                |
#		|  888000008  |待出库| 10.00 |  10.00   |        |            |                |
#		|  888000009  |待出库| 10.00 |  10.00   |        |            |                |
#		|  888000010  |待出库| 10.00 |  10.00   |        |            |                |
#
#	Then test能获得通用卡'10元卡'的库存列表:weizoom_card
#		| card_number |status| money |rest_money|comments|apply_person|apply_department|
#		|  999000001  |待出库| 10.00 |  10.00   |        |            |                |
#		|  999000002  |待出库| 10.00 |  10.00   |        |            |                |
#		|  999000003  |待出库| 10.00 |  10.00   |        |            |                |
#		|  999000004  |待出库| 10.00 |  10.00   |        |            |                |
#		|  999000005  |待出库| 10.00 |  10.00   |        |            |                |



@weizoom_card @create_card @cl
Scenario:2.新建微众卡-限制卡
	Given test登录管理系统
	When test新建限制卡
		"""
		[{
			"name":"测试卡1",
			"prefix_value":"777",
			"type":"condition",
			"use_limit":{
				"is_limit":"off"
			},
			"money":"10.00",
			"num":"2",
			"comments":""
		},{
			"name":"测试卡2",
			"prefix_value":"666",
			"type":"condition",
			"use_limit":{
				"is_limit":"on",
				"limit_money":"50.00"
			},
			"money":"10.00",
			"num":"1",
			"comments":"weizoom"
		},{
			"name":"测试卡3",
			"prefix_value":"555",
			"type":"property",
			"vip_shop":"jobs",
			"new_member":"on",
			"use_limit":{
				"is_limit":"off"
			},
			"money":"10.00",
			"num":"2",
			"comments":""
		},{
			"name":"测试卡4",
			"prefix_value":"444",
			"type":"property",
			"vip_shop":"jobs",
			"new_member":"off",
			"use_limit":{
				"is_limit":"on",
				"limit_money":"100.00"
			},
			"money":"25.00",
			"num":"1",
			"comments":"专属卡"
		}]
		"""
	Then test能获得限制卡规则列表
		"""
		[{
			"name":"测试卡4",
			"money":"25.00",
			"num":"1",
			"stock":"1",
			"type":"专属卡",
			"is_limit":"满100使用",
			"vip_shop":"jobs",
			"new_member":"",
			"card_range":"444000001-444000001",
			"comments":"专属卡"
		},{
			"name":"测试卡3",
			"money":"10.00",
			"num":"2",
			"stock":"2",
			"type":"专属卡",
			"is_limit":"不限制",
			"vip_shop":"jobs",
			"new_member":"新会员",
			"card_range":"555000001-555000002",
			"comments":""
		},{
			"name":"测试卡2",
			"money":"10.00",
			"num":"1",
			"stock":"1",
			"type":"条件卡",
			"is_limit":"满50使用",
			"vip_shop":"",
			"new_member":"",
			"card_range":"666000001-666000001",
			"comments":"weizoom"
		},{
			"name":"测试卡1",
			"money":"10.00",
			"num":"2",
			"stock":"2",
			"type":"条件卡",
			"is_limit":"不限制",
			"vip_shop":"",
			"new_member":"",
			"card_range":"777000001-777000002",
			"comments":""
		}]
		"""
	Then test能获得限制卡'测试卡4'的库存列表
		|  card_number | status| money |rest_money|comments|apply_person|apply_department|
		|   444000001  | 待出库| 25.00 |  25.00   |        |            |                |

	Then test能获得限制卡'测试卡3'的库存列表
		| card_number | status| money |rest_money|comments|apply_person|apply_department|
		|  555000001  | 待出库| 10.00 |  10.00   |        |            |                |
		|  555000002  | 待出库| 10.00 |  10.00   |        |            |                |

	Then test能获得限制卡'测试卡2'的库存列表
		| card_number | status| money |rest_money|comments|apply_person|apply_department|
		|  666000001  | 待出库| 10.00 |  10.00   |        |            |                |

	Then test能获得限制卡'测试卡1'的库存列表
		| card_number | status| money |rest_money|comments|apply_person|apply_department|
		|  777000001  | 待出库| 10.00 |  10.00   |        |            |                |
		|  777000002  | 待出库| 10.00 |  10.00   |        |            |                |

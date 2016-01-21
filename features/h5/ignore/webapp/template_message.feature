#author: 王丽 2015-12-24
#说明：天琦说暂时无法实现，于2016.01.19移除到ignore文件夹下

Feature:模板消息
	jobs设定开启模板消息，用户满足相应的模板消息的条件，可以收到相应的消息

Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp

	And jobs已有模板消息:weapp
		"""
		[{
			"template_id":"",
			"headline":"TM00398-付款成功通知",
			"industry":"IT科技",
			"type":"主营行业",
			"status":"未启用",
			"operate":"查看"
		}]
		"""
	When jobs给'主营行业'行业标题为'TM00398-付款成功通知'的模板消息添加内容
		"""
		{
			"template_id":"_k8QP2Fs_nZBiR52e_Y1040m5zi30i3E28khSHz8QtY",
			"first":"我们已收到您的货款，开始为您打包商品，请耐心等待: )",
			"remark":"如有问题咨询微众客服，微众将第一时间为您服务！"
		}
		"""

	When jobs修改'主营行业'行业标题为'TM00398-付款成功通知'的状态
		"""
		{
			"template_id":"_k8QP2Fs_nZBiR52e_Y1040m5zi30i3E28khSHz8QtY",
			"headline":"我们已收到您的货款，开始为您打包商品，请耐心等待: )",
			"industry":"IT科技",
			"type":"主营行业",
			"status":"已启用",
			"operate":"查看"
		}
		"""

	And jobs已添加商品:weapp
		"""
		[{
			"name": "商品1",
			"price": 100.00
		}]
		"""
	And jobs已添加支付方式:weapp
		"""
		[{
			"type": "微信支付",
			"is_active": "启用"
		}, {
			"type": "货到付款",
			"is_active": "启用"
		}]
		"""

	And bill关注jobs的公众号
	And tom关注jobs的公众号

@message @templateMessage
Scenario:1 启用模板消息，配置正确的模板ID，可以成功接收到消息
	When bill访问jobs的webapp
	#购买商品，支付成功模板消息
	When bill购买jobs的商品
		"""
		{
			"order_id":"0000001",
			"ship_name": "tom",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "微信支付",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	When bill使用支付方式'微信支付'进行支付
		"""
		{
			"is_sync": true
		}
		"""
	Then bill支付订单成功
		"""
		{
			"status": "待发货",
			"final_price": 100.0,
			"products": [{
				"name": "商品1",
				"price": 100.0,
				"count": 1
			}]
		}
		"""

	Then server能发送模板消息
		"""
		{
			"touser":"bill_jobs",
			"first":"我们已收到您的货款，开始为您打包商品，请耐心等待: )",
			"remark":"如有问题咨询微众客服，微众将第一时间为您服务！",
			"orderProductPrice":"￥100.0 [实际付款]",
			"orderProductName":"商品1",
			"orderAddress":"泰兴大厦"
		}
		"""

#	Then bill收到模板消息
#		"""
#		付款成功通知<br />我们已收到您的货款，开始为您打包商品，请耐心等待: )<br />
#		订单金额：￥100.0[实际付款]<br />
#		商品详情：商品1<br />
#		收货信息：泰兴大厦<br />
#		订单编号：0000001
#		如有问题咨询微众客服，微众将第一时间为您服务！<br />
#		"""
#
#	#购买者才能收到相应的消息
#	Then tom收到模板消息
#		"""
#		"""

@message @templateMessage
Scenario:2 未启用模板消息，配置正确的模板ID，不可以成功接收到消息
	Given jobs登录系统:weapp
	When jobs修改'IT科技'行业标题为'付款成功通知'的状态
		"""
		{
			"title":"TM00398-付款成功通知",
			"template_id":"_k8QP2Fs_nZBiR52e_Y1040m5zi30i3E28khSHz8QtY",
			"headline":"我们已收到您的货款，开始为您打包商品，请耐心等待: )",
			"ending":"如有问题咨询微众客服，微众将第一时间为您服务！",
			"industry":"IT科技",
			"type":"主营行业",
			"status":"未启用"
		}
		"""
	When bill访问jobs的webapp
	#购买商品，支付成功模板消息
	When bill购买jobs的商品
		"""
		{
			"order_id":"0000001",
			"ship_name": "tom",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "微信支付",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	When bill使用支付方式'微信支付'进行支付
		"""
		{
			"is_sync": true
		}
		"""
	Then bill支付订单成功
		"""
		{
			"status": "待发货",
			"final_price": 100.0,
			"products": [{
				"name": "商品1",
				"price": 100.0,
				"count": 1
			}]
		}
		"""
	Then server能发送模板消息
		"""
		{}
		"""

#	Then bill收到模板消息
#		"""
#		"""

@message @templateMessage
Scenario:3 启用模板消息，配置错误的模板ID，不可以成功接收到消息
	Given jobs登录系统:weapp
	When jobs给'IT科技'行业标题为'付款成功通知'的模板消息添加内容
		"""
		{
			"template_id":"12334556",
			"headline":"我们已收到您的货款，开始为您打包商品，请耐心等待: )",
			"ending":"如有问题咨询微众客服，微众将第一时间为您服务！",
		}
		"""
	When bill访问jobs的webapp
	#购买商品，支付成功模板消息
	When bill购买jobs的商品
		"""
		{
			"order_id":"0000001",
			"ship_name": "tom",
			"ship_tel": "13811223344",
			"ship_area": "北京市 北京市 海淀区",
			"ship_address": "泰兴大厦",
			"pay_type": "微信支付",
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	When bill使用支付方式'微信支付'进行支付
		"""
		{
			"is_sync": true
		}
		"""
	Then bill支付订单成功
		"""
		{
			"status": "待发货",
			"final_price": 100.0,
			"products": [{
				"name": "商品1",
				"price": 100.0,
				"count": 1
			}]
		}
		"""
	Then server能发送模板消息
		"""
		{}
		"""

#	Then bill收到模板消息
#		"""
#		"""

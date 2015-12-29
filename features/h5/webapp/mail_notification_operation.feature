#author: 王丽 2015-12-24

Feature:运营邮件通知
	jobs设定开启运营邮件通知，用户订单满足相应的条件，配置的运营邮箱可以收到相应的邮件通知

Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
	And jobs已添加支付方式:weapp
		"""
		[{
			"type": "货到付款"
		}, {
			"type": "微信支付"
		}]
		"""
	And jobs已添加商品:weapp
		"""
		[{
			"name": "商品1",
			"price":100.0
		}]
		"""
	And jobs初始化邮件通知:weapp
	Given bill关注jobs的公众号


Scenario:1 启用"下订单时"邮件通知
	Given jobs登录系统:weapp
	When jobs配置'下单时'邮件通知:weapp
		"""
		{
			"emails":"925896183@qq.com",
			"member_ids":""
		}
		"""
	When jobs启用'下单时'邮件通知:weapp

	#购买商品，成功下单
	When bill访问jobs的webapp
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
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 100.0,
			"product_price": 100.00,
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
#	Then server能发送邮件
#	"""
#	商品名称：商品1<br> 订单号：0000001<br> 下单时间：2015-12-25 15:11<br> 订单状态：<font color="red">待支付</font><br> 订购数量：1<br> 支付金额：100.0<br> 收货人：tom<br> 收货人电话：13811223344<br> 收货人地址： 泰兴大厦
#	"""
#	Then 邮箱'ceshi@weizoom.com'获得'下单时'运营邮件通知
#		"""
#		商品名称：热干面<br />
#		订单号：20151224161321569<br />
#		下单时间：2015-12-24 16:13<br />
#		订单状态：待支付<br />
#		订购数量：1<br />
#		支付金额：1.5<br />
#		收货人：bill<br />
#		收货人电话：13811223344<br />
#		收货人地址： 泰兴大厦<br />
#		"""

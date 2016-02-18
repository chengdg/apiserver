#_author_: 张三香 2016.02.18

Feature:在apiserver中进行微信支付和支付宝支付的校验

Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
	And jobs已添加商品:weapp
		"""
		[{
			"name":"商品1",
			"price":100.0
		},{
			"name":"商品2",
			"price":200.0,
			"postage":10.0
		}]
		"""
	When bill关注jobs的公众号

@pay
Scenario:1 选择使用支付方式:微信支付v2
	Given jobs登录系统:weapp
	When jobs添加支付方式:weapp
		"""
		[{
			"type": "微信支付",
			"is_active": "启用",
			"version": "v2",
			"weixin_appid": "12345",
			"weixin_partner_id": "22345",
			"weixin_partner_key": "32345",
			"weixin_sign": "42345"
		}]
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"001",
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
			"final_price": 100.0
		}
		"""
	Then server能获取wxpay_interface接口信息
		"""
		{
			"final_price":100.0,
			"is_status_not":true,
			"order_id":"001",
			"pay_interface_type":"微信支付",
			"pay_version":"v2",
			"app_id":"12345"
		}
		"""
	Then server能获取wxpay_package接口信息
		"""
		{
			"total_fee":10000,
			"product_names":"商品1",
			"partner_id":"22345",
			"partner_key":"32345",
			"paysign_key":"42345",
			"app_id":"12345"
		}
		"""

@pay
Scenario:2 选择使用支付方式:微信支付v3
	Given jobs登录系统:weapp
	When jobs添加支付方式:weapp
		"""
		{
			"type": "微信支付",
			"version": "v3",
			"weixin_appid": "123450",
			"mch_id": "323450",
			"api_key": "423450"
		}
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"002",
			"pay_type": "微信支付",
			"products": [{
				"name": "商品1",
				"count": 1
			},{
				"name": "商品2",
				"count": 1
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price":310.0,
			"postage":10.0,
			"products": [{
				"name": "商品1",
				"price": 100.0,
				"count": 1
			},{
				"name": "商品2",
				"price": 200.0,
				"count": 1
			}]
		}
		"""
	Then server能获取wxpay_interface接口信息
		"""
		{
			"final_price":310.0,
			"is_status_not":true,
			"order_id":"002",
			"pay_interface_type":"微信支付",
			"pay_version":"v3",
			"app_id":"123450"
		}
		"""
	Then server能获取wxpay_package接口信息
		"""
		{
			"total_fee":31000,
			"product_names":"商品1,商品2",
			"app_id":"123450",
			"mch_id":"323450"
		}
		"""

@pay
Scenario:3 选择使用支付方式:支付宝
	Given jobs登录系统:weapp
	When jobs添加支付方式:weapp
		"""
		[{
			"type": "支付宝",
			"is_active": "启用",
			"partner": "11",
			"key": "21",
			"ali_public_key": "31",
			"private_key": "41",
			"seller_email": "a@a.com"
		}]
		"""
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"order_id":"003",
			"pay_type": "支付宝",
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
			"final_price": 100.0
		}
		"""
	Then server能获取alipay_interface接口信息
		"""
		{
			"final_price":100.0,
			"is_status_not":true,
			"order_id":"003",
			"partner":"11",
			"key":"21",
			"ali_public_key":"31",
			"private_key":"41",
			"input_charset":"utf-8",
			"sign_type":"MD5",
			"seller_email": "a@a.com"
		}
		"""
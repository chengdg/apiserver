#author: 王丽 
#editor: 张三香 2015.10.16
#editor: 王丽 2016.01.05

Feature: 会员列表-会员详情-传播能力
	"""
		会员分享链接和推广扫码带来的访问量和新增会员数的记录
		1、【二维码引流会员数量】：本会员通过"推广扫码"带来的新增会员数
		2、【分享链接引流会员数量】：本会员通过"分享链接"带来的新增会员数
		3、分享链接明细列表
			【分享链接】：分享链接的页面名称或者活动名称
			【点击】：点击此链接数（包含会员和非会员的点击数），同意人只计算一次
			【关注转化】：通过此链接带来的新增会员数
			【购买转化】：通过此链接带来的付款订单数（订单状态为：待发货、已发货、已完成、退款中、退款成功）
				备注：只能是购买分享的链接的商品
	"""

Background:
	Given 重置weapp的bdd环境

@mall2 @member @memberList @mall3 @bert @aav
Scenario:1 会员详情-传播能力(分享链接引流)
	Given jobs登录系统:weapp
	And 开启手动清除cookie模式:weapp

	#添加相关基础数据
		When jobs已添加商品:weapp
			"""
			[{
				"name": "商品1",
				"postage":10,
				"price":100
			}, {
				"name": "商品2",
				"postage":15,
				"price":100
			}]
			"""
		And jobs已添加支付方式:weapp
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

	#tom带来的传播能力数据创建

	#1 bill点击分享链接，关注公众号，购买商品
		#bill和tom建立好友关系
		When tom关注jobs的公众号
		When tom访问jobs的webapp
		When tom把jobs的商品"商品1"的链接分享到朋友圈

		When 清空浏览器:weapp
		When bill点击tom分享链接
		When bill关注jobs的公众号
		When bill访问jobs的webapp

		#bill通过tom分享的商品链接下单购买jobs的商品1
		#待支付
			When bill点击tom分享链接
			And bill购买jobs的商品
				"""
				{
					"order_id": "001",
					"products": [{
						"name": "商品1",
						"count": 1
					}],
					"pay_type": "微信支付"
				}
				"""
		#已取消
			#bill手机端取消订单
			When bill点击tom分享链接
			And bill购买jobs的商品
				"""
				{
					"order_id": "002",
					"products": [{
						"name": "商品1",
						"count": 1
					}],
					"pay_type": "微信支付"
				}
				"""
			And bill取消订单'002'

			#jobs后台取消订单
			When bill点击tom分享链接
			And bill购买jobs的商品
				"""
				{
					"order_id": "003",
					"products": [{
						"name": "商品1",
						"count": 1
					}],
					"pay_type": "微信支付"
				}
				"""
			Given jobs登录系统:weapp
			When jobs'取消'订单'003':weapp
		#待发货
			When bill点击tom分享链接
			And bill购买jobs的商品
				"""
				{
					"order_id": "004",
					"products": [{
						"name": "商品1",
						"count": 1
					}],
					"pay_type": "微信支付"
				}
				"""
			When 清空浏览器:weapp
			Given jobs登录系统:weapp
			When jobs'支付'订单'004':weapp
		#已发货
			When 清空浏览器:weapp
			When bill点击tom分享链接
			And bill购买jobs的商品
				"""
				{
					"order_id": "005",
					"products": [{
						"name": "商品1",
						"count": 1
					}],
					"pay_type": "微信支付"
				}
				"""
			And bill使用支付方式'微信支付'进行支付
			Given jobs登录系统:weapp
			When jobs对订单进行发货:weapp
				"""
				{
					"order_no":"005",
					"logistics":"顺丰速运",
					"number":"123456789"
				}
				"""
		#退款中
			When 清空浏览器:weapp
			When bill点击tom分享链接
			And bill购买jobs的商品
				"""
				{
					"order_id": "006",
					"products": [{
						"name": "商品1",
						"count": 1
					}],
					"pay_type": "微信支付"
				}
				"""
			And bill使用支付方式'微信支付'进行支付
			Given jobs登录系统:weapp
			When jobs'申请退款'订单'006':weapp
		#退款成功
			When 清空浏览器:weapp
			When bill点击tom分享链接
			And bill购买jobs的商品
				"""
				{
					"order_id": "007",
					"products": [{
						"name": "商品1",
						"count": 1
					}],
					"pay_type": "微信支付"
				}
				"""
			And bill使用支付方式'微信支付'进行支付
			Given jobs登录系统:weapp
			When jobs'申请退款'订单'007':weapp
			And jobs通过财务审核'退款成功'订单'007':weapp
		#已完成
			#bill完成订单
			When bill点击tom分享链接
			And bill购买jobs的商品
				"""
				{
					"order_id": "008",
					"products": [{
						"name": "商品1",
						"count": 1
					}],
					"pay_type": "微信支付"
				}
				"""
			And bill使用支付方式'微信支付'进行支付
			Given jobs登录系统:weapp
			When jobs对订单进行发货:weapp
				"""
				{
					"order_no": "008",
					"logistics": "off",
					"shipper": ""
				}
				"""
			When bill确认收货订单'008'

			#jobs后台完成订单
			When 清空浏览器:weapp
			When bill点击tom分享链接
			And bill购买jobs的商品
				"""
				{
					"order_id": "009",
					"products": [{
						"name": "商品1",
						"count": 1
					}],
					"pay_type": "微信支付"
				}
				"""
			When bill使用支付方式'微信支付'进行支付
			Given jobs登录系统:weapp
			When jobs对订单进行发货:weapp
				"""
				{
					"order_no": "009",
					"logistics": "off",
					"shipper": ""
				}
				"""
			When jobs'完成'订单'009':weapp

	#2 bill2关注公众号，点击分享链接，购买商品
		
		When bill2关注jobs的公众号
		When bill2访问jobs的webapp

		#bill2和tom建立好友关系，点击tom分享链接
		When tom访问jobs的webapp
		When tom把jobs的商品"商品1"的链接分享到朋友圈

		#同一用户多次点击同一分享链接，"点击次数"累计
		When 清空浏览器:weapp
		When bill2点击tom分享链接
		When bill2点击tom分享链接

		#bill2通过tom分享的商品链接下单购买jobs的商品1
		#已完成
			When bill2点击tom分享链接
			And bill2购买jobs的商品
				"""
				{
					"order_id": "0010",
					"products": [{
						"name": "商品1",
						"count": 1
					}],
					"pay_type": "微信支付"
				}
				"""
			And bill2使用支付方式'微信支付'进行支付
			Given jobs登录系统:weapp
			When jobs对订单进行发货:weapp
				"""
				{
					"order_no": "0010",
					"logistics": "off",
					"shipper": ""
				}
				"""
			And bill确认收货订单'0010'

	#3 tom分享链接，没有人点击
		When tom访问jobs的webapp
		When tom把jobs的商品"商品2"的链接分享到朋友圈

	#校验tom的传播能力
		When 清空浏览器:weapp
		Given jobs登录系统:weapp
		Then jobs获得'tom'的传播能力:weapp
			"""
			{
				"scan_qrcode_new_member": 0,
				"share_link_new_member":1,
				"share_detailed_data":[{
						"click_number":2,
						"new_member":1,
						"order":3
					},{
						"click_number":0,
						"new_member":0,
						"order":0
					}]
			}
			"""

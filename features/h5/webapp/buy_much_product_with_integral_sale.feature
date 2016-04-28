# watcher: fengxuejing@weizoom.com,benchi@weizoom.com
# __author__ : "冯雪静"

Feature: 在webapp中购买参与积分应用活动的商品（多个商品参加一个活动）
	"""
	多商品参加积分活动
		1.购买“多商品积分活动”的一个商品，积分金额小于最大折扣
		2.购买“多商品积分活动”的一个商品，积分金额大于最大折扣
		3.购买“多商品积分活动”的多个商品，积分大于最大折扣
		4.修改“多商品积分活动”关联的部分商品后，商品金额比设置的最高抵扣金额小，进行购买，积分不抵扣运费
		5.下架“多商品积分活动”关联的部分商品后，购买其他参加活动的商品
		6.删除“多商品积分活动”关联的部分商品后，购买其他参加活动的商品
		7.修改“多商品积分活动”关联的部分商品后，商品金额比设置的最高抵扣金额小，和普通商品进行购买，积分不抵其他商品金额
		8.后台管理员可以查看积分订单详情页
	"""


Background:
	Given 重置weapp的bdd环境
	Given jobs登录系统:weapp
	And jobs已添加商品规格:weapp
		"""
		[{
			"name": "尺寸",
			"type": "文字",
			"values": [{
				"name": "M"
			}, {
				"name": "S"
			}]
		}]
		"""
	And jobs已添加商品:weapp
		"""
		[{
			"name": "商品1",
			"model": {
				"models": {
					"standard": {
						"price": 100.00,
						"stock_type": "有限",
						"stocks": 2
					}
				}
			}
		}, {
			"name": "商品2",
			"price": 200.00
		}, {
			"name": "商品3",
			"price": 50.00
		}, {
			"name": "商品5",
			"is_enable_model": "启用规格",
			"model": {
				"models":{
					"M": {
						"price": 40.00,
						"stock_type": "无限"
					},
					"S": {
						"price": 10.00,
						"stock_type": "无限"
					}
				}
			}
		}, {
			"name": "商品6",
			"price": 200.00
		}, {
			"name": "商品7",
			"price": 50.00
		}]
		"""
	Given jobs设定会员积分策略:weapp
		"""
		{
			"integral_each_yuan": 2
		}
		"""
	#支付方式
	Given jobs已添加支付方式:weapp
		"""
		[{
			"type": "微信支付",
			"is_active": "启用"
		}, {
			"type": "货到付款",
			"is_active": "启用"
		}]
		"""
	When jobs创建积分应用活动:weapp
		"""
		[{
			"name": "多商品积分应用1",
			"start_date": "今天",
			"end_date": "1天后",
			"product_name": "商品1,商品2,商品3",
			"is_permanant_active": false,
			"rules": [{
				"member_grade": "全部",
				"discount": 80,
				"discount_money": 40.00
			}]
		}, {
			"name": "多商品积分应用2",
			"start_date": "今天",
			"end_date": "2天后",
			"product_name": "商品5,商品6",
			"is_permanant_active": true,
			"rules": [{
				"member_grade": "全部",
				"discount": 50,
				"discount_money": 5.00
			}]
		}]
		"""
	Given bill关注jobs的公众号:weapp

@mall3 @ztq
Scenario: 1 购买单个积分折扣商品，积分金额小于最大折扣金额

	When bill访问jobs的webapp
	When bill获得jobs的50会员积分
	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品1",
				"count": 1,
				"integral": 50,
				"integral_money": 25.00
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 75.00,
			"product_price": 100.00,
			"postage": 0.00,
			"integral_money":25.00,
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	Then bill在jobs的webapp中拥有0会员积分
	Given jobs登录系统:weapp
	Then jobs可以获得最新订单详情:weapp
		"""
		{
			"status": "待支付",
			"actions": ["支付", "修改价格", "取消订单"],
			"final_price": 75.00,
			"product_price": 100.00,
			"postage": 0.00,
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1,
				"integral_count": 50,
				"integral_money":25.00
			}]
		}
		"""

@mall3 @ztq
Scenario: 2 购买单个积分折扣商品，积分金额大于最大折扣金额

	When bill访问jobs的webapp
	When bill获得jobs的100会员积分
	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品5",
				"model": "M",
				"count": 1,
				"integral": 10,
				"integral_money":5.00
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 35.00,
			"product_price": 40.00,
			"postage": 0.00,
			"integral_money": 5.00,
			"products": [{
				"name": "商品5",
				"model": "M",
				"count": 1
			}]
		}
		"""
	Then bill在jobs的webapp中拥有90会员积分
	Given jobs登录系统:weapp
	Then jobs可以获得最新订单详情:weapp
		"""
		{
			"status": "待支付",
			"actions": ["支付", "修改价格", "取消订单"],
			"final_price": 35.00,
			"product_price": 40.00,
			"postage": 0.00,
			"products": [{
				"name": "商品5",
				"model": "M",
				"price": 40.00,
				"count": 1,
				"integral_count": 10,
				"integral_money":5.00
			}]
		}
		"""
@mall3 @ztq
Scenario: 3 购买多个参加积分应用活动的商品

	When bill访问jobs的webapp
	When bill获得jobs的1000会员积分
	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品1",
				"count": 1,
				"integral": 80,
				"integral_money":40.00
			}, {
				"name": "商品2",
				"count": 1,
				"integral": 80,
				"integral_money":40.00
			}, {
				"name": "商品5",
				"count": 1,
				"model": "S",
				"integral": 10,
				"integral_money":5.00
			}, {
				"name": "商品5",
				"count": 1,
				"model": "M",
				"integral": 10,
				"integral_money":5.00
			}, {
				"name": "商品6",
				"count": 1,
				"integral": 10,
				"integral_money":5.00
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 455.00,
			"product_price": 550.00,
			"postage": 0.00,
			"integral_money": 95.00,
			"products": [{
				"name": "商品1",
				"count": 1
			}, {
				"name": "商品2",
				"count": 1
			}, {
				"name": "商品5",
				"count": 1,
				"model": "S"
			}, {
				"name": "商品5",
				"count": 1,
				"model": "M"
			}, {
				"name": "商品6",
				"count": 1
			}]
		}
		"""
	Then bill在jobs的webapp中拥有810会员积分
	Given jobs登录系统:weapp
	Then jobs可以获得最新订单详情:weapp
		"""
		{
			"status": "待支付",
			"actions": ["支付", "修改价格", "取消订单"],
			"final_price": 455.00,
			"product_price": 550.00,
			"postage": 0.00,
			"products": [{
				"name": "商品1",
				"price": 100.00,
				"count": 1,
				"integral_count": 80,
				"integral_money": 40.00
			}, {
				"name": "商品2",
				"price": 200.00,
				"count": 1,
				"integral_count": 80,
				"integral_money":40.00
			}, {
				"name": "商品5",
				"price": 10.00,
				"count": 1,
				"model": "S",
				"integral_count": 10,
				"integral_money":5.00
			}, {
				"name": "商品5",
				"price": 40.00,
				"count": 1,
				"model": "M",
				"integral_count": 10,
				"integral_money":5.00
			}, {
				"name": "商品6",
				"price": 200.00,
				"count": 1,
				"integral_count": 10,
				"integral_money":5.00
			}]
		}
		"""

@mall3 @ztq
Scenario: 4 修改多商品积分活动关联的商品后，购买参加积分活动的商品
	1.修改部分商品价格后，进行购买
	2.下架部分商品后，进行购买
	3.删除部分商品后，进行购买

	Given jobs登录系统:weapp
	When jobs更新商品'商品1':weapp
		"""
		{
			"name": "商品1",
			"model": {
				"models": {
					"standard": {
						"price": 20.00,
						"stock_type": "有限",
						"stocks": 99
					}
				}
			},
			"postage": 10.00
		}
		"""
	When bill访问jobs的webapp
	When bill获得jobs的1000会员积分
	#积分不抵扣运费
	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品1",
				"count": 1,
				"integral": 40,
				"integral_money": 20.00
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 10.00,
			"product_price": 20.00,
			"postage": 10.00,
			"integral_money":20.00,
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	Then bill在jobs的webapp中拥有960会员积分
	Given jobs登录系统:weapp
	Then jobs可以获得最新订单详情:weapp
		"""
		{
			"status": "待支付",
			"actions": ["支付", "修改价格", "取消订单"],
			"final_price": 10.00,
			"product_price": 20.00,
			"postage": 10.00,
			"products": [{
				"name": "商品1",
				"price": 20.00,
				"count": 1,
				"integral_count": 40,
				"integral_money": 20.00
			}]
		}
		"""
	When jobs'下架'商品'商品2':weapp
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品1",
				"count": 1,
				"integral": 40,
				"integral_money": 20.00
			}, {
				"name": "商品3",
				"count": 1,
				"integral": 80,
				"integral_money": 40.00
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 20.00,
			"product_price": 70.00,
			"postage": 10.00,
			"integral_money":60.00,
			"products": [{
				"name": "商品1",
				"count": 1
			}, {
				"name": "商品3",
				"count": 1
			}]
		}
		"""
	Then bill在jobs的webapp中拥有840会员积分
	Given jobs登录系统:weapp
	Then jobs可以获得最新订单详情:weapp
		"""
		{
			"status": "待支付",
			"actions": ["支付", "修改价格", "取消订单"],
			"final_price": 20.00,
			"product_price": 70.00,
			"postage": 10.00,
			"products": [{
				"name": "商品1",
				"price": 20.00,
				"count": 1,
				"integral_count": 40,
				"integral_money": 20.00
			}, {
				"name": "商品3",
				"price": 50.00,
				"count": 1,
				"integral_count": 80,
				"integral_money": 40.00
			}]
		}
		"""
	When jobs'永久删除'商品'商品3':weapp
	When bill访问jobs的webapp
	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品1",
				"count": 1,
				"integral": 40,
				"integral_money": 20.00
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 10.00,
			"product_price": 20.00,
			"postage": 10.00,
			"integral_money":20.00,
			"products": [{
				"name": "商品1",
				"count": 1
			}]
		}
		"""
	Then bill在jobs的webapp中拥有800会员积分
	Given jobs登录系统:weapp
	Then jobs可以获得最新订单详情:weapp
		"""
		{
			"status": "待支付",
			"actions": ["支付", "修改价格", "取消订单"],
			"final_price": 10.00,
			"product_price": 20.00,
			"postage": 10.00,
			"products": [{
				"name": "商品1",
				"price": 20.00,
				"count": 1,
				"integral_count": 40,
				"integral_money": 20.00
			}]
		}
		"""

@mall3 @ztq
Scenario: 5 修改多商品积分活动关联的商品后，购买参加积分活动的商品和普通商品

	Given jobs登录系统:weapp
	When jobs更新商品'商品1':weapp
		"""
		{
			"name": "商品1",
			"model": {
				"models": {
					"standard": {
						"price": 20.00,
						"stock_type": "有限",
						"stocks": 99
					}
				}
			}
		}
		"""
	When bill访问jobs的webapp
	When bill获得jobs的1000会员积分
	#积分不抵扣运费
	When bill购买jobs的商品
		"""
		{
			"pay_type": "微信支付",
			"products": [{
				"name": "商品1",
				"count": 1,
				"integral": 40,
				"integral_money": 20.00
			}, {
				"name": "商品7",
				"count": 1
			}]
		}
		"""
	Then bill成功创建订单
		"""
		{
			"status": "待支付",
			"final_price": 50.00,
			"product_price": 70.00,
			"postage": 0.00,
			"integral_money":20.00,
			"products": [{
				"name": "商品1",
				"count": 1
			}, {
				"name": "商品7",
				"count": 1
			}]
		}
		"""
	Then bill在jobs的webapp中拥有960会员积分
	Given jobs登录系统:weapp
	Then jobs可以获得最新订单详情:weapp
		"""
		{
			"status": "待支付",
			"actions": ["支付", "修改价格", "取消订单"],
			"final_price": 50.00,
			"product_price": 70.00,
			"postage": 0.00,
			"products": [{
				"name": "商品1",
				"price": 20.00,
				"count": 1,
				"integral_count": 40,
				"integral_money": 20.00
			}, {
				"name": "商品7",
				"price": 50.00,
				"count": 1
			}]
		}
		"""

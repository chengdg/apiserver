Feature: 测试bdd server
  """
   测试bdd server
  """

Background:
	Given 重置weapp的bdd环境

@bdd_test @ignore
Scenario:1. 获得weapp的context
  When weapp设置context:weapp
  """
  {
      "ship_name": "bill",
      "ship_tel": "13811223344",
      "ship_area": "北京市 北京市 海淀区",
      "ship_address": "泰兴大厦",
      "pay_type":"微信支付",
      "products": [{
          "name": "商品1",
          "count": 2
      }]
  }
  """
  Then apiserver获得context
  """
  {
      "ship_name": "bill",
      "ship_tel": "13811223344",
      "ship_area": "北京市 北京市 海淀区",
      "ship_address": "泰兴大厦",
      "pay_type":"微信支付",
      "products": [{
          "name": "商品1",
          "count": 2
      }]
  }
  """
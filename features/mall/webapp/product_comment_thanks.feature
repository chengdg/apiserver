# __author__ : "benchi"
#editor 新新 2015.10.20

Feature: bill在webapp中对已到货的商品进行评价
"""
    bill在webapp中对已到货的商品进行评价
    评价完成后会有“感谢评价”页面
    1 如果还有待评价的商品那么该页面有“继续评价”和“返回首页”两个选项
    2 如果没有待评价的页面那么只有“返回首页”的选项
"""

Background:
    Given jobs登录系统
    And jobs已添加商品
        """
        [{
            "name": "商品1",
            "price": 10.00
        }, {
            "name": "商品2",
            "price": 20.00
        }]
        """
    Given bill关注jobs的公众号
    And jobs已有的订单
        """
        [{
            "order_no":"1",
            "member":"bill",
            "type":"普通订单",
            "status":"已完成",
            "sources":"本店",
            "order_price":10.00,
            "payment_price":10.00,
            "freight":0,
            "ship_name":"bill",
            "ship_tel":"13013013011",
            "ship_area":"北京市,北京市,海淀区",
            "ship_address":"泰兴大厦",
            "products":[{
                "name":"商品1",
                "price": 10.00,
                "count": 1
            }]
        },{
            "order_no":"2",
            "member":"bill",
            "type":"普通订单",
            "status":"已完成",
            "sources":"本店",
            "order_price":20.00,
            "payment_price":20.00,
            "freight":0,
            "ship_name":"bill",
            "ship_tel":"13013013011",
            "ship_area":"北京市,北京市,海淀区",
            "ship_address":"泰兴大厦",
            "products":[{
                "name":"商品2",
                "price": 20.00,
                "count": 1
            }]
        }]
        """

    When bill访问jobs的webapp
    Then bill成功获取个人中心的'待评价'列表
        """
        [{
            "order_no": "1",
            "products": [{
                    "product_name": "商品1"
            }]

        },{
            "order_no": "2",
            "products": [{
                    "product_name": "商品2"
            }]
        }]
        """

@mall2 @mall.webapp.comment.cc
Scenario:1 评价完成后会有“感谢评价”页面
    1 如果还有待评价的商品那么该页面有“继续评价”和“返回首页”两个选项
    2 如果没有待评价的页面那么只有“返回首页”的选项

    When bill访问jobs的webapp
    And bill完成订单'1'中'商品1'的评价包括'文字与晒图'
        """
        {
            "product_score": "4",
            "review_detail": "商品1还不错！！！！！",
            "serve_score": "4",
            "deliver_score": "4",
            "process_score": "4",
            "picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']"
        }
        """
    Then bill成功获取商品评价后'感谢评价'页面
        """
        [{
            "title1":"继续评价",
            "title2":"返回首页"
        }]
        """

    Then bill成功获取个人中心的'待评价'列表
        """
        [{
            "order_no": "2",
            "products": [{
                    "product_name": "商品2"
            }]
        }]
        """
    When bill完成订单'2'中'商品2'的评价包括'文字'
        """
        {
            "product_score": "4",
            "review_detail": "商品2不太好！！！！！！！",
            "serve_score": "4",
            "deliver_score": "4",
            "process_score": "4",
            "picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']"
        }
        """
    Then bill成功获取商品评价后'感谢评价'页面
        """
        [{
            "title2":"返回首页"
        }]
        """
    Then bill成功获取个人中心的'待评价'列表
        """
        [{}]
        """

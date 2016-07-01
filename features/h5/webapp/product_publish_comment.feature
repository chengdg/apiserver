# watcher: zhangsanxiang@weizoom.com,wangxinrui@weizoom.com,benchi@weizoom.com
#author: benchi
#editor: 张三香 2015.10.19
#editor: 新新  2015.10.20

Feature: bill在webapp中对已到货的商品进行评价包括，有图，无图，默认项：商品评分，服务态度，发货速度，物流服务 都为5颗星，评价字数在200个之内，显示项包括，商品名称，价格

Background:
    Given 重置'weapp'的bdd环境
    Given jobs登录系统::weapp
    And jobs已添加商品::weapp
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
    And jobs已有的订单::weapp
        """
        [{
            "order_no":"1",
            "member":"bill",
            "status":"已完成",
            "sources":"本店",
            "order_price":10.00,
            "payment_price":10.00,
            "postage":0.00,
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
            "status":"已完成",
            "sources":"本店",
            "order_price":20.00,
            "payment_price":20.00,
            "postage":0.00,
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
            "products": [
                {
                    "product_name": "商品1"
                }
            ]

        }, {
            "order_no": "2",
            "products": [
                {
                    "product_name": "商品2"
                }
            ]

        }]
        """

@mall2 @person @productReview @product @review   @mall.webapp.comment.dd @mall3 @bert
Scenario:2 无晒图
    When bill访问jobs的webapp
    And bill完成订单'1'中'商品1'的评价
        """
        {
            "product_score": "4",
            "review_detail": "商品1还不错！！！！！",
            "serve_score": "4",
            "deliver_score": "4",
            "process_score": "4"
        }
        """
    Then bill成功获取个人中心的'待评价'列表
        """
        [{
            "order_no": "1",
            "products": [
                {
                    "product_name": "商品1"
                }
            ]
        }, {
            "order_no": "2",
            "products": [
                {
                    "product_name": "商品2"
                }
            ]
        }]
        """


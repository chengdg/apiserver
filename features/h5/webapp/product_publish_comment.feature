#author: benchi
#editor: 张三香 2015.10.19
#editor: 新新  2015.10.20

Feature: bill在webapp中对已到货的商品进行评价包括，有图，无图，默认项：商品评分，服务态度，发货速度，物流服务 都为5颗星，评价字数在200个之内，显示项包括，商品名称，价格

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
            "status":"已完成",
            "sources":"本店",
            "order_price":10.00,
            "payment_price":10.00,
            "postage":0,
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
            "postage":0,
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

@mall2 @person @productReview @product @review   @mall.webapp.comment.dd 
Scenario:1 评价包括文字与晒图
    When bill访问jobs的webapp
    And bill完成订单'1'中'商品1'的评价包括'文字与晒图'
        """
        {
            "product_score": "4",
            "review_detail": "商商商品1还不错！！！！！品1还不错！！！商商品1还不错！！！！！品1还不错！！！商商品1还不错！！！！！品1还不错！！！商商品1还不错！！！！！品1还不错！！！商商品1还不错！！！！！品1还不错！！！商商品1还不错！！！！！品1还不错！！！商商品1还不错！！！！！品1还不错！！！商商品1还不错！！！！！品1还不错！！！商商品1还不错！！！！！品1还不错！！！商品1还不错！！！！！品1还不错！！！!",
            "serve_score": "4",
            "deliver_score": "4",
            "process_score": "4",
            "picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']"
        }
        """
    Then 订单'1'中'商品1'的评商品评价提示信息'发表评价失败'
    # And 订单'1'中'商品1'的评商品评价提示详情'评价文字要求在200字以内'

    #文字在200以内，成功提交
    When bill完成订单'1'中'商品1'的评价包括'文字与晒图'
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
    Then bill成功获取个人中心的'待评价'列表
        """
        [{
            "order_no": "2",
            "products": [
                {
                    "product_name": "商品2"
                }
            ]
        }]
        """

@mall2 @person @productReview @product @review   @mall.webapp.comment.dd 
Scenario:2 无晒图
    When bill访问jobs的webapp
    And bill完成订单'1'中'商品1'的评价包括'文字与晒图'
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


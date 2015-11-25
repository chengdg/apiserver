#author: benchi
#editor: 张三香 2015.10.19
#editor: 新新  2015.10.20

Feature: bill在webapp中进入到待评价列表，对已到货的商品进行评价,评价完成后，商品不在该列表中显示

Background:
    Given jobs登录系统
    And jobs已添加商品规格
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

    And jobs已添加商品
        """
        [{
            "name": "商品1",
            "price": 10.00
        },{
            "name": "商品2",
            "price": 20.00
        },{
            "name": "商品3",
            "price": 30.00
        },{
            "name": "商品4",
            "is_enable_model": "启用规格",
            "model": {
                "models":{
                    "M": {
                        "price": 40.00,
                        "stock_type": "无限"
                    },
                    "S": {
                        "price": 40.00,
                        "stock_type": "无限"
                    }
                }
            }
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
            "order_no":"5",
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
        },{
            "order_no":"3",
            "member":"bill",
            "status":"待支付",
            "sources":"本店",
            "order_price":30.00,
            "payment_price":30.00,
            "postage":0,
            "ship_name":"bill",
            "ship_tel":"13013013011",
            "ship_area":"北京市,北京市,海淀区",
            "ship_address":"泰兴大厦",
            "products":[{
                "name":"商品3",
                "price": 30.00,
                "count": 1
            }]
        },{
            "order_no":"4",
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
            "products":[
            {
                "name":"商品4",
                "model":"M",
                "price": 40.00,
                "count": 1
            }, {
                "name":"商品4",
                "model":"S",
                "price": 40.00,
                "count": 1
            }]
        }]
        """

    When bill访问jobs的webapp
    # 1)在"待评价"中显示的是订单状态为"已完成"的订单；
    Then bill成功获取个人中心的'待评价'列表
        """
        [{
            "order_no": "1",
            "products": [{
                    "product_name": "商品1"
                }]
        },{
            "order_no": "5",
            "products": [{
                    "product_name": "商品1"
                }]
        },{
            "order_no": "2",
            "products": [{
                    "product_name": "商品2"
                }]
        },{
            "order_no": "4",
            "products": [{
                    "product_name": "商品4",
                    "product_model_name": "M"
                },{
                    "product_name": "商品4",
                    "product_model_name": "S"
                }]
        }]
        """

@mall2 @person @productReview @product @review   @mall.webapp.comment.ee
Scenario:1 bill 进入待评价列表，该列表中显示的是订单状态为"已完成"的订单，可以对商品进行评价
    1)在"待评价"中显示的是订单状态为"已完成"的订单；
    2）对订单中的商品评价完后（包括，文字，晒图），那么下次进入"待评价"中，则不会看到该商品
    3）只提供文字评价后，下次进入"待评价"中，则会看到该商品 下，显示"追加晒图"添加完图片之后，该商品则不会显示在"待评价"列表中

    #2）对订单中的商品评价完后（包括，文字，晒图），那么下次进入"待评价"中，则不会看到该商品
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
            "order_no": "5",
            "products": [{
                    "product_name": "商品1"
                }]
        },{
            "order_no": "2",
            "products": [{
                    "product_name": "商品2"
                }]
        },{
            "order_no": "4",
            "products": [{
                    "product_name": "商品4",
                    "product_model_name": "M"
                },{
                    "product_name": "商品4",
                    "product_model_name": "S"
                }]
        }]
        """

    #3）只提供文字评价后，下次进入"待评价"中，则会看到该商品 下，显示"追加晒图",添加完图片之后，该商品则不会显示在"待评价"列表中
    When bill完成订单'2'中'商品2'的评价包括'文字'
        """
        {
            "product_score": "4",
            "review_detail": "商品2不太好！！！！！",
            "serve_score": "4",
            "deliver_score": "4",
            "process_score": "4"
        }
        """
    Then bill成功获取个人中心的'待评价'列表
        """
        [{
            "order_no": "5",
            "products": [{
                    "product_name": "商品1"
                }]
        },{
            "order_no": "2",
            "products": [{
                    "product_name": "商品2"
                }]
        },{
            "order_no": "4",
            "products": [{
                    "product_name": "商品4",
                    "product_model_name": "M"
                },{
                    "product_name": "商品4",
                    "product_model_name": "S"
                }]
        }]
        """

    When bill完成订单'2'中'商品2'的评价包括'晒图'
        """
        {
            "product_score": "4",
            "review_detail": "商品2不太好！！！！！",
            "serve_score": "4",
            "deliver_score": "4",
            "process_score": "4",
           "picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']"
        }
        """
    Then bill成功获取个人中心的'待评价'列表
        """
        [{
            "order_no": "5",
            "products": [{
                    "product_name": "商品1"
                }]
        },{
            "order_no": "4",
            "products": [{
                    "product_name": "商品4",
                    "product_model_name": "M"
                },{
                    "product_name": "商品4",
                    "product_model_name": "S"
                }]
        }]
        """

@mall2 @person @productReview @product @review   @mall.webapp.comment.ee
Scenario:2 同一商品，下过两个订单，不同订单对同一商品的评价不会相互影响
    例如：订单1，购买商品1，订单2，购买商品1，那么对订单1内的商品1评价完后，再次进入，还可以看到订单2的商品1，对其进行评价

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
            "order_no": "5",
            "products": [{
                    "product_name": "商品1"
                }]
        },{
            "order_no": "2",
            "products": [{
                    "product_name": "商品2"
                }]
        },{
            "order_no": "4",
            "products": [{
                    "product_name": "商品4",
                    "product_model_name": "M"
                },{
                    "product_name": "商品4",
                    "product_model_name": "S"
                }]
        }]
        """

@mall2 @person @productReview @product @review   @mall.webapp.comment.ee
Scenario:3 同一商品，不同规格进行评价，不会互相影响
    When bill关注jobs的公众号
    And bill访问jobs的webapp
    When bill完成订单'4'中'商品4:S'的评价包括'文字与晒图'
        """
        {
            "product_score": "4",
            "review_detail": "商品2不太好！！！！！",
            "serve_score": "4",
            "deliver_score": "4",
            "process_score": "4",
            "picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']"
        }
        """
    Then bill成功获取个人中心的'待评价'列表
        """
        [{
            "order_no": "1",
            "products": [{
                    "product_name": "商品1"
                }]
        },{
            "order_no": "5",
            "products": [{
                    "product_name": "商品1"
                }]
        },{
            "order_no": "2",
            "products": [{
                    "product_name": "商品2"
                }]
        },{
            "order_no": "4",
            "products": [{
                    "product_name": "商品4",
                    "product_model_name": "M"
                }]
        }]
        """

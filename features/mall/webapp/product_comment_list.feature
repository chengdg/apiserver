# __author__ : "benchi"
#editor 新新 2015.10.20

Feature: bill在webapp中某个商品详情中能够看到对商品评价信息
    在weapp的商品详情中，只显示两条评价信息；
        1）该评价信息，如果是后台进行了置顶操作，则显示在第一个
        2）否则按评价时间倒叙
        3） 其他评价内容在"更多评价"中显示


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
        }, {
            "name": "商品3",
            "price": 30.00
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
    When bill完成订单'2'中'商品2'的评价包括'文字'
        """
        {
            "product_score": "4",
            "serve_score": "4",
            "deliver_score": "4",
            "process_score": "4",
            "review_detail": "商品2不太好！！！！！！！"
        }
        """

    Given tom关注jobs的公众号
    And jobs已有的订单
        """
        [{
            "order_no":"3",
            "member":"tom",
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
            "order_no":"4",
            "member":"tom",
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
    When tom访问jobs的webapp
    When tom完成订单'3'中'商品1'的评价包括'文字与晒图'
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
    When tom完成订单'4'中'商品2'的评价包括'文字'
        """
        {
            "product_score": "4",
            "serve_score": "4",
            "deliver_score": "4",
            "process_score": "4",
            "review_detail": "商品2不太好！！！！！！！"
        }
        """
    Given jobs登录系统
    When jobs已获取对商品的评价信息
    And jobs已完成对商品的评价信息审核
        """
        [{
            "member": "tom",
            "status": "-1",
            "product_name": "商品1",
            "order_no": "3"
        }, {
            "member": "bill",
            "status": "1",
            "product_name": "商品1",
            "order_no": "1"
        }]
        """


@mall2 @mall.webapp.comment.bb @ProductDetail
Scenario: 1在weapp的商品详情中如果多余两条评价，只显示两条评价信息，如果只有一条评价信息，就显示一条，如果没有评价信息则不显示,只显示审核通过的评价
    1）该评价信息，如果是后台进行了置顶操作，则显示出来，
    2）否则把最后两条信息显示出来

    Given bill关注jobs的公众号
    When bill访问jobs的webapp
    And bill在商城首页点击'商品1'的链接
    #publish：true为bill可以看到，false 则bill看不到,top为true则置顶，其他按评价时间倒叙排列
    #在详情页只显示两条，信息内容包括，商品名，评价时间，评价内容，注意：置顶
    Then bill在商品详情页成功获取'商品1'的评价列表
        """
        [{
            "member": "bill",
            "review_detail": "商品1还不错！！！！！"
        }]
        """

    When bill在'商品1'的商品详情页点击'更多评价'

    Then bill成功获取'商品1'的商品详情的'更多评价'
        """
        [{
            "member": "bill",
            "review_detail": "商品1还不错！！！！！"
        }]
        """
    When bill在商城首页点击'商品2'的链接
    Then bill在商品详情页成功获取'商品2'的评价列表
        """
        [{}]
        """

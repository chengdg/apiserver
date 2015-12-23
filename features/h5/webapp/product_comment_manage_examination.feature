# __author__ : "benchi"
# __author__ : "冯雪静"
#editor:王丽 2015.15.10

Feature: jobs在后台对已有评价进行审核
"""
    [商品详情页的验证]
    1.审核通过：用户评价内容将显示在商品详情页；
    2.屏蔽处理：该评价将不被允许显示在商品详情页；
    3.通过并置顶：是指审核通过该评论，并且置顶显示该评价；
    4.置顶时间为15天，置顶周期结束后，恢复按评价时间倒序显示。
    5 同款商品，3个置顶操作，最后置顶的，排在最上面
    6.同款商品，最多可置顶3条评价信息，第4条置顶时，第一条置顶信息失去优先级，按原有时间顺序排列
    7.设置商品评价送积分，审核通过后，会给用户加相应的积分
"""

Background:

    Given jobs登录系统
    And jobs设定会员积分策略
        """
        {
            "be_member_increase_count": 20
        }
        """
    And jobs已添加商品
        """
        [{
            "name": "商品1",
            "price": "10.00"
            }, {
            "name": "商品2",
            "price": "20.00"
            }, {
            "name": "商品3",
            "price": "30.00"
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
            "order_no":"12",
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
            "order_no":"13",
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
            "order_no":"14",
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
            "order_no":"15",
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
            "order_no":"16",
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
    And bill完成订单'1'中'商品1'的评价
        """
        {
            "product_score": "4",
            "review_detail": "1商品1还不错！！！！！",
            "serve_score": "4",
            "deliver_score": "4",
            "process_score": "4",
            "picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']"
        }
        """
    And bill完成订单'12'中'商品1'的评价
        """
        {
            "product_score": "4",
            "review_detail": "12商品1还不错！！！！！",
            "serve_score": "4",
            "deliver_score": "4",
            "process_score": "4",
            "picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']"
        }
        """
    And bill完成订单'13'中'商品1'的评价
        """
        {
            "product_score": "4",
            "review_detail": "13商品1还不错！！！！！",
            "serve_score": "4",
            "deliver_score": "4",
            "process_score": "4",
            "picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']"
        }
        """
    And bill完成订单'14'中'商品1'的评价
        """
        {
            "product_score": "4",
            "review_detail": "14商品1还不错！！！！！",
            "serve_score": "4",
            "deliver_score": "4",
            "process_score": "4",
            "picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']"
        }
        """
    And bill完成订单'15'中'商品1'的评价
        """
        {
            "product_score": "4",
            "review_detail": "15商品1还不错！！！！！",
            "serve_score": "4",
            "deliver_score": "4",
            "process_score": "4",
            "picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']"
        }
        """
    And bill完成订单'16'中'商品1'的评价
        """
        {
            "product_score": "4",
            "review_detail": "16商品1还不错！！！！！",
            "serve_score": "4",
            "deliver_score": "4",
            "process_score": "4",
            "picture_list": "['/static/upload/webapp/3_20151102/2015_11_02_18_24_49_948000.png']"
        }
        """

    And bill完成订单'2'中'商品2'的评价
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
    When tom完成订单'3'中'商品1'的评价
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
    When tom完成订单'4'中'商品2'的评价
        """
        {
            "product_score": "4",
            "serve_score": "4",
            "deliver_score": "4",
            "process_score": "4",
            "review_detail": "商品2不太好！！！！！！！"
        }
        """

@mall2 @product @review   @mall.webapp.comment @prm1 @ProductDetail
Scenario:1 审核通过 屏蔽处理 通过并置顶
    1.审核通过:用户评价内容将显示在商品详情页
    2.屏蔽处理：该评价将不被允许显示在商品详情页
    3.通过并置顶：是指审核通过该评论，并且置顶显示该评价；

    Given jobs登录系统
    When jobs已完成对商品的评价信息审核
        """
        [{
            "product_name": "商品1",
            "order_no": "3",
            "member": "tom",
            "status": "-1"
        },{
            "product_name": "商品1",
            "order_no": "1",
            "member": "bill",
            "status": "1"
        },{
            "product_name": "商品1",
            "order_no": "12",
            "member": "bill",
            "status": "2"
        },{
           "member": "tom",
           "order_no": "4",
           "product_name": "商品2",
           "status": "0"
        },{
           "member": "bill",
           "order_no": "2",
           "product_name": "商品2",
           "status": "2"
        }]
        """

    When bill访问jobs的webapp
    #publish：true为bill可以看到，false 为屏蔽，则bill看不到,
    #top为true则置顶，其他按评价时间倒叙排列
    #在详情页只显示两条，信息内容包括，商品名，评价时间，评价内容，注意：置顶
    Then bill在商品详情页成功获取'商品1'的评价列表
        """
        [{
            "member": "bill",
            "review_detail": "12商品1还不错！！！！！"
        },{
            "member": "bill",
            "review_detail": "1商品1还不错！！！！！"
        }]
        """

    And bill在商品详情页成功获取'商品2'的评价列表
        """
        [{
            "member": "bill",
            "review_detail": "商品2不太好！！！！！！！"
        }]
        """

@mall2 @product @review @mall.webapp.comment @prm5 @ProductDetail
Scenario:2 同款商品，3个置顶操作，最后置顶的，排在最上面
    Given jobs登录系统
    When jobs已完成对商品的评价信息审核
        """
        [{
            "product_name": "商品1",
            "order_no": "3",
            "member": "tom",
            "status": "-1"
        },{
            "product_name": "商品1",
            "order_no": "1",
            "member": "bill",
            "status": "1"
        },{
            "product_name": "商品1",
            "order_no": "12",
            "member": "bill",
            "status": "2"
        },{
            "product_name": "商品1",
            "order_no": "13",
            "member": "bill",
            "status": "2"
        },{
            "product_name": "商品1",
            "order_no": "14",
            "member": "bill",
            "status": "2"
        },{
            "member": "tom",
            "order_no": "4",
            "product_name": "商品2",
            "status": "0"
        },{
            "member": "bill",
            "order_no": "2",
            "product_name": "商品2",
            "status": "2"
        }]
        """

    Given bill关注jobs的公众号
    When bill访问jobs的webapp
    #publish：true为bill可以看到，false 为屏蔽，则bill看不到,top为true则置顶，
    #其他按评价时间倒叙排列
    Then bill在商品详情页成功获取'商品1'的评价列表
        """
        [{
            "member": "bill",
            "review_detail": "14商品1还不错！！！！！"
        },{
            "member": "bill",
            "review_detail": "13商品1还不错！！！！！"
        }]
        """
    When bill在'商品1'的商品详情页点击'更多评价'

    Then bill成功获取'商品1'的商品详情的'更多评价'
        """
        [{
            "member": "bill",
            "review_detail": "14商品1还不错！！！！！"
        },{
            "member": "bill",
            "review_detail": "13商品1还不错！！！！！"
        },{
            "member": "bill",
            "review_detail": "12商品1还不错！！！！！"
        },{
            "member": "bill",
            "review_detail": "1商品1还不错！！！！！"
        }]
        """

@mall2 @product @review   @mall.webapp.comment @prm6 @ProductDetail
Scenario:3 同款商品，最多可置顶3条评价信息
    第4条置顶时，第一条置顶信息失去优先级，按原有时间顺序排列

    Given jobs登录系统
    When jobs已完成对商品的评价信息审核
        """
        [{
            "product_name": "商品1",
            "order_no": "3",
            "member": "tom",
            "status": "-1"
        },{
            "product_name": "商品1",
            "order_no": "1",
            "member": "bill",
            "status": "2"
        },{
            "product_name": "商品1",
            "order_no": "12",
            "member": "bill",
            "status": "2"
        },{
            "product_name": "商品1",
            "order_no": "13",
            "member": "bill",
            "status": "2"
        },{
            "product_name": "商品1",
            "order_no": "14",
            "member": "bill",
            "status": "2"
        },{
            "product_name": "商品1",
            "order_no": "15",
            "member": "bill",
            "status": "1"
        },{
            "product_name": "商品1",
            "order_no": "16",
            "member": "bill",
            "status": "1"
        },{
            "member": "tom",
            "order_no": "4",
            "product_name": "商品2",
            "status": "0"
        },{
            "member": "bill",
            "order_no": "2",
            "product_name": "商品2",
            "status": "2"
        }]
        """
    Given bill关注jobs的公众号
    When bill访问jobs的webapp
    #publish：true为bill可以看到，false 为屏蔽，则bill看不到,top为true则置顶，
    #其他按评价时间倒叙排列

    And bill在'商品1'的商品详情页点击'更多评价'

    Then bill成功获取'商品1'的商品详情的'更多评价'
        """
        [{
            "member": "bill",
            "review_detail": "14商品1还不错！！！！！"
        },{
            "member": "bill",
            "review_detail": "13商品1还不错！！！！！"
        },{
            "member": "bill",
            "review_detail": "12商品1还不错！！！！！"
        },{
            "member": "bill",
            "review_detail": "16商品1还不错！！！！！"
        },{
            "member": "bill",
            "review_detail": "15商品1还不错！！！！！"
        },{
            "member": "bill",
            "review_detail": "1商品1还不错！！！！！"
        }]
        """

#后续补充.雪静
@mall2 @product @review   @mall.webapp.comment @prm7
Scenario:4 jobs通过审核评价，给用户加积分
   1.tom评价jobs的商品，jobs通过审核，给tom加相应的积分
   2.tom评价jobs的商品，jobs通过并置顶，给tom加相应的积分
   3.jobs取消置顶，屏蔽评论，tom的积分不变

    When tom访问jobs的webapp
    Then tom在jobs的webapp中获得积分日志
        """
        [{
            "content": "首次关注",
            "integral": 20
        }]
        """
    Given jobs登录系统
    And jobs设定会员积分策略
        """
        {
            "review_increase": 20,
            "be_member_increase_count": 20
        }
        """
    When jobs已完成对商品的评价信息审核
        """
        [{
            "product_name": "商品1",
            "order_no": "3",
            "member": "tom",
            "status": "1"
        }]
        """
    When tom访问jobs的webapp
    Then tom在jobs的webapp中获得积分日志
        """
        [{
            "content": "商品评价奖励",
            "integral": 20
        },{
            "content": "首次关注",
            "integral": 20
        }]
        """
    Given jobs登录系统
    When jobs已完成对商品的评价信息审核
        """
        [{
            "product_name": "商品2",
            "order_no": "4",
            "member": "tom",
            "status": "2"
        }]
        """
    When tom访问jobs的webapp
    Then tom在jobs的webapp中获得积分日志
        """
        [{
            "content": "商品评价奖励",
            "integral": 20
        },{
            "content": "商品评价奖励",
            "integral": 20
        },{
            "content": "首次关注",
            "integral": 20
        }]
        """
    Given jobs登录系统
    When jobs已完成对商品的评价信息审核
        """
        [{
            "product_name": "商品2",
            "order_no": "4",
            "member": "tom",
            "status": "1"
        }]
        """
    When tom访问jobs的webapp
    Then tom在jobs的webapp中获得积分日志
        """
        [{
            "content": "商品评价奖励",
            "integral": 20
        },{
            "content": "商品评价奖励",
            "integral": 20
        },{
            "content": "首次关注",
            "integral": 20
        }]
        """
    Given jobs登录系统
    When jobs已完成对商品的评价信息审核
        """
        [{
            "product_name": "商品2",
            "order_no": "4",
            "member": "tom",
            "status": "-1"
        }]
        """
    When tom访问jobs的webapp
    Then tom在jobs的webapp中获得积分日志
        """
        [{
            "content": "商品评价奖励",
            "integral": 20
        },{
            "content": "商品评价奖励",
            "integral": 20
        },{
            "content": "首次关注",
            "integral": 20
        }]
        """
    Given jobs登录系统
    When jobs已完成对商品的评价信息审核
        """
        [{
            "product_name": "商品1",
            "order_no": "3",
            "member": "tom",
            "status": "2"
        }]
        """
    When tom访问jobs的webapp
    Then tom在jobs的webapp中获得积分日志
        """
        [{
            "content": "商品评价奖励",
            "integral": 20
        },{
            "content": "商品评价奖励",
            "integral": 20
        },{
            "content": "首次关注",
            "integral": 20
        }]
        """

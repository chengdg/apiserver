# -*- coding: utf-8 -*-
"""
@package business.mall.order_config
订单分享挣积分配置
"""
from wapi.decorators import param_required
from db.mall import models as mall_models
from datetime import datetime
from business import model as business_model

class OrderConfig(business_model.Model):
    """
    订单分享挣积分配置
    """

    __slots__ = (
        'id',
        'owner_id',
        'background_image',
        'share_image',
        'share_describe',
        'news_id'
    )

    def __init(self, model):
        business_model.Model.__init__(self)

        if model:
            self._init_slot_from_model(model)

    @staticmethod
    @param_required(['webapp_owner'])
    def get_order_config(args):
        webapp_owner = args['webapp_owner']

        model = mall_models.MallShareOrderPageConfig.select().dj_where(owner_id = webapp_owner.id).first()
        order_config = OrderConfig(model)
        return order_config
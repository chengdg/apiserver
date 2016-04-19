# -*- coding: utf-8 -*-
"""
@package business.mall.order_config
订单分享挣积分配置
"""
from datetime import datetime

import settings
from wapi.decorators import param_required
from db.mall import models as mall_models
from business import model as business_model

class OrderConfig(business_model.Model):
    """
    订单分享挣积分配置
    """

    __slots__ = (
        'id',
        'owner_id',
        'is_share_page',
        'background_image',
        'share_image',
        'share_describe',
        'material_id'
    )

    def __init__(self, model):
        business_model.Model.__init__(self)

        if model:
            self._init_slot_from_model(model)
            self.background_image = '%s%s' % ((settings.IMAGE_HOST, model.background_image) if model.background_image.find('http') == -1 else model.background_image)
            self.share_image = '%s%s' % ((settings.IMAGE_HOST, model.share_image) if model.share_image.find('http') == -1 else model.share_image)

    @staticmethod
    @param_required([])
    def get_order_config(args):
        webapp_owner = args['webapp_owner']
        model = mall_models.MallShareOrderPageConfig.select().dj_where(owner_id = webapp_owner.id).first()
        order_config = OrderConfig(model).to_dict()
        return order_config
# -*- coding: utf-8 -*-

from business import model as business_model
from db.member import models as member_models

class TengyiRebateDetails(business_model.Model):
    """
    腾易会员返利详情业务模型
    """
    __slots__ = (
        'id',
        'member_id',
        'is_self_order',
        'supply_member_id',
        'is_exchanged',
        'exchanged_at',
        'rebate_money',
        'created_at'
    )

    def __init__(self, model):
        business_model.Model.__init__(self)

        if model:
            self._init_slot_from_model(model)

    @staticmethod
    def get(member_id):
        models = member_models.TengyiRebateLog.select().dj_where(
            member_id = member_id
        )
        if models.count() > 0:
            return [TengyiRebateDetails(model) for model in models]
        else:
            return []
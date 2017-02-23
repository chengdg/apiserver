# -*- coding: utf-8 -*-

from business import model as business_model
from db.member import models as member_models

class TengyiMember(business_model.Model):
    """
    腾易微众会员业务模型
    """
    __slots__ = (
        'id',
        'member_id',
        'recommend_by_member_id',
        'level',
        'card_number',
        'created_at'
    )

    def __init__(self, model):
        business_model.Model.__init__(self)

        if model:
            self._init_slot_from_model(model)

    @staticmethod
    def get(member_id):
        model = member_models.TengyiMember.select().dj_where(
            member_id = member_id
        ).first()
        if model:
            return TengyiMember(model)
        else:
            return None
# -*- coding: utf-8 -*-

import logging
import settings

from eaglet.decorator import param_required
from core.decorator import deprecated

from business import model as business_model
from db.member import models as member_models

class ChannelDistributionQrcodeSettings(business_model.Model):
    """
    渠道分销二维码业务模型
    """
    __slots__ = (
        'id',
        'owner_id',
        'bing_member_title',
        'award_prize_info',
        'reply_type',
        'reply_detail',
        'reply_material_id',
        'coupon_ids',
        'bing_member_id',
        'return_standard',
        'group_id',
        'distribution_rewards',
        'commission_rate',
        'minimun_return_rate',
        'commission_return_standard',
        'ticket',
        'bing_member_count',
        'total_transaction_volume',
        'total_return',
        'will_return_reward',
        'created_at'
    )

    def __init__(self, model):
        business_model.Model.__init__(self)

        if model:
            self._init_slot_from_model(model)

    @staticmethod
    @param_required(['webapp_user', 'webapp_owner'])
    def get_for_webapp_user(args):
        owner_id = args['webapp_owner'].id
        member_id = args['webapp_user'].member.id

        model = member_models.ChannelDistributionQrcodeSettings.select().dj_where(
                owner_id=owner_id,
                bing_member_id=member_id
            ).first()
        if model:
            return ChannelDistributionQrcodeSettings(model)
        else:
            return None
# -*- coding: utf-8 -*-

from business import model as business_model
from business.account.member import Member
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
        'created_at',
        'member_info',
        'rebate_info'
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

    def get_referees(self, webapp_owner, fill_info=None):
        models = member_models.TengyiMember.select().dj_where(
            recommend_by_member_id = self.member_id,
        )
        members = [TengyiMember(model) for model in models]
        if fill_info:
            if fill_info.get('fill_member_info'):
                TengyiMember.__fill_member_info(webapp_owner, members)
        return members

    def get_rebated_details(self, webapp_owner):
        rebate_logs = member_models.TengyiRebateLog.select().dj_where(member_id=self.member_id,
                                                                      is_exchanged=True)
        member_ids = [r.supply_member_id for r in rebate_logs]
        member_ids.append(self.member_id)

        account_members = Member.from_ids(webapp_owner, member_ids)
        member_id2info = {m.id: m for m in account_members}

        for log in rebate_logs:
            supplier_id = self.member_id if log.is_self_order else log.supply_member_id
            member_info = member_id2info[supplier_id]
            self.rebate_info = {
                'is_self_rebate': log.is_self_order,
                'supplier_id': supplier_id,
                'supplier_name': member_info.username_for_html,
                'supplier_icon': member_info.user_icon,
                'rebate_time': log.exchanged_at.strftime('%Y-%m-%d %H:%M:%S'),
                'rebate_money': '%.2f' % log.rebate_money
            }
        return self.rebate_info

    @staticmethod
    def __fill_member_info(webapp_owner, members):
        member_ids = [m.member_id for m in members]
        account_members = Member.from_ids({
            'webapp_owner': webapp_owner,
            'member_ids': member_ids
        })
        member_id2info = {m.id: m for m in account_members}

        for member in members:
            member_id = member.member_id
            member_info = member_id2info[member_id]
            member.member_info = {
                'member_name': member_info.username_for_html,
                'user_icon': member_info.user_icon
            }
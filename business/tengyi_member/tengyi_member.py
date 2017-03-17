# -*- coding: utf-8 -*-

from datetime import datetime
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

    def __init__(self, model=None):
        business_model.Model.__init__(self)
        self.rebate_info = []
        self.level = 0 #此时表示还未成为正式星级会员

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
        ty_member_ids = [m.member_id for m in models]

        if ty_member_ids:
            relation_modes = member_models.TengyiMemberRelation.select().dj_where(member_id__notin=ty_member_ids,
                                                                                  recommend_by_member_id=self.member_id)
        else:
            relation_modes = member_models.TengyiMemberRelation.select().dj_where(recommend_by_member_id=self.member_id)
        ty_pre_members = [TengyiMember.from_dict({
            'member_id': m.member_id,
            'recommend_by_member_id': m.recommend_by_member_id,
            'level': 0,
            'created_at': m.created_at
        }) for m in relation_modes]
        ty_members = [TengyiMember(model) for model in models]
        all = ty_pre_members + ty_members
        if fill_info:
            if fill_info.get('fill_member_info'):
                TengyiMember.__fill_member_info(webapp_owner, all)
        return all

    def get_rebated_details(self, webapp_owner):
        rebate_logs = member_models.TengyiRebateLog.select().dj_where(member_id=self.member_id,
                                                                      is_exchanged=True)
        member_ids = [r.supply_member_id for r in rebate_logs]
        member_ids.append(self.member_id)

        account_members = Member.from_ids({
            'webapp_owner': webapp_owner,
            'member_ids': member_ids
        })
        member_id2info = {m.id: m for m in account_members}



        for log in rebate_logs:
            supplier_id = self.member_id if log.is_self_order else log.supply_member_id
            member_info = member_id2info[supplier_id]
            self.rebate_info.append({
                'is_self_rebate': log.is_self_order,
                'supplier_id': supplier_id,
                'supplier_name': member_info.username_for_html,
                'supplier_icon': member_info.user_icon,
                'rebate_time': log.exchanged_at.strftime('%Y-%m-%d %H:%M:%S'),
                'rebate_money': '%.2f' % log.rebate_money
            })
        return self.rebate_info

    def get_rebate_plan(self):
        plans = member_models.TengyiMemberRebateCycle.select().dj_where(member_id=self.member_id)

        return [{
            'date_range': ' - '.join([plan.start_time.strftime('%Y/%m/%d'), plan.end_time.strftime('%Y/%m/%d')]),
            'created_at': plan.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'rebate_money': plan.recommend_member_rebate_money,
            'status': self.__get_plan_status_text(plan)[0],
            'status_text': self.__get_plan_status_text(plan)[1]
        } for plan in plans]

    def __get_plan_status_text(self, plan):
        status_num2text = [u'待激活', u'7天后到账', u'已到帐', u'已过期', u'未知']
        is_receive_reward = plan.is_receive_reward
        start_time = plan.start_time.strftime('%Y/%m/%d')
        end_time = plan.end_time.strftime('%Y/%m/%d')
        now_time = datetime.now().strftime('%Y/%m/%d')

        if is_receive_reward: #已到帐
            return 2, status_num2text[2]
        else:
            logs = member_models.TengyiRebateLog.select().dj_where(member_id=plan.member_id,
                                                                   created_at__range=[plan.start_time.strftime('%Y-%m-%d'), plan.end_time.strftime('%Y-%m-%d')],
                                                                   is_exchanged=False, is_self_order=True)
            if logs.count() > 0:  # 已经返利但未到账
                return 1, status_num2text[1]
            if now_time < start_time or (now_time >= start_time and now_time <= end_time): #还未到计划时间或者当前正处于计划之中
                return 0, status_num2text[0]
            elif now_time > end_time: #已超过计划时间
                return 3, status_num2text[3]
            else: #
                return 4, status_num2text[4]

    @staticmethod
    def __fill_member_info(webapp_owner, ty_members):
        member_ids = [m.member_id for m in ty_members]
        account_members = Member.from_ids({
            'webapp_owner': webapp_owner,
            'member_ids': member_ids
        })
        member_id2info = {m.id: m for m in account_members}

        for ty_member in ty_members:
            member_id = ty_member.member_id
            member_info = member_id2info[member_id]
            ty_member.member_info = {
                'member_name': member_info.username_for_html,
                'user_icon': member_info.user_icon
            }
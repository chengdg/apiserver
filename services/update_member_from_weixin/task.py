# -*- coding: utf-8 -*-
from celery import task

from core.exceptionutil import unicode_full_stack
from core.watchdog.utils import watchdog_error
from db.member import models as member_model

from business.account.webapp_owner import WebAppOwner
from business.account.member_info_updater import MemberInfoUpdater


@task(bind=True)
def update_member_info(self, webapp_user_id, woid):
    """
    更新会员信息
    """

    webapp_owner = WebAppOwner.get({
        'woid': woid
        })

    #webapp_owner

    MemberInfoUpdater(webapp_owner).update(webapp_user_id)
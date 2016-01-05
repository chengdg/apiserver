# -*- coding: utf-8 -*-
from celery import task

from core.exceptionutil import unicode_full_stack
from core.watchdog.utils import watchdog_error
from db.member import models as member_model


@task(bind=True)
def update_member_info(self, webapp_user_id, woid):
    """
    更新会员信息
    """

    webapp_owner = WebAppOwner.get({
        'woid': webapp_owner_id
        })

    #webapp_owner

    MemberInfoUpdater(webapp_owner).update()
# -*- coding: utf-8 -*-
from eaglet.core.service.celery import task

from core.exceptionutil import unicode_full_stack
from eaglet.core import watchdog
from db.member import models as member_model


@task(bind=True)
def record_member_pv(self, member_id, url, page_title=''):
    """
    记录会员访问轨迹
    """
    try:
        member_model.MemberBrowseRecord.create(
                title=page_title,
                url=url,
                member=member_id
        )
    except:
        notify_message = u"record_member_pv,member_id:{} cause:\n{}".format(member_id, unicode_full_stack())
        watchdog.error(notify_message)
        raise self.retry()

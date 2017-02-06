# -*- coding: utf-8 -*-
from eaglet.core.service.celery import task

from core.exceptionutil import unicode_full_stack
from eaglet.core import watchdog
from db.member import models as member_model
import urlparse


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

        #访问商品详情单独写到一张表里，方便统计商品的访问记录  duhao  20161221
        if 'module=mall' in url and 'model=product' in url and 'model=products' not in url:
            result = urlparse.urlparse(url)
            params = urlparse.parse_qs(result.query, True)
            owner_id = params['woid'][0]
            product_id = params['rid'][0]
            referer = ''
            member_model.MemberBrowseProductRecord.create(
                title = page_title,
                url = url,
                member=member_id,
                owner_id=owner_id,
                product_id=product_id,
                referer=referer
            )
    except:
        notify_message = u"record_member_pv,member_id:{} cause:\n{}".format(member_id, unicode_full_stack())
        watchdog.error(notify_message)
        raise self.retry()

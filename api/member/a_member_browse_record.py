# -*- coding: utf-8 -*-
from eaglet.core import api_resource
from eaglet.decorator import param_required
from services.record_member_pv_service.task import record_member_pv


class AMemberBrowseRecord(api_resource.ApiResource):
    """
    记录会员访问轨迹
    """
    app = 'member'
    resource = 'browse_record'

    @param_required(['url', 'page_title'])
    def put(args):
        """
        创建会员访问轨迹
        """
        member_id = args['webapp_user'].member.id

        url = args['url']
        page_title = args['page_title']

        record_member_pv.delay(member_id, url, page_title)
        return {}
# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.mall.product_limit_zone_template import ProductLimitZoneTemplate

class AProductLimitZone(api_resource.ApiResource):
    """
    限定区域的信息
    """
    app = 'mall'
    resource = 'product_limit_zone'

    @param_required(['template_id'])
    def get(args):
        id = args['template_id']
        template = ProductLimitZoneTemplate.from_id({'id': id})
        return {'items': template.limit_zone_detail()}
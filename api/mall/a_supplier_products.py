# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required
from eaglet.core import paginator

from business.mall.new_simple_products import NewSimpleProducts
from business.mall.supplier import Supplier


class ASupplierProducts(api_resource.ApiResource):
    """
    供货商商品列表
    """
    app = 'mall'
    resource = 'supplier_products'

    @param_required(['webapp_owner', 'supplier_id'])
    def get(args):
        """
        获取商品详情

        @param supplier_id 商品供货商ID
        @return {
            'supplier_name': supplier_name,
            'products': simple_products.products,
            }
        """

        supplier_id = int(args['supplier_id'])
        webapp_owner = args['webapp_owner']
        webapp_user = args['webapp_user']
        cur_page = args['cur_page']
        cur_page_count = args.get('cur_page_count', 6)

        if supplier_id:
            supplier_name = Supplier.get_supplier_name(supplier_id)
        else:
            pass

        products, no_cache, page_info = Supplier().get_products_by_page(supplier_id, webapp_owner, cur_page, cur_page_count)
        is_cache_pending = False
        if no_cache:
            is_cache_pending = True
        
        
        return dict(products=products, supplier_name=supplier_name, mall_config=webapp_owner.mall_config,
                    page_info=page_info.to_dict(),
                    is_cache_pending=is_cache_pending)

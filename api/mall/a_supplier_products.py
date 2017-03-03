# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required
from eaglet.core import paginator

from business.mall.simple_products import SimpleProducts
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

        if supplier_id:
            supplier_name = Supplier.get_supplier_name(supplier_id)
        else:
            pass

        simple_products = SimpleProducts.get({
            "webapp_owner": webapp_owner,
            "category_id": 0
        })


        products = simple_products.products
        products = filter(lambda p: p['supplier'] == supplier_id, products)
        # 加上分页 TODO 放在业务层和分页页码处理
        page_info, products = paginator.paginate(products, cur_page, 6)
        
        return dict(products=products, supplier_name=supplier_name, mall_config=webapp_owner.mall_config,
                    page_info=page_info.to_dict())

# -*- coding: utf-8 -*-

from celery import task

from db.mall import models as mall_models


@task(bind=True)
def update_product_sale(self, product_sale_infos):
    """
    更新商品销量
    """
    for product_sale_info in product_sale_infos:
        if mall_models.ProductSales.select().dj_where(product_id=product_sale_info['product_id']).first():
            mall_models.ProductSales.update(
                sales=mall_models.ProductSales.sales + product_sale_info['purchase_count']).dj_where(
                    product_id=product_sale_info['product_id']).execute()
        else:
            mall_models.ProductSales.create(product=product_sale_info['product_id'],
                                            sales=product_sale_info['purchase_count'])

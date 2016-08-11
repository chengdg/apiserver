# -*- coding: utf-8 -*-
"""@package business.mall.supplier
供货商
"""
from eaglet.decorator import param_required

from business import model as business_model
from db.mall import models as mall_models

class SupplierPostageConfig(business_model.Model):
    """供货商
    """
    __slots__ = (
        'id',
        'supplier_id',
        'product_id',
        'condition_type',
        'condition_money',
        'condition_count',
        'postage',
        'status'
    )

    def __init__(self, model):
        business_model.Model.__init__(self)

        if model:
            self._init_slot_from_model(model)

    @staticmethod
    @param_required(['supplier_ids'])
    def from_suppler_ids(args):
        supplier_ids = args['supplier_ids']
        models = mall_models.SupplierPostageConfig.select().dj_where(
                supplier_id__in=supplier_ids,
                status=True
            )
        supplier_postage_configs = []
        for model in models:
            supplier_postage_configs.append(SupplierPostageConfig(model))
        return supplier_postage_configs

    @staticmethod
    @param_required(['supplier_ids'])
    def get_supplier_postage_config_by_supplier(args):
        supplier_ids = args['supplier_ids']
        configs = SupplierPostageConfig.from_suppler_ids({'supplier_ids': supplier_ids})
        return dict([config.supplier_id, {
                'condition_type': config.condition_type,
                'condition_money': config.condition_money,
                'postage': config.postage
            }] for config in configs)
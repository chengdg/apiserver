# -*- coding: utf-8 -*-
"""@package business.mall.supplier
供货商
"""
from eaglet.decorator import param_required

from business import model as business_model
from db.mall import models as mall_models
from db.account import models as account_models

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

    @staticmethod
    @param_required(['product_groups', 'supplier_ids'])
    def product_group_use_supplier_postage(args):
        product_groups = args['product_groups']
        supplier_ids = args['supplier_ids']
        supplier_models = mall_models.Supplier.select().dj_where(id__in=supplier_ids, name=u'自营')
        tmp_user_ids = [model.owner_id for model in supplier_models]
        user_ids = [profile.user_id for profile in account_models.UserProfile.select().dj_where(user_id__in=tmp_user_ids, webapp_type=3)]
        not_use_supplier_postage_supplier_id = [model.id for model in supplier_models if model.owner_id in user_ids]

        for group in product_groups:
            for data in group:
                try:
                    if data['products'][0]['supplier'] in not_use_supplier_postage_supplier_id:
                        data['use_supplier_postage'] = False
                    else:
                        data['use_supplier_postage'] = True
                except:

                    data['use_supplier_postage'] = True

        return product_groups
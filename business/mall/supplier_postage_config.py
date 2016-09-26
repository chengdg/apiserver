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
        postage_configs = mall_models.PostageConfig.select().dj_where(supplier_id__in=supplier_ids)
        supplier_postage_configs = {}
        for postage_config in postage_configs:
            factor = {
                'firstWeight': postage_config.first_weight,
                'firstWeightPrice': postage_config.first_weight_price,
                'isEnableAddedWeight': postage_config.is_enable_added_weight,
            }

            # if postage_config.is_enable_added_weight:
            factor['addedWeight'] = float(postage_config.added_weight)
            if postage_config.added_weight_price:
                factor['addedWeightPrice'] = float(postage_config.added_weight_price)
            else:
                factor['addedWeightPrice'] = 0

            # 特殊运费配置
            special_factor = dict()
            if postage_config.is_enable_special_config:
                for special_config in postage_config.get_special_configs():
                    data = {
                        'firstWeight': special_config.first_weight,
                        'firstWeightPrice': special_config.first_weight_price,
                        'addedWeight': float(special_config.added_weight),
                        'addedWeightPrice': float(special_config.added_weight_price)
                    }
                    for province_id in special_config.destination.split(','):
                        special_factor['province_{}'.format(province_id)] = data
            factor['special_factor'] = special_factor

            # 免运费配置
            free_factor = dict()
            if postage_config.is_enable_free_config:
                for free_config in postage_config.get_free_configs():
                    data = {
                        'condition': free_config.condition
                    }
                    if data['condition'] == 'money':
                        data['condition_value'] = float(free_config.condition_value)
                    else:
                        data['condition_value'] = int(free_config.condition_value)
                    for province_id in free_config.destination.split(','):
                        free_factor.setdefault('province_{}'.format(province_id), []).append(data)
            factor['free_factor'] = free_factor

            postage_config.factor = factor
            supplier_postage_configs[postage_config.supplier_id] = postage_config.to_dict('factor')
        return supplier_postage_configs

    @staticmethod
    @param_required(['supplier_ids'])
    def get_supplier_postage_config_by_supplier(args):
        supplier_ids = args['supplier_ids']
        configs = SupplierPostageConfig.from_suppler_ids({'supplier_ids': supplier_ids})
        return configs

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
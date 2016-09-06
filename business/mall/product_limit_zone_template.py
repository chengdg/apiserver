# -*- coding: utf-8 -*-
from eaglet.decorator import param_required

from db.mall import models as mall_models
from business import model as business_model

ZONE_NAMES = [u'直辖市', u'华北-东北', u'华东地区', u'华南-华中', u'西北-西南', u'其它']

PROVINCE_ID2ZONE = {
    1: u'直辖市',
    2: u'直辖市',
    3: u'华北-东北',
    4: u'华北-东北',
    5: u'华北-东北',
    6: u'华北-东北',
    7: u'华北-东北',
    8: u'华北-东北',
    9: u'直辖市',
    10: u'华东地区',
    11: u'华东地区',
    12: u'华东地区',
    13: u'华东地区',
    14: u'华东地区',
    15: u'华东地区',
    16: u'华南-华中',
    17: u'华南-华中',
    18: u'华南-华中',
    19: u'华南-华中',
    20: u'华南-华中',
    21: u'华南-华中',
    22: u'直辖市',
    23: u'西北-西南',
    24: u'西北-西南',
    25: u'西北-西南',
    26: u'西北-西南',
    27: u'西北-西南',
    28: u'西北-西南',
    29: u'西北-西南',
    30: u'西北-西南',
    31: u'西北-西南',
    32: u'其它',
    33: u'其它',
    34: u'其它',
}

class ProductLimitZoneTemplate(business_model.Model):
    __slots__ = (
        'id',
        'owner_id',
        'provinces',
        'cities',
        'created_at'
    )

    def __init__(self, model):
        business_model.Model.__init__(self)

        if model:
            self._init_slot_from_model(model)

    @staticmethod
    @param_required(['id'])
    def from_id(args):
        id = args['id']
        model = mall_models.ProductLimitZoneTemplate.select().dj_where(id=id).first()
        if model:
            return ProductLimitZoneTemplate(model)

    def __rename_zone(self, zone):
        if zone['provinceId'] == 5:
            zone['provinceName'] = u'内蒙古'
        elif zone['provinceId'] == 20:
            zone['provinceName'] = u'广西'
        elif zone['provinceId'] == 26:
            zone['provinceName'] = u'西藏'
        elif zone['provinceId'] == 30:
            zone['provinceName'] = u'宁夏'
        elif zone['provinceId'] == 31:
            zone['provinceName'] = u'新疆'
        elif zone['provinceId'] == 32:
            zone['provinceName'] = u'香港'
        elif zone['provinceId'] == 33:
            zone['provinceName'] = u'澳门'
        elif zone['provinceId'] == 34:
            zone['provinceName'] = u'台湾'
        return zone

    def limit_zone_detail(self):
        city_ids = self.cities.split(',')
        province_ids = self.provinces.split(',')
        template_cities = []
        if self.cities:
            template_cities = mall_models.City.select().dj_where(id__in=city_ids)
        template_provinces = []
        if self.provinces:
            template_provinces = mall_models.Province.select().dj_where(id__in=province_ids)
        id2province = dict([(p.id, p) for p in template_provinces])

        provinces = []
        zone_names = []
        for id in sorted(id2province.keys()):
            province_has_city = {
                'provinceId': id,
                'provinceName': id2province[id].name,
                'zoneName': PROVINCE_ID2ZONE[id],
                'cities': []
            }
            province_has_city = self.__rename_zone(province_has_city)
            for city in filter(lambda city: city.province_id == id, template_cities):
                province_has_city['cities'].append({
                    'cityId': city.id,
                    'cityName': city.name
                })
            provinces.append(province_has_city)

        return provinces
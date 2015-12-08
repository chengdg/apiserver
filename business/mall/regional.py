# -*- coding: utf-8 -*-
"""@package business.mall.regional
用于填写收货地址时获取地区信息

"""

from business import model as business_model
from db.mall import models as mall_models


class Regional(business_model.Model):
	"""用于填写收货地址时获取地区信息
	"""

	def get_all_provinces(self):
		provinces = {}
		for province in mall_models.Province.select():
			provinces[province.id] = province.name
		return provinces

	def get_cities_for_province(self, province_id):
		cities = {}
		for city in mall_models.City.select().dj_where(province_id=province_id):
			cities[city.id] = city.name
		return cities

	def get_districts_for_city(self, city_id):
		districts = {}
		for district in mall_models.District.select().dj_where(city_id=city_id):
			districts[district.id] = district.name
		return districts

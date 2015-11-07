# -*- coding: utf-8 -*-

from wapi.mall import models as mall_models

def _get_all_provinces():
	provinces = {}
	for province in mall_models.Province.objects.all():
		provinces[province.id] = province.name
	return provinces

def _get_cities_for_province(province_id):
	cities = {}
	for city in mall_models.City.objects.filter(province_id=province_id):
		cities[city.id] = city.name
	return cities

def _get_districts_for_city(city_id):
	districts = {}
	for district in District.objects.filter(city_id=city_id):
		districts[district.id] =district.name
	return districts


def get_str_value_by_string_ids(str_ids):
	if str_ids != '' and str_ids:
		#cache = get_cache('mem')
		#ship_address = cache.get(str_ids)
		#TODO: 重新加入缓存
		ship_address = None
		if not ship_address:
			area_args = str_ids.split('_')
			ship_address = ''
			curren_area = ''
			for index, area in enumerate(area_args):

				if index == 0:
					curren_area = Province.objects.get(id=int(area))
				elif index == 1:
					curren_area = City.objects.get(id=int(area))
				elif index == 2:
					curren_area = District.objects.get(id=int(area))
				ship_address =  ship_address + ' ' + curren_area.name
			#cache.set(str_ids, ship_address)
		return u'{}'.format(ship_address.strip())
	else:
		return None


def get_str_value_by_string_ids_(str_ids):
	if str_ids:
		cache = get_cache('area')

		provinces = cache.get('province')
		if not province:
			cache.set('province', Province.objects.all())
		cities = cache.get('cite')
		if not cite:
			cache.set('cite', City.objects.all())
		districts = cache.get('district')
		if not district:
			cache.set('district', objects.all())

		str_ids_list = str_ids.split("_")
		return u''.join((filter(lambda x: x==str_ids_list[0], provinces) +
				filter(lambda x: x==str_ids_list[1], cities) +
				filter(lambda x: x==str_ids_list[2], district)))
	else:
		raise Exception("order ship area should not be null")


try:
	ID2PROVINCE = dict([(p.id, p.name) for p in Province.objects.all()])
	ID2CITY = dict([(c.id, c.name) for c in City.objects.all()])
	ID2DISTRICT = dict([(d.id, d.name) for d in District.objects.all()])
except:
	pass

def get_str_value_by_string_ids_new(str_ids):
	if str_ids != '' and str_ids:
		area_args = str_ids.split('_')
		ship_address = ''
		curren_area = ''
		for index, area in enumerate(area_args):
			if index == 0:
				curren_area = ID2PROVINCE.get(int(area))
			elif index == 1:
				curren_area = ID2CITY.get(int(area))
			elif index == 2:
				curren_area = ID2DISTRICT.get(int(area))
			ship_address =  ship_address + ' ' + curren_area
		return u'{}'.format(ship_address.strip())
	else:
		return None

# -*- coding: utf-8 -*-

from db.mall import models as mall_models

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
					curren_area = mall_models.Province.get(id=int(area))
				elif index == 1:
					curren_area = mall_models.City.get(id=int(area))
				elif index == 2:
					curren_area = mall_models.District.get(id=int(area))
				ship_address =  ship_address + ' ' + curren_area.name
			#cache.set(str_ids, ship_address)
		return u'{}'.format(ship_address.strip())
	else:
		return None

try:
	ID2PROVINCE = dict([(p.id, p.name) for p in mall_models.Province.objects.all()])
	ID2CITY = dict([(c.id, c.name) for c in mall_models.City.objects.all()])
	ID2DISTRICT = dict([(d.id, d.name) for d in mall_models.District.objects.all()])
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


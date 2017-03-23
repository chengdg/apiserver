# -*- coding: utf-8 -*-
"""
商品规格生成器
"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from eaglet.decorator import param_required
#from wapi import wapi_utils
from eaglet.core.cache import utils as cache_util
from db.mall import models as mall_models
from db.mall import promotion_models
from eaglet.core import watchdog
from business import model as business_model
import settings
from business.mall.product_model import ProductModel


class ProductModelGenerator(business_model.Model):
	"""
	商品规格生成器
	"""
	__slots__ = ()

	@staticmethod
	@param_required(['webapp_owner'])
	def get(args):
		return ProductModelGenerator(args['webapp_owner'])

	def __init__(self, webapp_owner):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner

	def __get_all_model_property_info(self, webapp_owner_id, is_enable_model_property_info):
		"""
		获取系统中所有的商品规格属性信息

		@param[in] is_enable_model_property_info: 是否启用商品规格属性信息

		@return
			id2property <id, property>映射
			id2propertyvalue <id, property_value>映射
		"""
		if not is_enable_model_property_info:
			return {}, {}
		# 兼容微众商城老数据
		# if webapp_owner_id == 216 or webapp_owner_id == 119:
		properties = list(mall_models.ProductModelProperty.select())
		# else:
		# 	properties = list(mall_models.ProductModelProperty.select().dj_where(owner_id=webapp_owner_id))
		property_ids = [property.id for property in properties]
		id2property = dict([(str(property.id), property)
						   for property in properties])
		# # 兼容商品池
		# mall_type = self.context['webapp_owner'].mall_type
		# if mall_type:
		# 	pool_weapp_account = mall_models.UserProfile.select().dj_where(webapp_type=2).first()
		# 	if pool_weapp_account:
		# 		pool_properties = mall_models.ProductModelProperty.select().dj_where(owner_id=pool_weapp_account.user_id)
		# 		property_ids += [pool_property.id for pool_property in pool_properties]
		# 		id2property.update(dict([(str(property.id), property)
		# 								 for property in pool_properties]))
		id2propertyvalue = {}
		for value in mall_models.ProductModelPropertyValue.select().dj_where(property__in=property_ids):
			id = '%d:%d' % (value.property_id, value.id)
			id2propertyvalue[id] = value

		_id2property = {}
		_id2propertyvalue = {}
		if is_enable_model_property_info:
			for id, property in id2property.items():
				_id2property[id] = {
					"id": property.id,
					"name": property.name,
					"values": []
				}

			for id, value in id2propertyvalue.items():
				_property_id, _value_id = id.split(':')
				_property = _id2property[_property_id]
				data = {
					'propertyId': _property['id'],
					'propertyName': _property['name'],
					"id": value.id,
					"name": value.name,
					"image": value.pic_url
				}
				_id2propertyvalue[id] = data
				_property['values'].append(data)

		return _id2property, _id2propertyvalue

	def fill_models_for_products(self, products, is_enable_model_property_info):
		"""
		为商品集合填充规格信息

		@param[in, out] products: 待填充规格信息的商品集合，填充后，product将获得models, used_system_model_properties, is_use_custom_model三个属性
		@param[in] is_enable_model_property_info: 是否为model填充与model相关的系统商品规格信息
		"""
		webapp_owner = self.context['webapp_owner']

		id2product = dict()
		product_ids = list()
		for product in products:
			id2product[product.id] = product
			product_ids.append(product.id)

		id2property, id2propertyvalue = self.__get_all_model_property_info(webapp_owner.id, is_enable_model_property_info)

		# 获取所有models
		product2models = {}

		product2deleted_models = {}
		for db_model in mall_models.ProductModel.select().dj_where(product_id__in=product_ids):
			if db_model.is_deleted:
				product_model = ProductModel(db_model, id2property, id2propertyvalue)
				product2deleted_models.setdefault(db_model.product_id, []).append(product_model)
			else:
				product_model = ProductModel(db_model, id2property, id2propertyvalue)
				product2models.setdefault(db_model.product_id, []).append(product_model)

		for product_id, product_models in product2models.items():
			product = id2product[product_id]
			if len(product_models) == 1 and product_models[0].name == 'standard':
				product.is_use_custom_model = False
			else:
				product.is_use_custom_model = True

			product.models = product_models

			self.__fill_used_product_model_property(product)


	def __fill_used_product_model_property(self, product):
		"""
		填充商品中使用了的商品规格属性的信息

		从models中构建used_system_model_properties，
		加入商品有以下两个规格
		1. {property:'颜色', value:'红色'}, {property:'尺寸', value:'M'}
		2. {property:'颜色', value:'黄色'}, {property:'尺寸', value:'M'}

		则合并后的used_system_model_properties为:
		[{
			property: '颜色',
			values: ['红色', '黄色']
		}, {
			property: '尺寸',
			values: ['M']
		}]
		"""
		id2property = {}
		if product.is_use_custom_model:
			for model in product.models:
				if not model:
					continue

				if model.name == 'standard':
					continue

				if model.property_values:
					for model_property_value in model.property_values:
						model_property_value['type'] = 'product_model_property_value'
						property_id = model_property_value['propertyId']

						property_info = id2property.get(property_id, None)
						if property_info:
							#model_property_value可能会有重复
							if not model_property_value['id'] in property_info['added_value_set']:
								property_info['values'].append(model_property_value)
								property_info['added_value_set'].add(model_property_value['id'])
						else:
							added_value_set = set()
							added_value_set.add(model_property_value['id'])
							property_info = {
								"type": "product_model_property",
								"id": property_id,
								"name": model_property_value['propertyName'],
								"added_value_set": added_value_set,
								"values": [model_property_value]
							}
							id2property[property_id] = property_info

			#获得properties，并进行必要的排序
			properties = id2property.values()
			for property in properties:
				del property['added_value_set']
				property['values'].sort(lambda x,y: cmp(x['id'], y['id']))
			properties.sort(lambda x,y: cmp(x['id'], y['id']))
			product.used_system_model_properties = properties

		else:
			product.used_system_model_properties = None

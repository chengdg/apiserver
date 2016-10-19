# -*- coding: utf-8 -*-
"""@package business.mall.mall_data
业务层内部使用的业务对象，商城配置数据，从redis中获取相应数据

MallData业务对象统一了存放在redis中的postage_configs, mall_config, product_model_properties三种数据
其中

postage_config在redis中的数据为:
```javascript

```

mall_config在redis中的数据为:
```javascript
{
	"max_product_count": 100, 
	"is_enable_bill": false, 
	"created_at": [], 
	"order_expired_day": 0, 
	"owner": 3, 
	"id": 2
}
```

product_model_properties在redis中的数据为:
```javascript
{
 "id2property": {
  "1": {
   "id": 1, 
   "name": "\u989c\u8272"
  }, 
  "2": {
   "id": 2, 
   "name": "\u5c3a\u5bf8"
  }
 }, 
 "id2value": {
  "1": {
   "name": "\u7ea2\u8272", 
   "pic_url": "/standard_static/test_resource_img/icon_color/icon_1.png", 
   "property_id": 1, 
   "id": 1
  }, 
  ......
 }
}
```

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
from db.account import models as account_models
#import resource
from eaglet.core import watchdog
from business import model as business_model
import settings


class MallData(business_model.Model):
	"""
	商城配置数据
	"""
	__slots__ = (
		'postage_configs',
		'mall_config',
		'product_model_properties'
	)

	@staticmethod
	@param_required(['woid'])
	def get(args):
		mall_data = MallData(args['woid'])
		return mall_data

	def __init__(self, woid):
		business_model.Model.__init__(self)
		self.__get_from_cache(woid)

	def __get_mall_config_for_cache(self, webapp_owner_id):
		"""
		从数据库中获取MallConfig Model
		"""
		def inner_func():
			#update by bert at 20151014  for new account can't vs webapp
			try:
				mall_config = mall_models.MallConfig.get(owner=webapp_owner_id)
			except:
				mall_config = mall_models.MallConfig.create(owner=webapp_owner_id)
			return {
				'value': mall_config.to_dict()
			}

		return inner_func

	def __get_postage_configs_for_cache(self, webapp_owner_id):
		"""
		从数据库中获取PostageConfig集合
		"""
		def inner_func():
			postage_configs = mall_models.PostageConfig.select().dj_where(owner_id=webapp_owner_id)

			values = []
			for postage_config in postage_configs:
				factor = {
					'firstWeight': postage_config.first_weight,
					'firstWeightPrice': postage_config.first_weight_price,
					'isEnableAddedWeight': postage_config.is_enable_added_weight,
				}

				#if postage_config.is_enable_added_weight:
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
				postage_config_dict = postage_config.to_dict('factor')

				try:
					del postage_config_dict['created_at']
				except:
					pass
				values.append(postage_config_dict)

			return {
				'value': values
			}

		return inner_func

	def __get_product_model_properties_for_cache(self, webapp_owner_id):
		"""
		从数据库中获取商品规格信息
		"""
		def inner_func():
			properties = []
			user_profile = account_models.UserProfile.select().dj_where(user_id=webapp_owner_id)
			#duhao 20151221注释，去掉微众商城相关业务
			# if user_profile.count() == 1 and mall_models.WeizoomMall.select().dj_where(webapp_id=user_profile[0].webapp_id, is_active=True).count() == 1:
			# 	properties = list(mall_models.ProductModelProperty.select().dj_where())
			# else:
			# 	properties = list(mall_models.ProductModelProperty.select().dj_where(owner_id=webapp_owner_id))
			properties = list(mall_models.ProductModelProperty.select().dj_where(owner_id=webapp_owner_id))
			id2property = {}
			property_ids = []
			for property in properties:
				id2property[property.id] = {"id":property.id, "name":property.name}
				property_ids.append(property.id)

			id2value = {}
			for property_value in mall_models.ProductModelPropertyValue.select().dj_where(property_id__in=property_ids):
				id2value[property_value.id] = {"id":property_value.id, "property_id":property_value.property_id, "name":property_value.name, "pic_url":property_value.pic_url}

			return {
				'value': {
					'id2property': id2property,
					'id2value': id2value
				}
			}

		return inner_func

	def __get_from_cache(self, webapp_owner_id):
		'''
		方便外部使用缓存的接口
		'''
		mall_config_key = 'webapp_mall_config_{wo:%s}' % webapp_owner_id
		postage_configs_key = 'webapp_postage_configs_{wo:%s}' % webapp_owner_id
		product_model_properties_key = 'webapp_product_model_properties_{wo:%s}' % webapp_owner_id
		key_infos = [{
			'key': mall_config_key,
			'on_miss': self.__get_mall_config_for_cache(webapp_owner_id)
		}, {
			'key': postage_configs_key,
			'on_miss': self.__get_postage_configs_for_cache(webapp_owner_id)
		}, {
			'key': product_model_properties_key,
			'on_miss': self.__get_product_model_properties_for_cache(webapp_owner_id)
		}]
		data = cache_util.get_many_from_cache(key_infos)

		# return {
		# 	'postage_configs': mall_models.PostageConfig.from_list(data[postage_configs_key]),
		# 	'product_model_properties': data[product_model_properties_key],
		# 	'mall_config': mall_models.MallConfig.from_dict(data[mall_config_key])
		# }
		self.postage_configs = data[postage_configs_key]
		self.product_model_properties = data[product_model_properties_key]
		self.mall_config = data[mall_config_key]






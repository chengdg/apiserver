# -*- coding: utf-8 -*-

import json

from bs4 import BeautifulSoup

from core import inner_resource
from wapi.decorators import param_required
from wapi import wapi_utils
from cache import utils as cache_util
from wapi.mall import models as mall_models
from wapi.mall import promotion_models
from wapi.user import models as account_models
from wapi.user import weixin_models as weixin_user_models
from wapi.user import webapp_models as webapp_models
from wapi.member import models as member_models
import settings
from core.watchdog.utils import watchdog_alert, watchdog_warning, watchdog_error
from core.exceptionutil import unicode_full_stack


class RMallData(inner_resource.Resource):
	"""
	商品详情
	"""
	app = 'account'
	resource = 'mall_data'

	@staticmethod
	def get_mall_config_for_cache(webapp_owner_id):
		"""
		module_api:get_mall_config_for_cache
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

	@staticmethod
	def get_postage_configs_for_cache(webapp_owner_id):
		"""
		module_api:get_postage_configs_for_cache
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
							'firstWeight': postage_config.first_weight,
							'firstWeightPrice': special_config.first_weight_price,
							'addedWeight': float(postage_config.added_weight),
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
				values.append(postage_config.to_dict('factor'))

			return {
				'value': values
			}

		return inner_func

	@staticmethod
	def get_product_model_properties_for_cache(webapp_owner_id):
		"""
		module_api:get_product_model_properties_for_cache
		"""
		def inner_func():
			properties = []
			user_profile = account_models.UserProfile.select().dj_where(user_id=webapp_owner_id)
			if user_profile.count() == 1 and mall_models.WeizoomMall.select().dj_where(webapp_id=user_profile[0].webapp_id, is_active=True).count() == 1:
				properties = list(mall_models.ProductModelProperty.select().dj_where())
			else:
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

	@staticmethod
	def get_from_cache(webapp_owner_id):
		'''
		方便外部使用缓存的接口
		'''
		mall_config_key = 'webapp_mall_config_{wo:%s}' % webapp_owner_id
		postage_configs_key = 'webapp_postage_configs_{wo:%s}' % webapp_owner_id
		product_model_properties_key = 'webapp_product_model_properties_{wo:%s}' % webapp_owner_id
		key_infos = [{
			'key': mall_config_key,
			'on_miss': RMallData.get_mall_config_for_cache(webapp_owner_id)
		}, {
			'key': postage_configs_key,
			'on_miss': RMallData.get_postage_configs_for_cache(webapp_owner_id)
		}, {
			'key': product_model_properties_key,
			'on_miss': RMallData.get_product_model_properties_for_cache(webapp_owner_id)
		}]
		data = cache_util.get_many_from_cache(key_infos)

		return {
			'postage_configs': mall_models.PostageConfig.from_list(data[postage_configs_key]),
			'product_model_properties': data[product_model_properties_key],
			'mall_config': mall_models.MallConfig.from_dict(data[mall_config_key])
		}

	@param_required(['woid'])
	def get(args):
		data = RMallData.get_from_cache(args['woid'])
		return data

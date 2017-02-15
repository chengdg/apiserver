# -*- coding: utf-8 -*-
"""@package business.mall.product_model
商品规格
"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from eaglet.decorator import param_required
#from wapi import wapi_utils
from eaglet.core.cache import utils as cache_util
from db.mall import models as mall_models
from db.account import models as account_models
from db.mall import promotion_models
from eaglet.core import watchdog
from business import model as business_model
import settings
from business.mall.promotion.cps_promote_detail import CPSPromotionDetail
from business.mall.product_customized_price import ProductCustomizedPrice


class ProductModel(business_model.Model):
	"""
	商品
	"""
	__slots__ = (
		'id',
		'is_deleted',
		'product_id',
		'name',
		'weight',
		'price',
		'purchase_price',
		'original_price',
		'market_price',
		'user_code',
		'stock_type',
		'stocks',

		'property_values',
		'property2value',
		'gross_profit',
		'gross_profit_rate',
		'webapp_purchase_price',
	)

	def __init__(self, db_model=None, id2property=None, id2propertyvalue=None, webapp_owner=None):
		business_model.Model.__init__(self)

		if db_model:
			self._init_slot_from_model(db_model)
			self.original_price = db_model.price
			self.stocks = db_model.stocks if db_model.stock_type == mall_models.PRODUCT_STOCK_TYPE_LIMIT else u'无限'

			self.__fill_model_property_info(id2property, id2propertyvalue)
			self.__fill_account_divide_info(webapp_owner=webapp_owner)

	def __fill_model_property_info(self, id2property, id2propertyvalue):
		'''
		获取model关联的property信息
			model.property_values = [{
				'propertyId': 1,
				'propertyName': '颜色',
				'id': 1,
				'value': '红'
			}, {
				'propertyId': 2,
				'propertyName': '尺寸',
				'id': 3,
				'value': 'S'
			}]

			model.property2value = {
				'颜色': '红',
				'尺寸': 'S'
			}
		'''
		if not id2property:
			return

		if self.name == 'standard':
			self.property2value = None
			self.property_values = None
			return

		#商品规格名的格式为${property1_id}:${value1_id}_${property2_id}:${value2_id}
		ids = self.name.split('_')
		property_values = []
		property2value = {}
		for id in ids:
			# id的格式为${property_id}:${value_id}
			_property_id, _value_id = id.split(':')
			_property = id2property[_property_id]
			_value = id2propertyvalue[id]
			property2value[_property['name']] = {
				'id': _value['id'],
				'name': _value['name']
			}
			a_image = _value['image'] if _value['image'] else ''
			property_values.append({
				'propertyId': _property['id'],
				'propertyName': _property['name'],
				'id': _value['id'],
				'name': _value['name'],
				'image': '%s%s' % (settings.IMAGE_HOST, a_image) if a_image and a_image.find('http') == -1 else a_image
			})

		self.property_values = property_values
		self.property2value = property2value
		
	def __fill_account_divide_info(self, webapp_owner):
		"""
		社群的毛利、毛利率
		固定底价: 社群修改价 - 上浮结算价
		固定扣点: 商品售价 * 社群扣点
		毛利分成: {
			cps: 商品结算价 - 推广费,
			non_cps: (商品售价 - 微众售价) * 社群毛利点  ==> 社群毛利,
					 (商品售价 - 微众售价)/商品售价 * 社群毛利点 ==>社群毛利率
		}
	
		"""
		divide_info = webapp_owner.account_divide_info
		settlement_type = int(divide_info.settlement_type)
		divide_rebate = divide_info.divide_rebate
		
		if settlement_type == account_models.ACCOUNT_DIVIDE_TYPE_FIXED:
			# 固定底价
			# 目前暂时不考虑这个,只是把weapp的算法逻辑挪过来,
			customized_price_info = ProductCustomizedPrice.from_product_info(product_id=self.product_id,
																			 product_model_id=self.id,
																			 webapp_owner=webapp_owner)
			if customized_price_info:
				customized_price = customized_price_info.price
				gross_profit = customized_price - self.price
				gross_profit_rate = gross_profit / customized_price * 100
			else:
				gross_profit = 0
				gross_profit_rate = 0
		elif settlement_type == account_models.ACCOUNT_DIVIDE_TYPE_RETAIL:  # 固定扣点
			gross_profit = self.price * divide_rebate / 100
			gross_profit_rate = divide_rebate
		elif settlement_type == account_models.ACCOUNT_DIVIDE_TYPE_PROFIT:  # 毛利分成
			product_id = self.product_id
			cps_promotion_info = CPSPromotionDetail(None).get_promoting_detail_by_product_id(product_id=product_id)
			if cps_promotion_info:
				# cps 推广
				gross_profit = cps_promotion_info.promote_money * divide_rebate / 10000
				gross_profit_rate = float(gross_profit) / float(self.price) * 100
			else:
				gross_profit = (self.price - self.purchase_price) * divide_rebate / 100
				gross_profit_rate = (gross_profit / self.price) * 100 if self.price != 0 else 0
		else:
			gross_profit = 0
			gross_profit_rate = 0
		self.gross_profit_rate = '%.2f' % gross_profit_rate
		self.gross_profit = '%.2f' % gross_profit
		self.webapp_purchase_price = '%.2f' % (float(self.price) * (1 - gross_profit_rate / 100))

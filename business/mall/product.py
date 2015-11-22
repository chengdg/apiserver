# -*- coding: utf-8 -*-
"""@package business.mall.product
商品

"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
from db.mall import promotion_models
from core.watchdog.utils import watchdog_alert
from business import model as business_model
import settings
from business.mall.forbidden_coupon_product_ids import ForbiddenCouponProductIds


class CachedProduct(object):
	"""
	缓存的Product
	"""

	@staticmethod
	def __get_from_db(webapp_owner_id, product_id, member_grade_id=None):
		"""
		从数据库中获取商品详情
		"""
		def inner_func():
			try:
				#获取product及其model
				product_model = mall_models.Product.get(id = product_id)
				if product_model.owner_id != webapp_owner_id:
					pass
					# product.postage_id = -1
					# product.unified_postage_money = 0
					# product.postage_type = mall_models.POSTAGE_TYPE_UNIFIED
				
				#product.created_at = product.created_at.strftime("%Y-%m-%d %H:%M:%S")

				product = Product.from_model({
					'webapp_owner': CachedProduct.webapp_owner, 
					'model': product_model, 
					'fill_options': {
						"with_price": True,
						"with_product_model": True,
						"with_model_property_info": True,
						"with_image": True,
						"with_property": True,
						"with_product_promotion": True
					}
				})

				#获取商品的评论
				#TODO: 恢复获取评论的逻辑
				# product_review = ProductReview.objects.filter(
				# 							Q(product_id=product.id) &
				# 							Q(status__in=['1', '2'])
				# 				).order_by('-top_time', '-id')[:2]
				# product.product_review = product_review
				#
				# if product_review:
				# 	member_ids = [review.member_id for review in product_review]
				# 	members = get_member_by_id_list(member_ids)
				# 	member_id2member = dict([(m.id, m) for m in members])
				# 	for review in product_review:
				# 		if member_id2member.has_key(review.member_id):
				# 			review.member_name = member_id2member[review.member_id].username_for_html
				# 			review.user_icon = member_id2member[review.member_id].user_icon
				# 		else:
				# 			review.member_name = '*'
			except:
				if settings.DEBUG:
					raise
				else:
					#记录日志
					alert_message = u"获取商品记录失败,商品id: {} cause:\n{}".format(product_id, unicode_full_stack())
					watchdog_alert(alert_message, type='WEB')
					#返回"被删除"商品
					product = Product()
					product.is_deleted = True

			data = product.to_dict()

			return {'value': data}

		return inner_func

	@staticmethod
	def __get_from_cache(woid, product_id, member_grade_id=None):
		"""
		@see webapp_cache.get_webapp_product_detail
		"""
		key = 'webapp_product_detail_{wo:%s}_{pid:%s}' % (woid, product_id)
		data = cache_util.get_from_cache(key, CachedProduct.__get_from_db(woid, product_id))

		product = Product.from_dict(data)
		product.context['webapp_owner'] = CachedProduct.webapp_owner

		# Set member's discount of the product
		if hasattr(product, 'integral_sale') and product.integral_sale \
			and product.integral_sale['detail'].get('rules', None):
			for i in product.integral_sale['detail']['rules']:
				if i['member_grade_id'] == member_grade_id:
					product.integral_sale['detail']['discount'] = str(i['discount'])+"%"
					break

		promotion_data = data.get('promotion', None)
		if promotion_data and len(promotion_data) > 0:
		    product.promotion_model = promotion_models.Promotion.from_dict(promotion_data)
		else:
		    product.promotion_model = None
		product.promotion_dict = dict()

		integral_sale_data = data.get('integral_sale', None)
		if integral_sale_data and len(integral_sale_data) > 0:
		    product.integral_sale_model = promotion_models.Promotion.from_dict(
		        integral_sale_data)
		else:
		    product.integral_sale_model = None
		product.original_promotion_title = data['promotion_title']

		return product

	@staticmethod
	@param_required(['webapp_owner', 'member', 'product_id'])
	def get(args):
		#TODO2: 临时解决方案，后续去除
		CachedProduct.webapp_owner = args['webapp_owner']
		webapp_owner_id = args['webapp_owner'].id
		product_id = args['product_id']
		member = args['member']
		member_grade_id = member.grade_id if member else None

		try:
			product = CachedProduct.__get_from_cache(webapp_owner_id, product_id, member_grade_id)

			if product.is_deleted:
				return product

			for product_model in product.models:
				#获取折扣后的价格
				if webapp_owner_id != product.owner_id and product.weshop_sync == 2:
					product_model['price'] = round(product_model['price'] * 1.1, 2)

			# 商品规格

			#获取product的price info
			#TODO: 这部分是否可以缓存起来？
			if product.is_use_custom_model:
				custom_models = product.models[1:]
				if len(custom_models) == 1:
					#只有一个custom model，显示custom model的价格信息
					product_model = custom_models[0]
					product.price_info = {
						'display_price': str("%.2f" % product_model['price']),
						'display_original_price': str("%.2f" % product_model['original_price']),
						'display_market_price': str("%.2f" % product_model['market_price']),
						'min_price': product_model['price'],
						'max_price': product_model['price'],
					}
				else:
					#有多个custom model，显示custom model集合组合后的价格信息
					prices = []
					market_prices = []
					for product_model in custom_models:
						if product_model['price'] > 0:
							prices.append(product_model['price'])
						if product_model['market_price'] > 0:
							market_prices.append(product_model['market_price'])

					if len(market_prices) == 0:
						market_prices.append(0.0)

					if len(prices) == 0:
						prices.append(0.0)

					prices.sort()
					market_prices.sort()
					# 如果最大价格和最小价格相同，价格处显示一个价格。
					if prices[0] == prices[-1]:
						price_range =  str("%.2f" % prices[0])
					else:
						price_range = '%s-%s' % (str("%.2f" % prices[0]), str("%.2f" % prices[-1]))

					if market_prices[0] == market_prices[-1]:
						market_price_range = str("%.2f" % market_prices[0])
					else:
						market_price_range = '%s-%s' % (str("%.2f" % market_prices[0]), str("%.2f" % market_prices[-1]))

					# 最低价
					min_price = prices[0]
					# 最高价
					max_price = prices[-1]

					product.price_info = {
						'display_price': price_range,
						'display_original_price': price_range,
						'display_market_price': market_price_range,
						'min_price': min_price,
						'max_price': max_price,
					}
			else:
				standard_model = product.standard_model
				product.price_info = {
					'display_price': str("%.2f" % standard_model['price']),
					'display_original_price': str("%.2f" % standard_model['original_price']),
					'display_market_price': str("%.2f" % standard_model['market_price']),
					'min_price': standard_model['price'],
					'max_price': standard_model['price'],
				}
		except:
			if settings.DEBUG:
				raise
			else:
				#记录日志
				alert_message = u"获取商品记录失败,商品id: {} cause:\n{}".format(product_id, unicode_full_stack())
				watchdog_alert(alert_message, type='WEB')
				#返回"被删除"商品
				product = mall_modules.Product()
				product.is_deleted = True

		return product


class Product(business_model.Model):
	"""
	商品
	"""
	__slots__ = (
		'id',
		'owner_id',
		'type',
		'is_deleted',
		'name',
		'display_index',
		'is_member_product',
		'weshop_sync',
		'shelve_type',
		'shelve_start_time',
		'shelve_end_time',
		'detail',
		'_thumbnails_url',
		'order_thumbnails_url',
		'_pic_url',
		'swipe_images',
		'detail_link',
		'user_code',
		'bar_code',
		'min_limit',
		'categories',
		'properties',
		'created_at',

		#商品规格信息
		'is_use_custom_model',
		'model_name',
		'product_model_properties',
		'models',
		'custom_models',
		'standard_model',
		'current_used_model',
		'system_model_properties',

		#价格、销售信息
		'stock_type',
		'stocks',
		'total_stocks',
		'display_price',
		'display_price_range',
		'purchase_price',
		'price_info',
		'sales',
		'is_sellout',
		'postage_id',
		'postage_type',
		
		#促销信息
		'promotion',
		'promotion_title',
		'original_promotion_title', #需要去除，统一到promotion_title
		'product_review',
		'promotion_model', #需要去除，统一到promotion
		'promotion_dict', #需要去除，统一到promotion
		'integral_sale_model', #需要去除，统一到promotion
	)

	@staticmethod
	def from_models(query):
		1/0

	@staticmethod
	@param_required(['webapp_owner', 'model', 'fill_options'])
	def from_model(args):
		webapp_owner = args['webapp_owner']
		model = args['model']
		fill_options = args.get('fill_options', {})

		product = Product(model)
		Product.__fill_details(webapp_owner.id, [product], fill_options)
		product.__set_image_to_lazy_load()
		product.context['webapp_owner'] = webapp_owner

		return product

	@staticmethod
	@param_required(['webapp_owner', 'member', 'product_id'])
	def from_id(args):
		return CachedProduct.get(args)

	@staticmethod
	@param_required(['webapp_owner', 'member', 'product_ids'])
	def from_ids(args):
		"""从product_ids集合构造Product对象集合

		@return Product对象集合
		"""
		return [Product.from_id(product_id) for product_id in args['product_ids']]

	def __init__(self, model=None):
		business_model.Model.__init__(self)
		self.promotion = None

		if model:
			self._init_slot_from_model(model)
			self.owner_id = model.owner_id
			self.thumbnails_url = '%s%s' % (settings.IMAGE_HOST, model.thumbnails_url)
			self.pic_url = '%s%s' % (settings.IMAGE_HOST, model.pic_url)

	def __set_image_to_lazy_load(self):
		# 商品详情图片lazyload
		# TODO: 将这个逻辑改成字符串处理，不用xml解析
		soup = BeautifulSoup(self.detail)
		for img in soup.find_all('img'):
			try:
				img['data-url'] = img['src']
				del img['src']
				del img['title']
			except:
				pass
		self.detail = str(soup)

	@property
	def is_sellout(self):
		"""
		是否卖光
		"""
		return self.total_stocks <= 0

	@is_sellout.setter
	def is_sellout(self, value):
		pass

	@property
	def total_stocks(self):
		context = self.context
		if not 'total_stocks' in context:
			context['total_stocks'] = 0
			if self.is_use_custom_model:
				models = self.custom_models
			else:
				models = self.models

			if len(models) == 0:
				context['total_stocks'] = 0
				return context['total_stocks']
			is_dict = (type(models[0]) == dict)

			for model in models:
				stock_type = model['stock_type'] if is_dict else model.stock_type
				stocks = model['stocks'] if is_dict else model.stocks
				if stock_type == mall_models.PRODUCT_STOCK_TYPE_UNLIMIT:
					context['total_stocks'] = u'无限'
					return context['total_stocks']
				else:
					context['total_stocks'] = context['total_stocks'] + stocks
		return context['total_stocks']

	@total_stocks.setter
	def total_stocks(self, value):
		self.context['total_stocks'] = value

	@property
	def is_use_custom_model(self):
		context = self.context
		if not 'is_use_custom_model' in context:
			context['is_use_custom_model'] = (
				mall_models.ProductModel.select().dj_where(product=self.id, is_standard=False, is_deleted=False).count() > 0)  # 是否使用定制规格
		return context['is_use_custom_model']

	@is_use_custom_model.setter
	def is_use_custom_model(self, value):
		self.context['is_use_custom_model'] = value

	# 如果规格有图片就显示，如果没有，使用缩略图
	@property
	def order_thumbnails_url(self):
		'''
		if hasattr(self, 'custom_model_properties') and self.custom_model_properties:
			for model in self.custom_model_properties:
				if model['property_pic_url']:
					return model['property_pic_url']
		'''
		context = self.context
		if not 'order_thumbnails_url' in context:
			context['order_thumbnails_url'] = self.thumbnails_url
		return context['order_thumbnails_url']

	@order_thumbnails_url.setter
	def order_thumbnails_url(self, url):
		self.context['order_thumbnails_url'] = url

	@property
	def hint(self):
		"""
		判断商品是否被禁止使用全场优惠券
		"""
		webapp_owner = self.context['webapp_owner']
		forbidden_coupon_product_ids = ForbiddenCouponProductIds.get_for_webapp_owner({
			'webapp_owner': webapp_owner
		}).ids
		if self.id in forbidden_coupon_product_ids:
			return u'该商品不参与全场优惠券使用！'
		else:
			return u''

	def is_on_shelve(self):
		"""
		判断商品是否是商家状态
		"""
		return self.shelve_type == mall_models.PRODUCT_SHELVE_TYPE_ON

	def get_specific_model(self, model_name):
		"""
		获得特定的商品规格信息

		@param [in] model_name: 商品规格名

		@return dict形式的商品规格信息
		```
		{
			"price": 1.0,
			"weight": 1.0,
		}
		```
		"""
		models = self.models

		candidate_models = filter(lambda m: m['name'] == model_name, models)
		if len(candidate_models) > 0:
			model = candidate_models[0]
			return model
		else:
			return None

	def fill_specific_model(self, model_name, models=None):
		if not models:
			models = self.models

		candidate_models = filter(lambda m: m['name'] == model_name, models)
		if len(candidate_models) > 0:
			model = candidate_models[0]
			product = self
			product.price = model['price']
			product.weight = model['weight']
			product.stock_type = model['stock_type']
			if not hasattr(product, 'min_limit'):
				product.min_limit = product.stocks
			product.stocks = model['stocks']
			product.model_name = model_name
			product.model = model
			product.is_model_deleted = False
			product.market_price = model.get('market_price', 0.0)

			if model_name == 'standard':
				product.custom_model_properties = None
			else:
				product.custom_model_properties = [{'property_value': property_value['name']} for property_value in model['property_values']]

	# def fill_standard_model(self):
	# 	"""
	# 	填充标准商品规格信息
	# 	"""
	# 	try:
	# 		product_model = ProductModel.get(product=self.id, is_standard=True)

	# 		self.price = product_model.price
	# 		self.weight = product_model.weight
	# 		self.stock_type = product_model.stock_type
	# 		self.min_limit = self.stocks
	# 		self.stocks = product_model.stocks
	# 		self.market_price = product_model.market_price
	# 		return product_model
	# 	except:
	# 		if settings.DEBUG:
	# 			raise
	# 		else:
	# 			fatal_msg = u"商品填充标准规格信息错误，商品id:{}, cause:\n{}".format(self.id, unicode_full_stack())
	# 			watchdog_fatal(fatal_msg)

	# def fill_model(self, show_delete=False):
	# 	"""
	# 	填充所有商品规格信息
	# 	"""
	# 	standard_model = self.fill_standard_model()

	# 	if self.is_use_custom_model:
	# 		self.custom_models = ProductModel.select().dj_where(product=self.id, name__not='standard', is_deleted=show_delete)
	# 	else:
	# 		self.custom_models = []

	# 	self.models = []
	# 	self.models.append({
	# 		"id": standard_model.id,
	# 		"name": "standard",
	# 		"original_price": self.price,
	# 		"price": self.price,
	# 		"weight": self.weight,
	# 		"stock_type": self.stock_type,
	# 		"stocks": self.stocks,
	# 		"market_price": self.market_price,
	# 		"user_code": self.user_code
	# 	})

	# 	self.custom_properties = []
	# 	self.product_model_properties = []
	# 	recorded_model_property = set()  # 保存已记录的model property
	# 	if len(self.custom_models) > 0:
	# 		# 获取系统所有property
	# 		id2property = dict([(property.id, property) for property in ProductModelProperty.select().dj_where(owner=self.owner_id, is_deleted=False)])
	# 		properties = id2property.values()
	# 		properties.sort(lambda x, y: cmp(x.id, y.id))
	# 		for property in properties:
	# 			self.custom_properties.append({
	# 				"id": property.id,
	# 				"name": property.name
	# 			})
	# 		self.custom_properties_json_str = json.dumps(self.custom_properties)

	# 		property_ids = id2property.keys()
	# 		id2value = dict([(value.id, value) for value in ProductModelPropertyValue.select().dj_where(property_id__in=property_ids, is_deleted=False)])

	# 		# 获取系统所有<property, [values]>
	# 		id2property = {}
	# 		for property in properties:
	# 			id2property[
	# 				property.id] = {
	# 				"id": property.id,
	# 				"name": property.name,
	# 				"values": []}
	# 		stock_custom_model_names = []  # 无限库存或库存不为>0的custom_model_name集合
	# 		property_value_ids = []
	# 		for custom_model in self.custom_models:
	# 			if custom_model.stock_type == 0 or custom_model.stocks > 0:
	# 				stock_custom_model_names.append(str(custom_model.name))
	# 			for model_property_info in custom_model.name.split('_'):
	# 				property_id, property_value_id = model_property_info.split(':')
	# 				property_value_ids.append(int(property_value_id))
	# 		self.stock_custom_model_names = stock_custom_model_names

	# 		# 解决规格顺序错乱的BUG
	# 		values = id2value.values()
	# 		if values:
	# 			values.sort(lambda x, y: cmp(x.id, y.id))

	# 		for value in values:
	# 			# 增加该规格值是否属于该产品
	# 			is_belong_product = (value.id in property_value_ids)
	# 			id2property[value.property_id]['values'].append({
	# 				"id": value.id,
	# 				"name": value.name,
	# 				"image": value.pic_url,
	# 				"is_belong_product": is_belong_product
	# 			})
	# 		self.model_properties = id2property.values()
	# 		self.model_properties.sort(lambda x, y: cmp(x['id'], y['id']))

	# 		# 获取商品关联的所有的model和property
	# 		for custom_model in self.custom_models:
	# 			if custom_model.name == 'standard':
	# 				continue

	# 			model_dict = {
	# 				"id": custom_model.id,
	# 				"name": custom_model.name,
	# 				"original_price": custom_model.price,
	# 				"price": custom_model.price,
	# 				"weight": custom_model.weight,
	# 				"stock_type": custom_model.stock_type,
	# 				"stocks": custom_model.stocks,
	# 				"user_code": custom_model.user_code,
	# 				"market_price": custom_model.market_price
	# 			}

	# 			model_dict['property_values'] = []
	# 			try:
	# 				for model_property_info in custom_model.name.split('_'):
	# 					property_id, property_value_id = model_property_info.split(':')
	# 					if not id2value.has_key(int(property_value_id)):
	# 						continue
	# 					model_dict['property_values'].append({
	# 						"propertyId": property_id,
	# 						"propertyName": id2property[int(property_id)]['name'],
	# 						"id": property_value_id,
	# 						"name": id2value[int(property_value_id)].name
	# 					})

	# 					# 记录商品的model property
	# 					if not property_id in recorded_model_property:
	# 						model_property = id2property[int(property_id)]
	# 						self.product_model_properties.append(model_property)
	# 						recorded_model_property.add(property_id)

	# 				self.models.append(model_dict)
	# 			except:
	# 				fatal_msg = u"商品填充所有商品规格信息错误，商品id:{}, 错误的mall_product_model.id:{}, cause:\n{}".format(
	# 					self.id,
	# 					custom_model.id,
	# 					unicode_full_stack())
	# 				watchdog_fatal(fatal_msg)

	# 	self.models_json_str = json.dumps(self.models)
	# 	self.product_model_properties_json_str = json.dumps(self.product_model_properties)

	@staticmethod
	def __fill_display_price(products):
		"""根据商品规格，获取商品价格
		"""
		# 获取所有models
		product2models = {}
		product_ids = [product.id for product in products]
		for model in mall_models.ProductModel.select().dj_where(product__in=product_ids):
			if model.is_deleted:
				# model被删除，跳过
				continue

			product_id = model.product_id
			if product_id in product2models:
				models = product2models[product_id]
			else:
				models = {
					'standard_model': None,
					'custom_models': [],
					'is_use_custom_model': False
				}
				product2models[product_id] = models

			if model.name == 'standard':
				models['standard_model'] = model
			else:
				models['is_use_custom_model'] = True
				models['custom_models'].append(model)

		# 为每个product确定显示价格
		for product in products:
			product_id = product.id
			if product_id in product2models:
				models = product2models[product.id]
				if models['is_use_custom_model']:
					custom_models = models['custom_models']
					if len(custom_models) == 1:
						product.display_price = custom_models[0].price
					else:
						prices = sorted(
							[model.price
							 for model in custom_models])
						# 列表页部分显示商品的最小价格
						# add by liupeiyu at 19.0
						# product.display_price = '%s-%s' % (prices[0], prices[-1])
						product.display_price = prices[0]
				else:
					product.display_price = models['standard_model'].price
			else:
				product.display_price = product.price

	@staticmethod
	def __fill_model_detail(webapp_owner_id, products, product_ids, id2property={}, id2propertyvalue={}, is_enable_model_property_info=False):
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
					"image": value.pic_url,
					"is_belong_product": False
				}
				_id2propertyvalue[id] = data
				_property['values'].append(data)

		# 获取所有models
		product2models = {}
		for model in mall_models.ProductModel.select().dj_where(product_id__in=product_ids):
			if model.is_deleted:
				# model被删除，跳过
				continue

			model_dict = {
				"id": model.id,
				"name": model.name,
				"price": model.price,
				"original_price": model.price,
				"weight": model.weight,
				"stock_type": model.stock_type,
				"stocks": model.stocks if model.stock_type == mall_models.PRODUCT_STOCK_TYPE_LIMIT else u'无限',
				"user_code": model.user_code,
				"market_price": model.market_price
			}

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
			if is_enable_model_property_info and model.name != 'standard':
				ids = model.name.split('_')
				property_values = []
				property2value = {}
				for id in ids:
					# id的格式为${property_id}:${value_id}
					_property_id, _value_id = id.split(':')
					_property = _id2property[_property_id]
					_value = _id2propertyvalue[id]
					property2value[_property['name']] = {
						'id': _value['id'],
						'name': _value['name']
					}
					property_values.append({
						'propertyId': _property['id'],
						'propertyName': _property['name'],
						'id': _value['id'],
						'name': _value['name']
					})
					_value['is_belong_product'] = True
				model_dict['property_values'] = property_values
				model_dict['property2value'] = property2value

			product_id = model.product_id
			if product_id in product2models:
				models = product2models[product_id]
			else:
				models = {
					'standard_model': None,
					'custom_models': [],
					'is_use_custom_model': False}
				product2models[product_id] = models

			if model.name == 'standard':
				models['standard_model'] = model_dict
			else:
				models['is_use_custom_model'] = True
				models['custom_models'].append(model_dict)

		# 为每个product确定显示信息
		for product in products:
			product.sales = -1  # 实现sales逻辑
			product.system_model_properties = _id2property.values()
			product_id = product.id
			if product_id in product2models:
				models = product2models[product.id]
				product.models = [models['standard_model']]
				if models['is_use_custom_model']:
					product.is_use_custom_model = True
					product.custom_models = models['custom_models']
					product.standard_model = models['standard_model']
					custom_models = models['custom_models']
					product.models.extend(custom_models)
					if len(custom_models) == 1:
						target_model = custom_models[0]
						display_price_range = target_model['price']
					else:
						# 列表页部分显示商品的最小价格那个model的信息
						custom_models.sort(lambda x, y: cmp(x['price'], y['price']))
						target_model = custom_models[0]
						low_price = target_model['price']
						high_price = custom_models[-1]['price']
						if low_price == high_price:
							display_price_range = low_price
						else:
							display_price_range = '%s ~ %s' % (low_price, high_price)
				else:
					product.is_use_custom_model = False
					target_model = models['standard_model']
					product.standard_model = target_model
					display_price_range = target_model['price']

				product.current_used_model = target_model
				product.display_price = target_model['price']
				product.display_price_range = display_price_range
				product.user_code = target_model['user_code']
				product.stock_type = target_model['stock_type']
				product.min_limit = product.stocks
				product.stocks = u'无限' if target_model[
					'stock_type'] == mall_models.PRODUCT_STOCK_TYPE_UNLIMIT else target_model['stocks']
			else:
				# 所有规格都已经被删除
				product.is_use_custom_model = False
				product.current_used_model = {}
				product.display_price = product.price
				product.display_price_range = product.price
				product.user_code = product.user_code
				product.stock_type = mall_models.PRODUCT_STOCK_TYPE_LIMIT
				product.stocks = 0
				product.min_limit = 0
				product.standard_model = {}
				product.models = []

	@staticmethod
	def __fill_image_detail(webapp_owner_id, products, product_ids):
		for product in products:
			product.swipe_images = [{
				'id': img.id, 
				'url': '%s%s' % (settings.IMAGE_HOST, img.url),
				'linkUrl': img.link_url, 
				'width': img.width, 
				'height': img.height
			} for img in mall_models.ProductSwipeImage.select().dj_where(product_id=product.id)]

	@staticmethod
	def __fill_property_detail(webapp_owner_id, products, product_ids):
		for product in products:
			product.properties = [{
				"id": property.id, 
				"name": property.name,
				"value": property.value
			} for property in mall_models.ProductProperty.select().dj_where(product_id=product.id)]

	@staticmethod
	def __fill_category_detail(webapp_owner_id, products, product_ids, only_selected_category=False):
		categories = list(Promall_models.ductCategory.select().dj_where(owner=webapp_owner_id).order_by('id'))

		# 获取product关联的category集合
		id2product = dict([(product.id, product) for product in products])
		for product in products:
			product.categories = []
			product.id2category = {}
			id2product[product.id] = product
			if not only_selected_category:
				for category in categories:
					category_data = {
						'id': category.id,
						'name': category.name,
						'is_selected': False
					}
					product.categories.append(category_data)
					product.id2category[category.id] = category_data

		category_ids = [category.id for category in categories]
		id2category = dict([(category.id, category) for category in categories])
		for relation in mall_models.CategoryHasProduct.select().dj_where(product_id__in=product_ids).order_by('id'):
			category_id = relation.category_id
			product_id = relation.product_id
			if not category_id in id2category:
				# 微众商城分类，在商户中没有
				continue
			category = id2category[category_id]
			if not only_selected_category:
				id2product[product_id].id2category[
					category.id]['is_selected'] = True
			else:
				id2product[product_id].categories.append({
					'id': category.id,
					'name': category.name,
					'is_selected': True
				})

	def __fill_promotion_detail2(self):
		promotion_ids = map(lambda x: x.promotion_id, promotion_models.ProductHasPromotion.select().dj_where(product=product.id))
		# Todo: 促销已经结束， 但数据库状态未更改
		promotions = promotion_models.Promotion.select().dj_where(
			owner_id=webapp_owner_id,
			id__in=promotion_ids,
			status=promotion_models.PROMOTION_STATUS_STARTED
		)
		promotion = None
		integral_sale = None
		for one_promotion in promotions:
			if one_promotion.type == promotion_models.PROMOTION_TYPE_INTEGRAL_SALE:
				integral_sale = one_promotion
			# RFC
			elif one_promotion.type != promotion_models.PROMOTION_TYPE_COUPON:
				promotion = one_promotion
		#填充积分折扣信息
		if integral_sale:
			promotion_models.Promotion.fill_concrete_info_detail(webapp_owner_id, [integral_sale])
			if integral_sale.promotion_title:
				product.integral_sale_promotion_title = integral_sale.promotion_title
			product.integral_sale = integral_sale.to_dict('detail', 'type_name')
		else:
			product.integral_sale = None
		#填充促销活动信息
		if promotion:
			promotion_models.Promotion.fill_concrete_info_detail(webapp_owner_id, [promotion])
			if promotion.promotion_title:
				product.promotion_title = promotion.promotion_title
			if promotion.type == promotion_models.PROMOTION_TYPE_PRICE_CUT:
				promotion.promotion_title = '满%s减%s' % (promotion.detail['price_threshold'], promotion.detail['cut_money'])
			elif promotion.type == promotion_models.PROMOTION_TYPE_PREMIUM_SALE:
				promotion.promotion_title = '%s * %s' % (promotion.detail['premium_products'][0]['name'], promotion.detail['count'])
			elif promotion.type == promotion_models.PROMOTION_TYPE_FLASH_SALE:
				# promotion.promotion_title = '活动截止:%s' % (promotion.end_date)
				gapPrice = product.price - promotion.detail['promotion_price']
				promotion.promotion_title = '已优惠%s元' % gapPrice
			else:
				promotion.promotion_title = ''
			product.promotion = promotion.to_dict('detail', 'type_name')
		else:
			product.promotion = None

	@staticmethod
	def __fill_promotion_detail(webapp_owner, products, product_ids):
		for product in products:
			product.promotion = None
		'''
		from mall.promotion import models as promotion_models
		today = datetime.today()
		id2product = dict([(product.id, product) for product in products])

		type2promotions = {}
		id2promotion = {}
		product_promotion_relations = list(
			promotion_models.Promotion.objects.filter(
				product_id__in=product_ids))
		promotion_ids = [relation.promotion_id
						 for relation in product_promotion_relations]
		promotions = list(
			promotion_models.Promotion.objects.filter(
				product_id__in=product_ids))
		for promotion in promotions:
			type2promotions.setdefault(promotion.type, []).append(promotion)
			id2promotion[promotion.id] = promotion

		for relation in product_promotion_relations:
			product = id2product[relation.product_id]
			promotion = id2promotion[relation.promotion_id]
			product.promotion = {
				'id': promotion.id,
				'type': promotion.type_name,
				'name': promotion.name,
				'status_value': promotion.status,
				'status': promotion.status_name,
				'start_date': promotion.start_date.strftime("%Y-%m-%d %H:%M"),
				'end_date': promotion.end_date.strftime('%Y-%m-%d %H:%M')
			}

		for type, promotions in type2promotions.items():
			if type == promotion_models.PROMOTION_TYPE_FLASH_SALE:
				model2product = dict(
					[(product.current_used_model['id'], product) for product in products])
				product_model_ids = [product.current_used_model['id']
									 for product in products]
				model_promotion_details = promotion_models.ProductModelFlashSaleDetail.objects.filter(
					owner=webapp_owner,
					product_model_id__in=product_model_ids)
				for model_promotion_detail in model_promotion_details:
					model2product[promotion_detail.product_model_id].promotion[
						'price'] = model_promotion_detail.promotion_price
			else:
				pass
		'''

	@staticmethod
	def __fill_sales_detail(webapp_owner_id, products, product_ids):
		id2product = dict([(product.id, product) for product in products])
		for product in products:
			product.sales = 0

		for sales in ProductSales.select().dj_where(product_id__in=product_ids):
			product_id = sales.product_id
			if id2product.has_key(product_id):
				id2product[product_id].sales = sales.sales

	@staticmethod
	def __fill_details(webapp_owner_id, products, options):
		"""
		填充各种细节信息
		"""
		id2property = None
		id2propertyvalue = None
		is_enable_model_property_info = options.get('with_model_property_info',False)
		if is_enable_model_property_info:
			# 获取model property，为后续使用做准备
			properties = list(mall_models.ProductModelProperty.select().dj_where(owner_id=webapp_owner_id))
			property_ids = [property.id for property in properties]
			id2property = dict([(str(property.id), property)
							   for property in properties])
			id2propertyvalue = {}
			for value in mall_models.ProductModelPropertyValue.select().dj_where(property__in=property_ids):
				id = '%d:%d' % (value.property_id, value.id)
				id2propertyvalue[id] = value

		product_ids = [product.id for product in products]

		for product in products:
			product.detail_link = '/mall2/product/?id=%d&source=onshelf' % product.id

		if options.get('with_price', False):
			Product.__fill_display_price(products)

		if options.get('with_product_model', False):
			Product.__fill_model_detail(
				webapp_owner_id,
				products,
				product_ids,
				id2property,
				id2propertyvalue,
				is_enable_model_property_info)

		if options.get('with_product_promotion', False):
			Product.__fill_promotion_detail(webapp_owner_id, products, product_ids)

		if options.get('with_image', False):
			Product.__fill_image_detail(webapp_owner_id, products, product_ids)

		if options.get('with_property', False):
			Product.__fill_property_detail(webapp_owner_id, products, product_ids)

		if options.get('with_selected_category', False):
			Product.__fill_category_detail(
				webapp_owner_id,
				products,
				product_ids,
				True)

		if options.get('with_all_category', False):
			self.__fill_category_detail(
				webapp_owner_id,
				products,
				product_ids,
				False)

		if options.get('with_sales', False):
			Product.__fill_sales_detail(webapp_owner_id, products, product_ids)

		# if options.get('with_promotion', False):
		# 	Product.__fill_promotion_detail(webapp_owner_id, products, product_ids)

	def to_dict(self, **kwargs):
		result = {
			'id': self.id,
			'owner_id': self.owner_id,
			'type': self.type,
			'is_deleted': self.is_deleted,
			'name': self.name,
			'model_name': getattr(self, 'model_name', 'standard'),
			'weshop_sync': self.weshop_sync,
			'shelve_type': self.shelve_type,
			'shelve_start_time': self.shelve_start_time,
			'shelve_end_time': self.shelve_end_time,
			'detail': self.detail,
			'thumbnails_url': self.thumbnails_url,
			'order_thumbnails_url': self.order_thumbnails_url if 'http:' in self.order_thumbnails_url else '%s%s' % (settings.IMAGE_HOST, self.order_thumbnails_url),
			'pic_url': self.pic_url,
			'detail_link': '/mall2/product/?id=%d&source=onshelf' % self.id,
			'categories': getattr(self, 'categories', []),
			'properties': getattr(self, 'properties', []),
			'product_model_properties': getattr(self, 'product_model_properties', None),
			'display_price': self.display_price,
			'display_price_range': self.display_price_range,
			'user_code': self.user_code,
			'bar_code': self.bar_code,
			'min_limit': self.min_limit,
			'stocks': self.stocks if self.stock_type else '无限',
			'sales': getattr(self, 'sales', 0),
			'is_use_custom_model': self.is_use_custom_model,
			'models': self.models,
			'custom_models': self.models[1:],
			'total_stocks': self.total_stocks,
			'is_sellout': self.is_sellout,
			'standard_model': self.standard_model,
			'current_used_model': self.current_used_model,
			'created_at': self.created_at if type(self.created_at) == str else datetime.strftime(self.created_at, '%Y-%m-%d %H:%M'),
			'display_index': self.display_index,
			'is_member_product': self.is_member_product,
			'purchase_price': self.purchase_price,
			'swipe_images': getattr(self, 'swipe_images', []),
			'promotion': getattr(self, 'promotion', None),
			'promotion_title': getattr(self, 'promotion_title', ''),
			'product_review': getattr(self, 'product_review', None),
			'price_info': getattr(self, 'price_info', None)
		}

		if 'extras' in kwargs:
			for extra in kwargs['extras']:
				result[extra] = getattr(self, extra, None)

		return result




# -*- coding: utf-8 -*-
"""@package business.mall.product
商品

Product是商品业务对象的实现，内部使用CachedProduct对象进行redis的读写操作。
OrderProduct，ShoppingCartProduct等更特定的商品业务对象都在内部使用Product业务对象实现。
"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from business.mall.realtime_stock import RealtimeStock
from business.mall.supplier import Supplier
from core.exceptionutil import unicode_full_stack
from eaglet.decorator import param_required
#from wapi import wapi_utils
from eaglet.core.cache import utils as cache_util
from db.mall import models as mall_models
from db.mall import promotion_models
from eaglet.core import watchdog
from business import model as business_model
import db.account.models as account_model
import settings
from business.mall.forbidden_coupon_product_ids import ForbiddenCouponProductIds
from business.mall.product_model_generator import ProductModelGenerator
from business.mall.product_model import ProductModel
from business.mall.promotion.promotion_repository import PromotionRepository
from business.decorator import cached_context_property


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
			#获取product及其model
			product_model = mall_models.Product.get(id = product_id)
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
					"with_product_promotion": True,
					"with_product_classification": True
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
		# if hasattr(product, 'integral_sale') and product.integral_sale \
		# 	and product.integral_sale['detail'].get('rules', None):
		# 	for i in product.integral_sale['detail']['rules']:
		# 		if i['member_grade_id'] == member_grade_id:
		# 			product.integral_sale['detail']['discount'] = str(i['discount'])+"%"
		# 			break

		# integral_sale_data = data.get('integral_sale', None)
		# if integral_sale_data and len(integral_sale_data) > 0:
		#     product.integral_sale_model = promotion_models.Promotion.from_dict(
		#         integral_sale_data)
		# else:
		#     product.integral_sale_model = None
		# product.original_promotion_title = data['promotion_title']

		return product

	@staticmethod
	@param_required(['webapp_owner', 'product_id'])
	def get(args):
		#TODO2: 临时解决方案，后续去除
		CachedProduct.webapp_owner = args['webapp_owner']
		webapp_owner_id = args['webapp_owner'].id
		product_id = args['product_id']
		member = args.get('member', None)
		member_grade_id = member.grade_id if member else None

		try:
			product = CachedProduct.__get_from_cache(webapp_owner_id, product_id, member_grade_id)

			if CachedProduct.webapp_owner.mall_type:
				is_pool_product = mall_models.ProductPool.select().dj_where(woid=webapp_owner_id, product_id=product_id).count() > 0
				if  product.owner_id != webapp_owner_id and (not is_pool_product):
					product.is_deleted = True
				elif product.owner_id != webapp_owner_id and is_pool_product:
					pool_product = mall_models.ProductPool.select().dj_where(woid=webapp_owner_id, product_id=product_id).first()
					if pool_product.status == mall_models.PP_STATUS_ON:
						product.shelve_type = mall_models.PRODUCT_SHELVE_TYPE_ON
					elif pool_product.status == mall_models.PP_STATUS_OFF:
						product.shelve_type = mall_models.PRODUCT_SHELVE_TYPE_OFF
					else:
						product.is_deleted = True

			elif product.owner_id != webapp_owner_id:
				product.is_deleted = True
		except:
			if settings.DEBUG and not settings.IS_UNDER_BDD:
				raise
			else:
				#记录日志
				alert_message = u"获取商品记录失败,商品id: {} cause:\n{}".format(product_id, unicode_full_stack())
				watchdog.alert(alert_message)
				#返回"被删除"商品
				product = Product()
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
		'thumbnails_url',
		'order_thumbnails_url',
		'pic_url',
		'swipe_images',
		'detail_link',
		'bar_code',
		'min_limit',
		'categories',
		'id2category',
		'properties',
		'created_at',
		'supplier',
		'supplier_user_id',

		#商品规格信息
		'is_use_custom_model',
		#'model_name',
		#'product_model_properties',
		'models',
		'used_system_model_properties',

		#价格、销售信息
		'price_info',
		'sales',
		'is_sellout',
		'postage_id',
		'postage_type',
		'unified_postage_money',
		'is_use_cod_pay_interface',
		'product_promotion_title', #商品的促销标题
		'is_enable_bill',
		'buy_in_supplier',

		#促销信息
		'promotion',
		'promotion_title', #商品关联的促销活动的促销标题
		'integral_sale',
		'product_review',
		'is_deleted',
		'is_delivery', # 是否勾选配送时间
		# 'supplier_name' # 供货商名称
		'purchase_price',
		'price',
		'weight',
		'stock_type',
		'limit_zone_type',
		'limit_zone',
		'classification_id'
	)


	@staticmethod
	@param_required(['webapp_owner', 'model', 'fill_options'])
	def from_model(args):
		webapp_owner = args['webapp_owner']
		model = args['model']
		fill_options = args.get('fill_options', {})

		product = Product(model)
		Product.__fill_details(webapp_owner, [product], fill_options)
		product.__set_image_to_lazy_load()
		product.context['webapp_owner'] = webapp_owner

		return product


	@staticmethod
	@param_required(['webapp_owner', 'models', 'fill_options'])
	def from_models(args):
		"""
		商品列表
		@param args:
		@return:
		"""

		webapp_owner = args['webapp_owner']
		models = args['models']
		fill_options = args.get('fill_options', {})

		products = []

		print("type:", type(models[0]))

		for model in models:
			products.append(Product(model))

		Product.__fill_details(webapp_owner, products, fill_options)

		return products


	@staticmethod
	@param_required(['webapp_owner', 'product_id'])
	def from_id(args):
		return CachedProduct.get(args)

	@staticmethod
	@param_required(['webapp_owner', 'member', 'product_ids'])
	def from_ids(args):
		"""从product_ids集合构造Product对象集合

		@return Product对象集合
		"""
		#update by bert
		return [Product.from_id({"product_id":product_id,"webapp_owner": args['webapp_owner']}) for product_id in args['product_ids']]

	def __init__(self, model=None):
		business_model.Model.__init__(self)
		self.promotion = None

		if model:
			self._init_slot_from_model(model)
			self.owner_id = model.owner_id
			self.min_limit = model.stocks
			self.thumbnails_url = '%s%s' % (settings.IMAGE_HOST, model.thumbnails_url) if model.thumbnails_url.find('http') == -1 else model.thumbnails_url
			self.pic_url = '%s%s' % (settings.IMAGE_HOST, model.pic_url) if model.pic_url.find('http') == -1 else model.pic_url

	def __set_image_to_lazy_load(self):
		"""将商品详情图片设置微lazy load
		"""
		# 商品详情图片lazyload
		# TODO: 将这个逻辑改成字符串处理，不用xml解析
		soup = BeautifulSoup(self.detail)
		for img in soup.find_all('img'):
			try:
				if 'http:' in img['src']:
					img['data-url'] = img['src']
				else:
					img['data-url'] = '%s%s' % (settings.IMAGE_HOST, img['src'])
				del img['src']
				del img['title']
			except:
				pass
		self.detail = str(soup)

	@property
	def is_sellout(self):
		"""
		[property] 是否卖光
		"""
		return self.total_stocks <= 0

	@is_sellout.setter
	def is_sellout(self, value):
		"""
		[property setter] 是否卖光
		"""
		pass

	@property
	def total_stocks(self):
		"""
		[property] 商品总库存
		"""
		context = self.context
		if not 'total_stocks' in context:
			context['total_stocks'] = 0
			models = self.models
			# if self.is_use_custom_model:
			# 	models = self.models[1:]
			# else:
			# 	models = self.models

			if not models or len(models) == 0:
				context['total_stocks'] = 0
				return context['total_stocks']
			is_dict = (type(models[0]) == dict)

			# for model in models:
			# 	stock_type = model['stock_type'] if is_dict else model.stock_type
			# 	stocks = model['stocks'] if is_dict else model.stocks
			# 	if stock_type == mall_models.PRODUCT_STOCK_TYPE_UNLIMIT:
			# 		context['total_stocks'] = u'无限'
			# 		return context['total_stocks']
			# 	else:
			# 		context['total_stocks'] = context['total_stocks'] + stocks

			# 有无限的规格
			has_unlimited_model = False
			for model in models:
				stock_type = model['stock_type'] if is_dict else model.stock_type
				if stock_type == mall_models.PRODUCT_STOCK_TYPE_UNLIMIT:
					has_unlimited_model = True
					break
			if has_unlimited_model:
				context['total_stocks'] = u'无限'
				return context['total_stocks']
			else:
				realtime_stock = RealtimeStock.from_product_id({
					'product_id': self.id
				}).model2stock
				stock_dicts = realtime_stock.values()
				# stock_dicts:[{'stock_type': 1, 'stocks': 1}, {'stock_type': 1, 'stocks': 2}, {'stock_type': 1, 'stocks': 3}]
				for s in stock_dicts:
					context['total_stocks'] = context['total_stocks'] + s['stocks']

		return context['total_stocks']

	@total_stocks.setter
	def total_stocks(self, value):
		"""
		[property setter] 商品总库存
		"""
		self.context['total_stocks'] = value

	# 如果规格有图片就显示，如果没有，使用缩略图
	@property
	def order_thumbnails_url(self):
		"""
		[property] 订单中的缩略图
		"""
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
		"""
		[property setter] 订单中的缩略图
		"""
		# self.context['order_thumbnails_url'] = url
		self.thumbnails_url = url

	@property
	def hint(self):
		"""
		[property] 判断商品是否被禁止使用全场优惠券
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
		判断商品是否是上架状态
		"""
		return self.shelve_type == mall_models.PRODUCT_SHELVE_TYPE_ON

	def apply_discount(self, webapp_user):
		"""
		执行webapp_user携带的折扣信息

		Parameters
			[in] webapp_user
		"""
		if self.is_member_product:
			_, discount_value = webapp_user.member.discount
			discount = discount_value / 100.0

			self.price_info['min_price'] = round(self.price_info['min_price'] * discount, 2) #折扣后的价格
			self.price_info['max_price'] = round(self.price_info['max_price'] * discount, 2) #折扣后的价格
			self.price_info['display_price'] = round(float(self.price_info['display_price']) * discount, 2) #折扣后的价格

			for model in self.models:
				model.price = round(model.price * discount, 2)

	@cached_context_property
	def __deleted_models(self):
		return list(mall_models.ProductModel.select().dj_where(product_id=self.id, is_deleted=True))

	def get_specific_model(self, model_name):
		"""
		获得特定的商品规格信息

		@param [in] model_name: 商品规格名

		@return ProductModel对象

		注意，这里返回的有可能是被删除的规格，使用者应该通过product_model.is_deleted来判断
		"""
		models = self.models
		if not models:
			watchdog.info({
				'msg': u'商品models为空！',
				'product_id': self.id,
				'product_detail': self.to_dict()
			})
			Product.__fill_model_detail(self.context['webapp_owner'], [self], True)
			models = self.models
		candidate_models = filter(lambda m: m.name == model_name if m else False, models)
		if len(candidate_models) > 0:
			model = candidate_models[0]
			return model
		else:
			candidate_models = filter(lambda m: m.name == model_name if m else False, self.__deleted_models)
			if len(candidate_models) > 0:
				model = candidate_models[0]
				return model
			else:
				return None

	@staticmethod
	def __fill_display_price(products):
		"""根据商品规格，获取商品价格
		"""
		for product in products:
			if product.is_use_custom_model:
				custom_models = product.models
				if len(custom_models) == 1:
					#只有一个custom model，显示custom model的价格信息
					product_model = custom_models[0]
					product.price_info = {
						'display_price': str("%.2f" % product_model.price),
						'display_original_price': str("%.2f" % product_model.original_price),
						'display_market_price': str("%.2f" % product_model.market_price),
						'min_price': product_model.price,
						'max_price': product_model.price,
					}
				else:
					#有多个custom model，显示custom model集合组合后的价格信息
					prices = []
					market_prices = []
					for product_model in custom_models:
						if product_model.price > 0:
							prices.append(product_model.price)
						if product_model.market_price > 0:
							market_prices.append(product_model.market_price)

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
						#'display_price': price_range,
						#'display_original_price': price_range,
						'display_price': min_price,
						'display_original_price': min_price,
						'display_market_price': market_price_range,
						'min_price': min_price,
						'max_price': max_price,
					}
			else:
				standard_model = None
				if product.models:
					standard_model = product.models[0]

				if standard_model:
					product.price_info = {
						'display_price': str("%.2f" % standard_model.price),
						'display_original_price': str("%.2f" % standard_model.original_price),
						'display_market_price': str("%.2f" % standard_model.market_price),
						'min_price': standard_model.price,
						'max_price': standard_model.price,
					}
				else:
					product.price_info = {
						'display_price': str("%.2f" % 0),
						'display_original_price': str("%.2f" % 0),
						'display_market_price': str("%.2f" % 0),
						'min_price': 0,
						'max_price': 0,
					}

	@staticmethod
	def __fill_model_detail(webapp_owner, products, is_enable_model_property_info=False):
		"""填充商品规格相关细节
		向product中添加is_use_custom_model, models, used_system_model_properties三个属性
		"""
		if products[0].models:
			#已经完成过填充，再次进入，跳过填充
			return

		#TODO2: 因为这里是静态方法，所以目前无法使用product.context['webapp_owner']，构造基于Object的临时解决方案，需要优化
		webapp_owner_id = webapp_owner.id
		from core.cache.utils import Object
		# webapp_owner = Object('fake_webapp_owner')
		# webapp_owner.id = webapp_owner_id
		product_model_generator = ProductModelGenerator.get({
			'webapp_owner': webapp_owner
		})
		product_model_generator.fill_models_for_products(products, is_enable_model_property_info)

	@staticmethod
	def __fill_image_detail(webapp_owner, products, product_ids):
		"""填充商品轮播图相关细节
		"""
		for product in products:
			product.swipe_images = [{
				'id': img.id,
				'url': '%s%s' % (settings.IMAGE_HOST, img.url) if img.url.find('http') == -1 else img.url,
				'linkUrl': img.link_url,
				'width': img.width,
				'height': img.height
			} for img in mall_models.ProductSwipeImage.select().dj_where(product_id=product.id)]

	@staticmethod
	def __fill_property_detail(webapp_owner, products, product_ids):
		"""填充商品属性相关细节
		"""
		for product in products:
			product.properties = [{
				"id": property.id,
				"name": property.name,
				"value": property.value
			} for property in mall_models.ProductProperty.select().dj_where(product_id=product.id)]

	@staticmethod
	def __fill_category_detail(webapp_owner, products, product_ids, only_selected_category=False):
		"""填充商品分类信息相关细节
		"""
		webapp_owner_id = webapp_owner.id
		categories = list(mall_models.ProductCategory.select().dj_where(owner=webapp_owner_id).order_by('id'))

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

	@staticmethod
	def __fill_promotion_detail(webapp_owner, products, product_ids):
		"""填充商品促销相关细节
		"""
		PromotionRepository.fill_for_products({
			'products': products,
			'webapp_owner': webapp_owner
		})

	@staticmethod
	def __fill_sales_detail(webapp_owner, products, product_ids):
		"""填充商品销售情况相关细节
		"""
		id2product = dict([(product.id, product) for product in products])
		for product in products:
			product.sales = 0

		for sales in ProductSales.select().dj_where(product_id__in=product_ids):
			product_id = sales.product_id
			if id2product.has_key(product_id):
				id2product[product_id].sales = sales.sales

	@staticmethod
	def __fill_classification_detail(webapp_owner, products, product_ids):
		"""填充商品分类信息
		"""
		#获取商品分类ID   product_classification为None时，表示无分类信息
		for product in products:
			product_classification = mall_models.ClassificationHasProduct.select().dj_where(product_id=product.id).first()
			if product_classification:
				product.classification_id = product_classification.classification_id
			else:
				product.classification_id = 0

	@staticmethod
	def __fill_details(webapp_owner, products, options):
		"""填充各种细节信息

		此方法会根据options中的各种填充选项，填充相应的细节信息

		@param[in] products: Product业务对象集合
		@param[in] options: 填充选项
			with_price: 填充价格信息
			with_product_model: 填充所有商品规格信息
			with_product_promotion: 填充商品促销信息
			with_image: 填充商品轮播图信息
			with_property: 填充商品属性信息
			with_selected_category: 填充选中的分类信息
			with_all_category: 填充所有商品分类详情
			with_sales: 填充商品销售详情
			with_product_classification:填充商品的分类信息
		"""
		is_enable_model_property_info = options.get('with_model_property_info',False)
		product_ids = [product.id for product in products]

		for product in products:
			product.detail_link = '/mall2/product/?id=%d&source=onshelf' % product.id

		if options.get('with_price', False):
			#price需要商品规格信息
			Product.__fill_model_detail(
				webapp_owner,
				products,
				is_enable_model_property_info)
			Product.__fill_display_price(products)

		if options.get('with_product_model', False):
			Product.__fill_model_detail(
				webapp_owner,
				products,
				is_enable_model_property_info)

		if options.get('with_product_promotion', False):
			Product.__fill_promotion_detail(webapp_owner, products, product_ids)

		if options.get('with_image', False):
			Product.__fill_image_detail(webapp_owner, products, product_ids)

		if options.get('with_property', False):
			Product.__fill_property_detail(webapp_owner, products, product_ids)

		if options.get('with_selected_category', False):
			Product.__fill_category_detail(
				webapp_owner,
				products,
				product_ids,
				True)

		if options.get('with_all_category', False):
			Product.__fill_category_detail(
				webapp_owner,
				products,
				product_ids,
				False)

		if options.get('with_sales', False):
			Product.__fill_sales_detail(webapp_owner, products, product_ids)

		if options.get('with_product_classification', False):
			Product.__fill_classification_detail(
				webapp_owner,
				products,
				product_ids
				)

		# if options.get('with_promotion', False):
		# 	Product.__fill_promotion_detail(webapp_owner_id, products, product_ids)

	def to_dict(self, **kwargs):
		self.product_promotion_title = self.promotion_title
		promotion_title = self.promotion_title
		if self.promotion and self.promotion.promotion_title:
			promotion_title = self.promotion.promotion_title
		result = {
			'id': self.id,
			'owner_id': self.owner_id,
			'type': self.type,
			'is_deleted': self.is_deleted,
			'name': self.name,
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
			'bar_code': self.bar_code,
			'min_limit': self.min_limit,
			'sales': getattr(self, 'sales', 0),
			'is_use_custom_model': self.is_use_custom_model,
			'is_use_cod_pay_interface': self.is_use_cod_pay_interface,
			'models': [model.to_dict() for model in self.models] if self.models else [],
			'used_system_model_properties': getattr(self, 'used_system_model_properties', None),
			'total_stocks': self.total_stocks,
			'is_sellout': self.is_sellout,
			'is_enable_bill': self.is_enable_bill,
			'buy_in_supplier': self.buy_in_supplier,
			'created_at': self.created_at if type(self.created_at) == str else datetime.strftime(self.created_at, '%Y-%m-%d %H:%M'),
			'supplier': self.supplier,
			'supplier_name': self.supplier_name,
			'display_index': self.display_index,
			'is_member_product': self.is_member_product,
			'swipe_images': getattr(self, 'swipe_images', []),
			'promotion': self.promotion.to_dict() if self.promotion else None,
			'promotion_title': promotion_title,
			'product_promotion_title': self.product_promotion_title,
			'integral_sale': self.integral_sale.to_dict() if self.integral_sale else None,
			'product_review': getattr(self, 'product_review', None),
			'price_info': getattr(self, 'price_info', None),
			'postage_type': self.postage_type,
			'unified_postage_money': self.unified_postage_money,
			'is_delivery': self.is_delivery,
			'purchase_price': self.purchase_price,
			'supplier_user_id': self.supplier_user_id,
			'supplier_postage_config': self.supplier_postage_config,
			'use_supplier_postage': self.use_supplier_postage,
			'limit_zone_type': self.limit_zone_type,
			'limit_zone': self.limit_zone,
			'classification_id': self.classification_id
		}
		if 'extras' in kwargs:
			for extra in kwargs['extras']:
				result[extra] = getattr(self, extra, None)

		return result

	def after_from_dict(self):
		product_models = []
		for model_dict in self.models:
			product_models.append(ProductModel.from_dict(model_dict))
		self.models = product_models

		if self.promotion:
			self.promotion = PromotionRepository.get_promotion_from_dict_data(self.promotion)

			if not self.promotion.is_active():
				#缓存中的促销已过期
				self.promotion = None

		if self.integral_sale:
			self.integral_sale = PromotionRepository.get_promotion_from_dict_data(self.integral_sale)

			if not self.integral_sale.is_active():
				self.integral_sale = None

	@cached_context_property
	def supplier_name(self):
		try:
			# 非微众系列商家
			if not self.context['webapp_owner'].user_profile.webapp_type:
				return ''
			# 手动添加的供货商
			if self.supplier:
				return Supplier.get_supplier_name(self.supplier)
			# 同步的供货商
			relation = mall_models.WeizoomHasMallProductRelation.select().dj_where(weizoom_product_id=self.id).first()
			if relation:
				supplier_name = account_model.UserProfile.select().dj_where(user_id=relation.mall_id).first().store_name
			else:
				supplier_name = ''

			return supplier_name
		except:
			watchdog.alert(unicode_full_stack())
			return ''

	@cached_context_property
	def supplier_postage_config(self):
		if not self.supplier:
			return {}

		supplier_postage_config_model = mall_models.SupplierPostageConfig.select().dj_where(
				supplier_id=self.supplier,
				status=True
			).first()
		if supplier_postage_config_model and supplier_postage_config_model.postage:
			return {
				'condition_type': supplier_postage_config_model.condition_type,
				'condition_money': supplier_postage_config_model.condition_money,
				'postage': supplier_postage_config_model.postage
			}
		else:
			return {}

	@cached_context_property
	def use_supplier_postage(self):
		if not self.supplier:
			return False
		supplier_model = mall_models.Supplier.select().dj_where(id=self.supplier).first()
		user_profile = account_model.UserProfile.select().dj_where(user_id=supplier_model.owner_id).first()
		if supplier_model.name == u'自营' and user_profile.webapp_type == 3:
			return False
		else:
			return True
	# @cached_context_property
	# def supplier_user_id(self):
	# 	try:
	# 		if not self.context['webapp_owner'].user_profile.webapp_type:
	# 			return 0
	# 		relation = mall_models.WeizoomHasMallProductRelation.select().dj_where(weizoom_product_id=self.id).first()
	# 		return relation.mall_id
	# 	except BaseException as e:
	# 		return 0

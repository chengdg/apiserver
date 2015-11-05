# -*- coding: utf-8 -*-

import json
import itertools

from core import resource
from core import auth
from cache import utils as cache_util
import cache
from wapi.decorators import param_required
from wapi.mall import models as mall_models
import settings


class RProducts(resource.Resource):
	"""
	商品集合
	"""
	app = 'mall'
	resource = 'products'

	@staticmethod
	def get_product_ids_in_weizoom_mall(webapp_id):
		return [weizoom_mall_other_mall_product.product_id for weizoom_mall_other_mall_product in mall_models.WeizoomMallHasOtherMallProduct.select().dj_where(webapp_id=webapp_id)]

	###################################################################################
	# get_weizoom_mall_partner_products: 获取该微众商城下的合作商家加入到微众商城的商品
	###################################################################################
	@staticmethod
	def get_weizoom_mall_partner_products_and_ids(webapp_id):
		return RProducts._get_weizoom_mall_partner_products_and_ids_by(webapp_id)

	@staticmethod
	def get_verified_weizoom_mall_partner_products_and_ids(webapp_id):
		return RProducts._get_weizoom_mall_partner_products_and_ids_by(webapp_id, True)

	@staticmethod
	def get_not_verified_weizoom_mall_partner_products_and_ids(webapp_id):
		return RProducts._get_weizoom_mall_partner_products_and_ids_by(webapp_id, False)

	@staticmethod
	def _get_weizoom_mall_partner_products_and_ids_by(webapp_id, is_checked=None):
		if mall_models.WeizoomMall.select().dj_where(webapp_id=webapp_id).count() > 0:
			weizoom_mall = mall_models.WeizoomMall.select().dj_where(webapp_id=webapp_id)[0]

			product_ids = []
			product_check_dict = dict()
			other_mall_products = mall_models.WeizoomMallHasOtherMallProduct.select().dj_where(weizoom_mall=weizoom_mall)
			if is_checked != None:
				 other_mall_products.dj_where(is_checked=is_checked)

			for other_mall_product in other_mall_products:
				product_check_dict[other_mall_product.product_id] = other_mall_product.is_checked
				product_ids.append(other_mall_product.product_id)

			products = mall_models.Product.select().dj_where(id__in=product_ids, shelve_type=mall_models.PRODUCT_SHELVE_TYPE_ON, is_deleted=False)

			for product in products:
				product.is_checked = product_check_dict[product.id]

			return products, product_ids
		else:
			return None, None

	@staticmethod
	def get_products(webapp_id, is_access_weizoom_mall, webapp_owner_id, category_id, options=dict()):
		"""
		get_products: 获得product集合

		options可用参数：

		 1. search_info: 搜索

		最后修改：闫钊
		"""
		#获得category和product集合
		category = None
		products = None
		if category_id == 0:
			products = mall_models.Product.select().dj_where(
				owner = webapp_owner_id, 
				shelve_type = mall_models.PRODUCT_SHELVE_TYPE_ON, 
				is_deleted = False,
				type__not = mall_models.PRODUCT_DELIVERY_PLAN_TYPE).order_by(mall_models.Product.display_index, -mall_models.Product.id)

			if not is_access_weizoom_mall:
				# 非微众商城
				product_ids_in_weizoom_mall = RProducts.get_product_ids_in_weizoom_mall(webapp_id)
				products.dj_where(id__notin = product_ids_in_weizoom_mall)

			products_0 = products.dj_where(display_index=0)
			products_not_0 = products.dj_where(display_index__not=0)
			# TODO: need to be optimized
			products = list(itertools.chain(products_not_0, products_0))

			category = mall_models.ProductCategory()
			category.name = u'全部'
		else:
			watchdog_alert('过期的方法分支module_api.get_products_in_webapp else', type='mall')
			# try:
			if not is_access_weizoom_mall:
				# 非微众商城
				product_ids_in_weizoom_mall = RProducts.get_product_ids_in_weizoom_mall(webapp_id)
				other_mall_product_ids_not_checked = []
			else:
				product_ids_in_weizoom_mall = []
				_, other_mall_product_ids_not_checked = RProducts.get_not_verified_weizoom_mall_partner_products_and_ids(webapp_id)

			category = mall_models.ProductCategory.get(mall_models.ProductCategory.id==category_id)
			category_has_products = mall_models.CategoryHasProduct.select().dj_where(category=category)
			products_0 = []  # 商品排序， 过滤0
			products_not_0 = []  # 商品排序， 过滤!0
			for category_has_product in category_has_products:
				if category_has_product.product.shelve_type == mall_models.PRODUCT_SHELVE_TYPE_ON:
					product = category_has_product.product
					#过滤已删除商品和套餐商品
					if(product.is_deleted or product.type == mall_models.PRODUCT_DELIVERY_PLAN_TYPE or
								product.id in product_ids_in_weizoom_mall or
								product.id in other_mall_product_ids_not_checked or
								product.shelve_type != mall_models.PRODUCT_SHELVE_TYPE_ON):
						continue
					# # 商品排序， 过滤
					if product.display_index == 0:
						products_0.append(product)
					else:
						products_not_0.append(product)
			# 处理商品排序
			products_0 = sorted(products_0, key=operator.attrgetter('id'), reverse=True)
			products_not_0 = sorted(products_not_0, key=operator.attrgetter('display_index'))
			products = products_not_0 + products_0
			# except :
			# 	products = []
			# 	category = ProductCategory()
			# 	category.is_deleted = True
			# 	category.name = u'全部'

		#处理search信息
		# if 'search_info' in options:
		# 	query = options['search_info']['query']
		# 	if query:
		# 		conditions = {}
		# 		conditions['name__contains'] = query
		# 		products = products.filter(**conditions)
		return category, products

	@staticmethod
	def get_from_db(webapp_owner_user_profile, is_access_weizoom_mall):
		def inner_func():
			webapp_id = webapp_owner_user_profile.webapp_id
			webapp_owner_id = webapp_owner_user_profile.user_id

			_, products = RProducts.get_products(webapp_id, is_access_weizoom_mall, webapp_owner_id, 0)

			categories = mall_models.ProductCategory.select().dj_where(owner=webapp_owner_id)

			product_ids = [product.id for product in products]
			category_has_products = mall_models.CategoryHasProduct.select().dj_where(product__in=product_ids)
			product2categories = dict()
			for relation in category_has_products:
				product2categories.setdefault(relation.product_id, set()).add(relation.category_id)

			try:
				categories = [{"id": category.id, "name": category.name} for category in categories]
				product_dicts = []

				# Fill detail
				new_products = []
				import resource
				for product in products:
					new_product = resource.get('mall', 'product_detail', {
						"oid": webapp_owner_id,
						"product_id": product.id
					})
					#new_product = get_webapp_product_detail(webapp_owner_id, product.id)
					new_products.append(new_product)

				mall_models.Product.fill_display_price(new_products)

				for product in new_products:
					product_dict = product.to_dict()
					product_dict['display_price'] = product.display_price
					product_dict['categories'] = product2categories.get(product.id, set())
					product_dict['promotion'] = product.promotion if hasattr(product, 'promotion') else None
					product_dicts.append(product_dict)
				return {
					'value': {
						"products": product_dicts,
						"categories": categories
					}
				}
			except:
				if settings.DEBUG:
					raise
				else:
					return None
		return inner_func

	@staticmethod
	def get_from_cache(webapp_owner_user_profile, is_access_weizoom_mall, category_id):
		key = 'webapp_products_categories_{wo:%s}' % webapp_owner_user_profile.user_id
		data = cache_util.get_from_cache(key, RProducts.get_from_db(webapp_owner_user_profile, is_access_weizoom_mall))

		if category_id == 0:
			category = mall_models.ProductCategory()
			category.name = u'全部'
		else:
			id2category = dict([(c["id"], c) for c in data['categories']])
			if category_id in id2category:
				category_dict = id2category[category_id]
				category = mall_models.ProductCategory()
				category.id = category_dict['id']
				category.name = category_dict['name']
			else:
				category = mall_models.ProductCategory()
				category.is_deleted = True
				category.name = u'已删除分类'

		products = mall_models.Product.from_list(data['products'])
		if category_id != 0:
			products = [product for product in products if category_id in product.categories]

			# 分组商品排序
			products_id = map(lambda p: p.id, products)
			chp_list = mall_models.CategoryHasProduct.select().dj_where(category_id=category_id, product__in=products_id)
			product_id2chp = dict(map(lambda chp: (chp.product_id, chp), chp_list))
			for product in products:
				product.display_index = product_id2chp[product.id].display_index
				product.join_category_time = product_id2chp[product.id].created_at

			# 1.shelve_type, 2.display_index, 3.id
			products_is_0 = filter(lambda p: p.display_index == 0, products)
			products_not_0 = filter(lambda p: p.display_index != 0, products)
			products_is_0 = sorted(products_is_0, key=attrgetter('join_category_time'), reverse=True)
			products_not_0 = sorted(products_not_0, key=attrgetter('display_index'))

			products = products_not_0 + products_is_0

		return category, products

	@param_required(['oid', 'category_id', 'wid'])
	def get(args):
		"""
		获取商品详情

		@param category_id 类别ID(id=0表示全部分类)
		"""
		owner_id = args['oid']
		category_id = int(args['category_id'])
		webapp_id = args['wid']
		is_access_weizoom_mall = args.get('is_access_weizoom_mall', False)
		
		# 伪造一个UserProfile，便于传递参数
		user_profile = auth.UserProfile(webapp_id, owner_id)

		#product = mall_models.Product.objects.get(id=args['id'])

		# 通过缓存获取数据
		category, products = RProducts.get_from_cache(user_profile, is_access_weizoom_mall, category_id)
		#print("products: {}".format(products))
		#func = webapp_cache.get_webapp_products_from_db(user_profile, is_access_weizoom_mall)
		#result = func()
		#print("result from get_webapp_products_from_db: {}".format(result))
		#products = result['value']['products']
		#categories = result['value']['categories']
		result = []
		for product in products:
			data = product.to_dict('display_price')
			data['pic_url'] = '%s%s' % (settings.IMAGE_HOST, data['pic_url'])
			data['thumbnails_url'] = '%s%s' % (settings.IMAGE_HOST, data['thumbnails_url'])
			result.append(data)
		return result

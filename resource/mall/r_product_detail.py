# -*- coding: utf-8 -*-

import json

from bs4 import BeautifulSoup

from core import inner_resource
from wapi.decorators import param_required
from wapi import wapi_utils
from cache import utils as cache_util
from wapi.mall import models as mall_models
from wapi.mall import promotion_models
import settings
from core.watchdog.utils import watchdog_alert


class RProductDetail(inner_resource.Resource):
	"""
	商品详情
	"""
	app = 'mall'
	resource = 'product_detail'

	@staticmethod
	def to_dict(products):
		data = []
		for product in products:
			data.append(Product.to_dict(product))
		return data

	@staticmethod
	def get_from_db(webapp_owner_id, product_id, member_grade_id=None):
		"""
		从数据库中获取商品详情
		"""
		def inner_func():
			try:
				#获取product及其model
				product = mall_models.Product.get(mall_models.Product.id == product_id)
				if product.owner_id != webapp_owner_id:
					product.postage_id = -1
					product.unified_postage_money = 0
					product.postage_type = mall_models.POSTAGE_TYPE_UNIFIED
				product.update_time = product.update_time.strftime("%Y-%m-%d %H:%M:%S")
				product.created_at = product.created_at.strftime("%Y-%m-%d %H:%M:%S")
				#product.fill_model()

				mall_models.Product.fill_details(webapp_owner_id, [product], {
					"with_price": True,
					"with_product_model": True,
					"with_model_property_info": True,
					"with_image": True,
					"with_property": True
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

				#获取促销活动和积分折扣信息
				#TODO: 恢复促销活动的逻辑
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

			# 商品详情图片lazyload
			# TODO: 将这个逻辑改成字符串处理，不用xml解析
			soup = BeautifulSoup(product.detail)
			for img in soup.find_all('img'):
				try:
					img['data-url'] = img['src']
					del img['src']
					del img['title']
				except:
					pass
			product.detail = str(soup)

			data = product.format_to_dict()

			return {'value': data}

		return inner_func

	@staticmethod
	def get_from_cache(woid, product_id, member_grade_id=None):
		"""
		webapp_cache.get_webapp_product_detail
		"""
		key = 'webapp_product_detail_{wo:%s}_{pid:%s}' % (woid, product_id)
		data = cache_util.get_from_cache(key, RProductDetail.get_from_db(woid, product_id))

		product = mall_models.Product.from_dict(data)

		# Set member's discount of the product
		if hasattr(product, 'integral_sale') and product.integral_sale \
			and product.integral_sale['detail'].get('rules', None):
			for i in product.integral_sale['detail']['rules']:
				if i['member_grade_id'] == member_grade_id:
					product.integral_sale['detail']['discount'] = str(i['discount'])+"%"
					break

		promotion_data = data.get('promotion', None)
		if promotion_data and len(promotion_data) > 0:
		    product.promotion_model = promotion_models.Promotion.from_dict(
		        promotion_data)
		else:
		    product.promotion_model = dict()
		product.promotion_dict = dict()

		integral_sale_data = data.get('integral_sale', None)
		if integral_sale_data and len(integral_sale_data) > 0:
		    product.integral_sale_model = promotion_models.Promotion.from_dict(
		        integral_sale_data)
		else:
		    product.integral_sale_model = None
		product.original_promotion_title = data['promotion_title']

		return product

	@param_required(['woid', 'product_id'])
	def get(args):
		"""
		module_api.get_product_detail
		"""
		webapp_owner_id = args['woid']
		product_id = args['product_id']
		member = args.get('member', None)
		member_grade_id = member.grade_id if member else None

		try:
			product = RProductDetail.get_from_cache(webapp_owner_id, product_id, member_grade_id)

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

		if 'return_model' in args:
			return product
		else:
			return product.format_to_dict()

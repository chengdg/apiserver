# -*- coding: utf-8 -*-

import json

from bs4 import BeautifulSoup

from core import resource
from wapi.decorators import param_required
from wapi import wapi_utils
from cache import utils as cache_util
from wapi.mall import models as mall_models
import settings

class RProductDetail(resource.Resource):
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
				product.fill_model()

				#获取轮播图
				product.swipe_images = []
				for swipe_image in mall_models.ProductSwipeImage.select().where(mall_models.ProductSwipeImage.product_id==product_id):
					product.swipe_images.append({
						'url': swipe_image.url
					})
				product.swipe_images_json = json.dumps(product.swipe_images)

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
				# TODO: 恢复促销活动的逻辑
				# promotion_ids = map(lambda x: x.promotion_id, promotion_models.ProductHasPromotion.objects.filter(product=product))
				# # Todo: 促销已经结束， 但数据库状态未更改
				# promotions = promotion_models.Promotion.objects.filter(
				# 	owner_id=webapp_owner_id,
				# 	id__in=promotion_ids,
				# 	status=promotion_models.PROMOTION_STATUS_STARTED
				# )
				# promotion = None
				# integral_sale = None
				# for one_promotion in promotions:
				# 	if one_promotion.type == promotion_models.PROMOTION_TYPE_INTEGRAL_SALE:
				# 		integral_sale = one_promotion
				# 	# RFC
				# 	elif one_promotion.type != promotion_models.PROMOTION_TYPE_COUPON:
				# 		promotion = one_promotion
				# #填充促销活动信息
				# if promotion:
				# 	promotion_models.Promotion.fill_concrete_info_detail(webapp_owner_id, [promotion])
				# 	product.original_promotion_title = product.promotion_title
				# 	if promotion.promotion_title:
				# 		product.promotion_title = promotion.promotion_title
				# 	if promotion.type == promotion_models.PROMOTION_TYPE_PRICE_CUT:
				# 		promotion.promotion_title = '满%s减%s' % (promotion.detail['price_threshold'], promotion.detail['cut_money'])
				# 	elif promotion.type == promotion_models.PROMOTION_TYPE_PREMIUM_SALE:
				# 		promotion.promotion_title = '%s * %s' % (promotion.detail['premium_products'][0]['name'], promotion.detail['count'])
				# 	elif promotion.type == promotion_models.PROMOTION_TYPE_FLASH_SALE:
				# 		# promotion.promotion_title = '活动截止:%s' % (promotion.end_date)
				# 		gapPrice = product.price - promotion.detail['promotion_price']
				# 		promotion.promotion_title = '已优惠%s元' % gapPrice
				# 	else:
				# 		promotion.promotion_title = ''
				# 	product.promotion = promotion.to_dict('detail', 'type_name')
				# else:
				# 	product.original_promotion_title = product.promotion_title
				# 	product.promotion = None
				# #填充积分折扣信息
				# if integral_sale:
				# 	promotion_models.Promotion.fill_concrete_info_detail(webapp_owner_id, [integral_sale])
				# 	# integral_sale.end_date = integral_sale.end_date.strftime('%Y-%m-%d %H:%M:%S')
				# 	# integral_sale.created_at = integral_sale.created_at.strftime('%Y-%m-%d %H:%M:%S')
				# 	# integral_sale.start_date = integral_sale.start_date.strftime('%Y-%m-%d %H:%M:%S')
				# 	product.integral_sale = integral_sale.to_dict('detail', 'type_name')
				# else:
				# 	product.integral_sale = None

				# Product.fill_property_detail(webapp_owner_id, [product], '')
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

			# product.mark = str(product.id) + '-' + product.model_name
			data = product.to_dict(
									'min_limit',
									'swipe_images_json',
									'models',
									'_is_use_custom_model',
									'product_model_properties',
									'is_sellout',
									'promotion',
									'integral_sale',
									'properties',
									'product_review'
			)
			#data['original_promotion_title'] = product.original_promotion_title

			return {'value': data}

		return inner_func

	@param_required(['oid', 'product_id'])
	def get(args):
		oid = args['oid']
		product_id = args['product_id']
		key = 'webapp_product_detail_{wo:%s}_{pid:%s}' % (oid, product_id)
		data = cache_util.get_from_cache(key, RProductDetail.get_from_db(oid, product_id))

		product = mall_models.Product.from_dict(data)

		# Set member's discount of the product
		if hasattr(product, 'integral_sale') and product.integral_sale \
			and product.integral_sale['detail'].get('rules', None):
			for i in product.integral_sale['detail']['rules']:
				if i['member_grade_id'] == member_grade_id:
					product.integral_sale['detail']['discount'] = str(i['discount'])+"%"
					break

		# promotion_data = data['promotion']
		# if promotion_data and len(promotion_data) > 0:
		#     product.promotion_model = promotion_models.Promotion.from_dict(
		#         promotion_data)
		# else:
		#     product.promotion_model = dict()
		product.promotion_dict = dict()

		# integral_sale_data = data['integral_sale']
		# if integral_sale_data and len(integral_sale_data) > 0:
		#     product.integral_sale_model = promotion_models.Promotion.from_dict(
		#         integral_sale_data)
		# else:
		#     product.integral_sale_model = None
		# product.original_promotion_title = data['original_promotion_title']

		return product

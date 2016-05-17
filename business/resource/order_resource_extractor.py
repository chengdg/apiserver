#coding: utf8
"""@package business.resource.order_resource_extractor.OrderResourceExtractor
抽取Order中资源，用于取消订单过程中释放资源

释放资源步骤：

1. 从订单中识别促销信息；
2. 从订单中识别积分；
3. 从订单中识别优惠券；
4. 从订单中识别微众卡；

"""


import logging
from business import model as business_model 

from business.resource.integral_resource import IntegralResource
from business.mall.allocator.integral_resource_allocator import IntegralResourceAllocator
from business.mall.allocator.product_resource_allocator import ProductResourceAllocator
from business.resource.product_resource import ProductResource
from business.resource.products_resource import ProductsResource
from business.resource.coupon_resource import CouponResource
from business.mall.allocator.coupon_resource_allocator import CouponResourceAllocator
#from db.mall import models as mall_models
from business.mall.coupon.coupon import Coupon
from db.mall import promotion_models
from business.wzcard.wzcard_resource_allocator import WZCardResourceAllocator
from business.mall.log_operator import LogOperator
from business.wzcard.wzcard_resource import WZCardResource
from db.mall import models as mall_models

class OrderResourceExtractor(business_model.Model):
	"""
	Order资源抽取器
	"""
	__slots__=(

	)

	def __init__(self, webapp_owner, webapp_user):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user
		return

	def __extract_integral(self, order):
		"""
		抽取积分资源
		"""
		logging.info(u"order.integral={}".format(order.integral))
		resources = []

		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']
		# TODO: allocator中的resource_type是property，目前只能用这种ugly方式获取。后续考虑将resource_type改成staticmethod。
		resource_type = IntegralResourceAllocator(webapp_owner, webapp_user).resource_type
		integral_resource = IntegralResource.get({
				'webapp_owner': webapp_owner,
				'webapp_user': webapp_user,
				'type': resource_type
			})
		integral_resource.integral = order.integral
		integral_resource.integral_log_id = -1 # 表示不删除integral_log
		#integral_resource.money = order.integral_money

		resources.append(integral_resource)
		logging.info("extracted {} IntegralResources, resource_type={}".format(len(resources), resource_type))
		return resources


	def __extract_products_resource(self, order):
		"""
		抽取ProductsResource
		"""
		logging.info(u"to extract ProductsResource from order")

		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		# 从Order中恢复ProductsResource
		product_resources = []
		resource_type = ProductResourceAllocator(webapp_owner, webapp_user).resource_type

		order_products = order.products
		for order_product in order_products:
			purchase_count = order_product.purchase_count
			if order_product.model:
				model_id = order_product.model.id
			else:
				# 处理赠品的情况
				try:
					model_id = mall_models.ProductModel.select().dj_where(product_id=order_product.id, name='standard').first().id
				except:
					model_id = -1
			product_resource = ProductResource.get({
					'type': resource_type
				})
			product_resource.purchase_count = purchase_count
			product_resource.model_id = model_id
			product_resources.append(product_resource)

		products_resource = ProductsResource(product_resources, "order_products")
		return products_resource


	def __extract_coupon_resource(self, order):
		"""
		抽取订单优惠券资源
		"""
		logging.info(u"to extract CouponResource from order")
		resources = []

		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		resource_type = CouponResourceAllocator(webapp_owner, webapp_user).resource_type

		logging.info("coupon_id: {}".format(order.coupon_id))
		coupon = Coupon.from_id({
				'id': order.coupon_id
			})
		if coupon:
			resource = CouponResource.get({
					'type': resource_type,
				})

			logging.info('Coupon to be released: {}'.format(coupon.to_dict()))
			resource.coupon = coupon
			resource.money = coupon.money
			#resource.raw_status = coupon.status
			resource.raw_status = promotion_models.COUPON_STATUS_UNUSED
			if coupon.provided_time == promotion_models.DEFAULT_DATETIME:
				resource.raw_status = promotion_models.COUPON_STATUS_UNGOT
			resource.raw_member_id = coupon.member_id

			resources.append(resource)
		else:
			logging.info("`coupon` is None?")
			
		return resources


	def __extract_wzcard_resource(self, order):
		"""
		抽取使用的WZCardResource

		@todo 待重构，增加WZCardResourceExtractor
		"""
		logging.info(u"to extract WZCardResource from order, order_id:{}".format(order.order_id))
		resources = []

		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		resource_type = WZCardResourceAllocator(webapp_owner, webapp_user).resource_type

		# 从微众卡日志找出信息
		used_wzcards = LogOperator.get_used_wzcards(order.order_id)
		logging.info("extracted wzcard resource: {}".format(used_wzcards))

		info = mall_models.OrderCardInfo.select().dj_where(order_id=order.order_id).first()
		trade_id = info.trade_id
		resource = WZCardResource(resource_type, order.order_id, trade_id)
		resources.append(resource)

		return resource



	def extract(self, order):
		"""
		根据Order实例抽取资源，用于释放

		@param order Order实例
		@return Resource list
		"""
		logging.info(u"trying to extract resources from order id:{}".format(order.id))

		resources = []

		# 抽取积分资源
		integral_resources = self.__extract_integral(order)
		if integral_resources:
			resources.extend(integral_resources)

		products_resource = self.__extract_products_resource(order)
		if products_resource:
			resources.append(products_resource)

		# 抽取优惠券资源
		extracted_resources = self.__extract_coupon_resource(order)
		if extracted_resources:
			resources.extend(extracted_resources)

		# 抽取微众卡资源
		extracted_resource = self.__extract_wzcard_resource(order)
		if extracted_resource:
			resources.append(extracted_resource)

		logging.info(u"extracted {} resources".format(len(resources)))
		return resources

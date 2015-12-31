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
from db.mall import models as mall_models
from business.mall.coupon.coupon import Coupon
from db.mall import promotion_models

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
			model_id = order_product.model.id
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
			resource.raw_member_id = coupon.member_id

			resources.append(resource)
		else:
			logging.info("`coupon` is None?")
			
		return resources



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

		logging.info(u"extracted {} resources".format(len(resources)))
		return resources

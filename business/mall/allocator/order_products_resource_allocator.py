# -*- coding: utf-8 -*-
"""@package business.mall.allocator.OrderProductResourceAllocator
请求订单商品库存资源

"""
from collections import OrderedDict

from db.mall import models as mall_models

from business import model as business_model
from business.resource.products_resource import ProductsResource
from business.mall.allocator.product_resource_allocator import ProductResourceAllocator
from business.mall.merged_reserved_product import MergedReservedProduct
import logging
from business.mall.promotion.promotion_result import PromotionResult
from business.mall.promotion.promotion_failure import PromotionFailure

class OrderProductsResourceAllocator(business_model.Service):
	"""请求订单商品库存资源
	"""
	__slots__ = (
		'order'
		)

	def __init__(self, webapp_owner, webapp_user):
		business_model.Service.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

		self.context['resource2allocator'] = {}


	def release(self, product_resource):
		if not product_resource:
			logging.info(u"`product_resource` should not be None. It's meaningless.")
			return

		product_resource_allocator = ProductResourceAllocator.get()

		for resource in product_resource.resources:
			if not resource:
				continue
			logging.info(u'Resource type: {}'.format(resource.get_type()))
			product_resource_allocator.release(resource)

			#if resource.get_type() == business_model.RESOURCE_TYPE_PRODUCTS:
			#	release_resources.append(resource)

		#for release_resource in release_resources:
		#	resources = release_resource.resources
		#	for resource in resources:
		#		allocator = self.context['resource2allocator'].get(resource.model_id, None)
		#		if allocator:
		#			allocator.release()

	def __allocate_promotion(self, product):
		"""
		分配促销资源
		"""
		if product.has_expected_promotion() and not product.is_expected_promotion_active():
			return False, [PromotionFailure({
				"type": 'promotion:expired',
				"msg": u"该活动已经过期",
				"short_msg": u"已经过期"
			})]

		if not product.promotion:
			return True, PromotionResult()

		# 分配各种促销资源
		promotion_results = product.promotion.allocate(self.context['webapp_user'], product)
		has_failed_promotion_result = False
		for promotion_result in promotion_results:
			print promotion_result
			if not promotion_result.is_success:
				has_failed_promotion_result = True
			if promotion_result.need_disable_discount:
				product.disable_discount()

		if has_failed_promotion_result:
			return False, promotion_results
		else:
			return True, promotion_results

	def __supply_product_info_into_fail_reason(self, product, result):
		#如果失败原因中没有商品信息，则填充商品信息
		if (not 'id' in result) or (not result['id']):
			result['id'] = product.id
		if (not 'name' in result) or (not result['name']):
			result['name'] = product.name
		if (not 'stocks' in result) or (not result['stocks']):
			result['stocks'] = product.purchase_count
		if (not 'model_name' in result) or (not result['model_name']):
			result['model_name'] = product.model_name
		if (not 'pic_url' in result) or (not result['pic_url']):
			result['pic_url'] = product.thumbnails_url

	def __merge_different_model_product(self, products):
		"""
		将同一商品的不同规格的商品进行合并，主要合并

		Parameters
			[in] products: ReservedProduct对象集合

		Returns
			MergedReservedProduct对象集合
		"""
		id2product = OrderedDict()
		for product in products:
			merged_reserved_product = id2product.get(product.id, None)
			if not merged_reserved_product:
				merged_reserved_product = MergedReservedProduct()
				merged_reserved_product.add_product(product)
				id2product[product.id] = merged_reserved_product
			else:
				merged_reserved_product.add_product(product)

		return id2product.values()

	def allocate_resource(self, order, purchase_info):
		"""
		分配OrderProduct资源

		@return is_success, reasons, resource
		"""
		products = order.products
		#分配促销
		is_promotion_success = True
		promotion_reason = None
		merged_reserved_products = self.__merge_different_model_product(products)
		
		successed = True
		resources = []
		reasons = []
		for product in products:
			logging.info(u"try to allocate product: {}({})".format(product.name, product.id))
			product_resource_allocator = ProductResourceAllocator.get()
			successed_once, reason, resource = product_resource_allocator.allocate_resource(product)
			logging.info(u"success: {}, reason: {}, resource: {}".format(successed_once, reason, resource))

			if not successed_once:
				successed = False
				self.__supply_product_info_into_fail_reason(product, reason)
				if reason['type'] == 'product:is_off_shelve':
					if purchase_info.is_purchase_from_shopping_cart:
						reason['msg'] = u'有商品已下架<br/>2秒后返回购物车<br/>请重新下单'
					else:
						reason['msg'] = u'商品已下架<br/>2秒后返回商城首页'
				elif reason['type'] == 'product:not_enough_stocks':
					if purchase_info.is_purchase_from_shopping_cart:
						reason['msg'] = u'有商品库存不足<br/>2秒后返回购物车<br/>请重新下单'
					else:
						reason['msg'] = u'有商品库存不足，请重新下单'
				resources.append(resource)
				logging.info(u"adding reason: msg={}".format(reason['msg']))
				logging.info(u"appending reason: {}".format(reason))
				reasons.append(reason)
			else:
				resources.append(resource)
				self.context['resource2allocator'][resource.model_id] = product_resource_allocator

		if not successed:
			# TODO: 应该改成用ProductResourceAllocator释放
			resource = ProductsResource(resources, self.resource_type)
			self.release(resource)
			resources = None

		promotion_reasons = []
		updated_premium_products = []
		if successed:
			for merged_reserved_product in merged_reserved_products:
				__is_promotion_success, __promotion_reasons = self.__allocate_promotion(merged_reserved_product)
				if isinstance(__promotion_reasons,list):
					for __promotion_reason in __promotion_reasons:
						updated_premium_products.extend(__promotion_reason.updated_premium_products)
				if not __is_promotion_success:
					is_promotion_success = __is_promotion_success
					logging.info(u"appending reason: {}".format(promotion_reason))
					#merged_promotion_product = merged_reserved_product
					if len(merged_reserved_product.get_products()) > 1:
						for inner_reserved_product in merged_reserved_product.get_products():
							for __promotion_reason in __promotion_reasons:
								promotion_reason_dict = __promotion_reason.to_dict()
								promotion_reason_dict['id'] = None
								promotion_reason_dict['name'] = None
								promotion_reason_dict['stocks'] = None
								promotion_reason_dict['model_name'] = None
								promotion_reason_dict['pic_url'] = None
								self.__supply_product_info_into_fail_reason(inner_reserved_product, promotion_reason_dict)
								logging.info(u"adding reason: msg={}".format(promotion_reason_dict['msg']))
								promotion_reasons.append(promotion_reason_dict)
					else:
						for __promotion_reason in __promotion_reasons:
							promotion_reason_dict = __promotion_reason.to_dict()
							self.__supply_product_info_into_fail_reason(merged_reserved_product, promotion_reason_dict)
							logging.info(u"adding reason: msg={}".format(promotion_reason_dict['msg']))
							promotion_reasons.append(promotion_reason_dict)
			#has_real_fail_reason = len([reason for reason in promotion_reasons if reason['type'] != 'promotion:premium_sale:no_premium_product_stocks' and reason['type'] != 'promotion:premium_sale:not_enough_premium_product_stocks']) > 0
			if len(promotion_reasons) > 0:
				reasons.extend(promotion_reasons)
				for premium_product in updated_premium_products:
					mall_models.ProductModel.update(stocks=mall_models.ProductModel.stocks+premium_product['premium_count']).dj_where(product_id=premium_product['premium_product_id'], name='standard').execute()


		if not successed:
			return False, reasons, None
		elif not is_promotion_success:
			if resources:
				products_resource = ProductsResource(resources, self.resource_type)
				self.release(products_resource)
			return False, reasons, None
		resource = ProductsResource(resources, self.resource_type)
	 	return True, reasons, resource

	@property
	def resource_type(self):
		return "order_products"

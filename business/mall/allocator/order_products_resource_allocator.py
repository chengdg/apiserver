# -*- coding: utf-8 -*-
"""@package business.mall.allocator.OrderProductResourceAllocator
请求订单商品库存资源

"""
from business import model as business_model 
from business.resource.products_resource import ProductsResource
from business.mall.allocator.product_resource_allocator import ProductResourceAllocator
from business.mall.merged_reserved_product import MergedReservedProduct
from core.decorator import deprecated

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


	def release(self, resources):
		if not resources:
			return 

		release_resources = []
		for resource in resources:
			if resource.get_type() == business_model.RESOURCE_TYPE_PRODUCT:
				release_resources.append(resource)

		for release_resource in release_resources:
			resources = release_resource.resources

			for resource in resources:
				allocator = self.context['resource2allocator'].get(resource.model_id, None)
				if allocator:
					allocator.release()

	def __allocate_promotion(self, product):
		if product.has_expected_promotion() and not product.is_expected_promotion_active():
			return False, {
				"is_success": False,
				"type": 'promotion:expired',
				"msg": u"该活动已经过期",
				"short_msg": u"已经过期"
			}

		if not product.promotion:
			return True, {
				"is_success": True
			}

		promotion_result = product.promotion.allocate(self.context['webapp_user'], product)
		if not promotion_result.is_success:
			reason = {
				'type': promotion_result.type,
				'msg': promotion_result.msg,
				'short_msg': promotion_result.short_msg
			}
			if promotion_result.id:
				#TODO: 失败信息中带有product信息，目前是ugly的解决方案，等待后续优化
				reason.update(promotion_result.to_dict())
			return False, reason
		else:
			if promotion_result.need_disable_discount:
				#促销申请的结果要求禁用会员折扣
				product.disable_discount()

		return True, {
			"is_success": True
		}

	def __supply_product_info_into_fail_reason(self, product, result):
		if not 'id' in result:
			#如果失败原因中没有商品信息，则填充商品信息
			result['id'] = product.id
			result['name'] = product.name
			result['stocks'] = product.stocks
			result['model_name'] = product.model_name
			result['pic_url'] = product.thumbnails_url


	def allocate_resource(self, resources):
		"""
		根据extractor抽取出的资源信息申请资源
		"""
		successed = False
		#resources = []
		#for product in products:
		for resource in resources:
			# 找出商品类型的resource
			if resource.type != self.resource_type:
				continue

			# 从ProductResource资源中获取product
			product = resource.product
		 	product_resource_allocator = ProductResourceAllocator.get()
		 	successed, reason, resource = product_resource_allocator.allocate_resource(product)

		 	if not successed:
		 		self.__supply_product_info_into_fail_reason(product, reason)
		 		if reason['type'] == 'product:is_off_shelve':
		 			#if purchase_info.is_purchase_from_shopping_cart:
		 			if resource.is_purchase_from_shopping_cart:
		 				reason['msg'] = u'有商品已下架<br/>2秒后返回购物车<br/>请重新下单'
		 			else:
		 				reason['msg'] = u'商品已下架<br/>2秒后返回商城首页'
		 		elif reason['type'] == 'product:not_enough_stocks':
		 			#if purchase_info.is_purchase_from_shopping_cart:
		 			if resource.is_purchase_from_shopping_cart:
		 				reason['msg'] = u'有商品库存不足<br/>2秒后返回购物车<br/>请重新下单'
		 			else:
		 				reason['msg'] = u'有商品库存不足，请重新下单'
		 		self.release(resources)
		 		break
		 	else:
		 		resources.append(resource)
		 		self.context['resource2allocator'][resource.model_id] = product_resource_allocator

		if not successed:
			return False, reason, None

		resource = ProductsResource(resources)
	 	return True, reason, resource


	@deprecated
	def allocate_resource_old(self, order, purchase_info):
		#webapp_owner = self.context['webapp_owner']
		#webapp_user = self.context['webapp_user']

		# moved to ProductResourceExtractor
		# merged_reserved_products = self.__merge_different_model_product(products)

		successed = False
		resources = []
		for product in products:
		 	product_resource_allocator = ProductResourceAllocator.get()
		 	successed, reason, resource = product_resource_allocator.allocate_resource(product)

		 	if not successed:
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
		 		self.release(resources)
		 		break
		 	else:
		 		resources.append(resource)
		 		self.context['resource2allocator'][resource.model_id] = product_resource_allocator

		if not successed:
			return False, reason, None
		else:
			resource = ProductsResource(resources)
		 	return True, reason, resource

	@property
	def resource_type(self):
		return "order_products"
	
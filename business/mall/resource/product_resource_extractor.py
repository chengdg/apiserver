#coding: utf8
"""
商品资源抽取器
"""
from business import model as business_model 
from business.mall.reserved_product_repository import ReservedProductRepository
from business.mall.group_reserved_product_service import GroupReservedProductService
from business.resource.product_resource import ProductResource
from business.mall.merged_reserved_product import MergedReservedProduct
from business.mall.resource.resource_extractor import ResourceExtractor

class ProductResourceExtractor(ResourceExtractor):
	"""
	商品资源抽取器
	"""
	__slots__ = (
	)

	def __init__(self, webapp_owner, webapp_user):
		ResourceExtractor.__init__(self, webapp_owner, webapp_user)


	def __process_products(self, order, purchase_info):
		"""
		向order中添加products和product_groups

		@note 从OrderFactory迁移的代码
		"""
		webapp_owner = self.context['webapp_owner']
		webapp_user = self.context['webapp_user']

		#获得已预订商品集合
		reserved_product_repository = ReservedProductRepository.get({
			'webapp_owner': webapp_owner,
			'webapp_user': webapp_user
		})
		order.products = reserved_product_repository.get_reserved_products_from_purchase_info(purchase_info)

		#按促销进行product分组
		group_reserved_product_service = GroupReservedProductService.get(webapp_owner, webapp_user)
		order.product_groups = group_reserved_product_service.group_product_by_promotion(order.products)

		#对每一个group应用促销活动
		for promotion_product_group in order.product_groups:
			promotion_product_group.apply_promotion(purchase_info)
		return order


	def __merge_different_model_product(self, products):
		"""
		将同一商品的不同规格的商品进行合并，主要合并

		@param[in] products: ReservedProduct对象集合

		@return MergedReservedProduct对象集合
		"""
		id2product = {}
		for product in products:
			merged_reserved_product = id2product.get(product.id, None)
			if not merged_reserved_product:
				merged_reserved_product = MergedReservedProduct()
				merged_reserved_product.add_product(product)
				id2product[product.id] = merged_reserved_product
			else:
				merged_reserved_product.add_product(product)

		return id2product.values()


	def extract(self, order, purchase_info):
		"""
		根据purchase_info抽取resource

		每一种product是一个ProductResource

		@note 相当于MapReduce模型中的map

		@return Resource对象
		"""
		resources = []
		# 抽取商品资源信息

		# 在order中添加products、product_groups等信息
		order = self.__process_products(order, purchase_info)

		products = order.products

		#分配促销
		merged_reserved_products = self.__merge_different_model_product(products)
		for merged_reserved_product in merged_reserved_products:
			is_success, reason = self.__allocate_promotion(merged_reserved_product)
			if not is_success:
				self.__supply_product_info_into_fail_reason(merged_reserved_product, reason)
				return False, reason, None

			product_resource = ProductResource.get({
				'type': self.resource_type,
				})
			# allocator以resources作为输入，那么resource应包括allocator所需要的信息
			product_resource.product = merged_reserved_product
			product_resource.is_purchase_from_shopping_cart = purchase_info.is_purchase_from_shopping_cart
			resources.append(product_resource)
		
		return order, resources


	@property
	def resource_type(self):
		return business_model.RESOURCE_TYPE_PRODUCT		

	def merge_resources(self, order, resources):
		"""
		合并资源

		相当于MapReduce中的combiner
		"""
		return


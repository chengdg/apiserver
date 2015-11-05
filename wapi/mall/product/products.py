# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required
import resource

class Products(api_resource.ApiResource):
	"""
	商品
	"""
	app = 'mall'
	resource = 'products'


	@param_required(['category_id'])
	def get(args):
		"""
		获取商品详情

		@param category_id 商品分类ID
		"""
		category_id = args['category_id']
		oid = args['oid']
		wid = args['wid']

		products = resource.get('mall', 'products', {
			"oid": oid,
			"wid": wid,
			"category_id": category_id
		})
		return products
		# #print("in product(), product_id={}".format(product_id))
		# #return {"name": u"商品%s" % product_id}
		# product = mall_models.Product.get(id=product_id)
		# return Product.to_dict(product)
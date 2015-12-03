#coding: utf8
"""@package wapi.mall.a_product_review
商品评论暴露的API

"""

#import copy
#from datetime import datetime

from core import api_resource
from wapi.decorators import param_required
#from db.mall import models as mall_models
#from db.mall import promotion_models
#from utils import dateutil as utils_dateutil
#import resource
#from wapi.mall.a_purchasing import APurchasing as PurchasingApiResource
#from core.cache import utils as cache_utils
#from business.mall.order_factory import OrderFactory
#from business.mall.purchase_info import PurchaseInfo
#from business.mall.pay_interface import PayInterface
from business.mall.order_review import OrderReview
from business.mall.product_review import ProductReview
import logging
#from core.watchdog.utils import watchdog_info




class AProductReview(api_resource.ApiResource):
	"""
	单条商品评论
	"""
	app = 'mall'
	resource = 'product_review'	

	@param_required(['woid', 'product_id'])
	def get(args):
		"""
		获取一条商品评论

		@note 在原Webapp中，review是包括product detail(商品详情)的`product`中。见`request_util.py:get_product()`。获得`product`需要woid, product_id, member_grade_id, wuid四项参数。实际通过`mall/module_api.py:get_product_detail()`获得product detail。而`get_product_detail()`调用`get_webapp_product_detail()`组装product detail。
		在`get_product_detail_for_cache()`找到`product_review`
		"""
		webapp_owner = args['webapp_owner']
		product_id = args['product_id']

		product_review = ProductReview.from_id({
			'webapp_owner': webapp_owner,
			'product_id': product_id
			})
		return {
			'product_review': product_review.to_dict()
		}

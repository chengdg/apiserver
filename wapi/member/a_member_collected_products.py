# -*- coding: utf-8 -*-
import json

from core import api_resource
from wapi.decorators import param_required
from db.mall import models as mall_models
from utils import dateutil as utils_dateutil
#import resource
from business.mall.product import Product


class AMemberCollectedProduct(api_resource.ApiResource):
	"""
	会员收藏商品
	"""
	app = 'member'
	resource = 'collected_products'


	@param_required(['webapp_user'])
	def get(args):
		"""
		获取会员收藏的商品

		@param webapp_user 会员帐号信息

		"""

		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']
		#member = webapp_user.member
		products = webapp_user.collected_products
		#products = member.collected_products
		
		return {'products':products}





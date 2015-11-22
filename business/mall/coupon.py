# -*- coding: utf-8 -*-
"""@package business.mall.coupon
优惠券
"""

#import json
#import itertools

#from core import inner_resource
#from core import auth
#from core.cache import utils as cache_util
#import cache
from wapi.decorators import param_required
#from db.mall import models as mall_models
#import settings
from business import model as business_model

class Coupon(business_model.Model):
	"""
	优惠券
	"""

	@staticmethod
	@param_required(['webapp_owner_id', 'coupon_id'])
	def get(args):
		pass



# -*- coding: utf-8 -*-

import json
import itertools

from core import inner_resource
from core import auth
from cache import utils as cache_util
import cache
from wapi.decorators import param_required
from wapi.mall import models as mall_models
import settings


class Coupon(object):
	"""
	优惠券
	"""
	@staticmethod
	@param_required(['webapp_owner_id', 'coupon_id'])
	def get(args):
		pass
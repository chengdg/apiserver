# -*- coding: utf-8 -*-

import copy
from datetime import datetime

from core import api_resource
from wapi.decorators import param_required
from wapi.mall import models as mall_models
from wapi.mall import promotion_models
from utils import dateutil as utils_dateutil
import resource
from wapi.mall.a_purchasing import APurchasing as PurchasingApiResource
from core.cache import utils as cache_utils
from business.mall.order_factory import OrderFactory
from business.mall.purchase_info import PurchaseInfo
from business.mall.pay_interface import PayInterface

class AUserCenter(api_resource.ApiResource):
	"""
	个人中心
	"""
	app = 'user_center'
	resource = 'user_center'

	@param_required(['woid'])
	def get(args):
		"""
		获取个人中心
		"""
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']

		member = webapp_user.member
		member_data = {
			'user_icon': member.user_icon,
			'is_binded': member.is_binded,
			'username_for_html': member.username_for_html,
			'grade': member.grade,
			'history_order_count': member.history_order_count,
			'not_payed_order_count': member.not_payed_order_count,
			'not_ship_order_count': member.not_ship_order_count,
			'shiped_order_count': member.shiped_order_count,
			'review_count': member.review_count,
			'integral': member.integral,
			'wishlist_product_count': member.wishlist_product_count,
			'market_tools': member.market_tools
		}

		return member_data

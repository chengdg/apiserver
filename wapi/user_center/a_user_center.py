# -*- coding: utf-8 -*-

#import copy
from datetime import datetime

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
from business.mall.shopping_cart import ShoppingCart
from business.mall.review.waiting_review_orders import WaitingReviewOrders

from services.update_member_from_weixin.task import update_member_info

class AUserCenter(api_resource.ApiResource):
	"""
	个人中心
	"""
	app = 'user_center'
	resource = 'user_center'

	@param_required([])
	def get(args):
		"""
		获取个人中心
		"""
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']
		member = webapp_user.member

		today = datetime.now()
		today_str = datetime.today().strftime('%Y-%m-%d')
		if member.update_time.strftime("%Y-%m-%d") != today_str:
			update_member_info.delay(webapp_user.id, webapp_owner.id)

		shopping_cart = ShoppingCart.get_for_webapp_user({
			'webapp_user': args['webapp_user'],
			'webapp_owner': args['webapp_owner'],
		})
		shopping_cart_product_count = shopping_cart.product_count

		is_binded = webapp_user.is_binded
		if is_binded:
			phone = webapp_user.phone
		else:
			phone = ''

		#评价相关
		waiting_review_orders = WaitingReviewOrders.get_for_webapp_user({
			'webapp_owner': webapp_owner,
			'webapp_user': webapp_user
			})

		wishlist_product_count = waiting_review_orders.waiting_count()

		member_data = {
			'user_icon': webapp_user.user_icon,
			'is_binded': is_binded,
			'username_for_html': webapp_user.username_for_html,
			'grade': webapp_user.grade,
			'history_order_count': webapp_user.history_order_count,
			'not_payed_order_count': webapp_user.not_payed_order_count,
			'not_ship_order_count': webapp_user.not_ship_order_count,
			'shiped_order_count': webapp_user.shiped_order_count,
			'review_count': webapp_user.review_count,
			'integral': webapp_user.integral,
			'wishlist_product_count': wishlist_product_count,
			'market_tools': member.market_tools,
			'shopping_cart_product_count': shopping_cart_product_count,
			'phone': phone
		}

		return member_data



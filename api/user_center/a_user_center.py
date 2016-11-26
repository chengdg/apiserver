# -*- coding: utf-8 -*-

#import copy
import json
from datetime import datetime

from eaglet.core import api_resource
from eaglet.decorator import param_required
#from db.mall import models as mall_models
#from db.mall import promotion_models
#from util import dateutil as utils_dateutil
#import resource
#from api.mall.a_purchasing import APurchasing as PurchasingApiResource
#from eaglet.core.cache import utils as cache_utils
#from business.mall.order_factory import OrderFactory
#from business.mall.purchase_info import PurchaseInfo
#from business.mall.pay_interface import PayInterface
from business.mall.shopping_cart import ShoppingCart
from business.channel_qrcode.channel_distribution_qrcode import ChannelDistributionQrcodeSettings
from business.account.ad_clicked import AdClicked
from business.member_card.member_card import MemberCard
from services.update_member_from_weixin.task import update_member_info
from eaglet.core import watchdog
import uuid


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
		member_bind_channel_qrcode = ChannelDistributionQrcodeSettings.get_for_webapp_user({
			'webapp_user': args['webapp_user'],
			'webapp_owner': args['webapp_owner'],
		})
		if member_bind_channel_qrcode:
			is_bind_channel_qrcode = True
			total_reward = member_bind_channel_qrcode.will_return_reward
		else:
			is_bind_channel_qrcode = False
			total_reward = 0

		is_weizoom_mall = True if webapp_owner.mall_type == 1 else False
		is_vip = False
		if is_weizoom_mall:
			#ad  click 
			ad_clicked = AdClicked.from_member_id({
				"member_id":member.id
				})

			is_ad_clicked = True if ad_clicked else False

			member_card = MemberCard.from_member_id({
				"member_id": member.id
			})
			if member_card:
				is_vip = True
		else:
			is_ad_clicked = False

		member_data = {
			'user_icon': webapp_user.user_icon,
			'is_binded': is_binded,
			'username_for_html': webapp_user.username_for_html,
			'grade': webapp_user.grade.to_dict(),
			'history_order_count': webapp_user.history_order_count,
			'not_payed_order_count': webapp_user.not_payed_order_count,
			'not_ship_order_count': webapp_user.not_ship_order_count,
			'shiped_order_count': webapp_user.shiped_order_count,
			'review_count': webapp_user.review_count,
			'integral': webapp_user.integral,
			'wishlist_product_count': webapp_user.collected_product_count,
			'market_tools': member.market_tools,
			'shopping_cart_product_count': shopping_cart_product_count,
			'phone': phone,
			'is_bind_channel_qrcode': is_bind_channel_qrcode,
			'total_reward': total_reward,
			'is_ad_clicked': is_ad_clicked,
			'is_vip': is_vip,
			'is_weizoom_mall': is_weizoom_mall
		}

		return member_data



# -*- coding: utf-8 -*-
"""
个人中心-星级会员
"""
from eaglet.core import api_resource
from eaglet.decorator import param_required
from business.member_card.member_card import MemberCard

class ATengyiMemberCard(api_resource.ApiResource):
	"""
	腾易微众定制
	个人中心-星级会员
	"""
	app = 'member_card'
	resource = 'tengyi_member_card'

	@param_required([])
	def get(args):
		"""
		前台需要：推荐返利，商品返利，支付订单，订单退款
		"""
		webapp_user = args['webapp_user']
		member_id = webapp_user.member.id

		member_card = MemberCard.from_member_id({
			"member_id": member_id,
			"fill_options": {
				"with_price": True
			}
		})
		
		if member_card:
			data = {
				'card_number': member_card.card_number,
				'is_active': member_card.is_active,
				'remained_backcash_times': member_card.remained_backcash_times,
				'balance': member_card.balance,
				'card_name': member_card.card_name,
				'is_vip': True,
				'user_icon': webapp_user.user_icon,
				'username_for_html': webapp_user.username_for_html,
				'valid_time_to': member_card.valid_time_to,
				'interval_days': member_card.interval_days,
				'next_clear_time': member_card.next_clear_time,
				'bill_info': member_card.get_tengyi_bill_info()
			}
		else:
			data = {}
			
		return data

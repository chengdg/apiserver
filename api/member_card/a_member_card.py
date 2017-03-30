# -*- coding: utf-8 -*-
"""
个人中心-VIP会员
"""
from eaglet.core import api_resource
from eaglet.decorator import param_required
from business.member_card.member_card import MemberCard

class AMemberCard(api_resource.ApiResource):
	"""
	个人中心-VIP会员
	"""
	app = 'member_card'
	resource = 'member_card'

	@param_required([])
	def get(args):
		"""
		通过 个人中心-VIP会员 入口进入会员页面。通常情况下，只有绑定了手机号并且已经开通了的会员会进入到这个页面，
		但为了防止非会员通过别人直接分享链接或者其他方式直接打开这个页面，这里面再次对is_binded和is_vip进行了判断，
		如果is_binded为False，前端应该跳转到绑定手机号页面，
		如果is_vip为False，前端应该跳转到会员卡列表页面

		@param 无
		@return member_card dict
		"""
		webapp_user = args['webapp_user']
		is_binded = webapp_user.is_binded
		member_id = webapp_user.member.id

		member_card = MemberCard.from_member_id({
			"member_id": member_id,
			"fill_options": {
				"with_price": True
						}
		})
		
		if is_binded and member_card:
			data = {
				'card_number': member_card.card_number,
				'is_active': member_card.is_active,
				'remained_backcash_times': member_card.remained_backcash_times,
				'balance': member_card.balance,
				'card_name': member_card.card_name,
				'is_binded': is_binded,
				'is_vip': True,
				'user_icon': webapp_user.user_icon,
				'username_for_html': webapp_user.username_for_html,
				'valid_time_to': member_card.valid_time_to,
				'interval_days': member_card.interval_days,
				'next_clear_time': member_card.next_clear_time,
				'bill_info': member_card.get_bill_info()
			}
		else:
			data = {
				'is_binded': is_binded,
				'is_vip': False
			}
			
		return data

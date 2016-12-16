# -*- coding: utf-8 -*-
"""
我想买-查看采购进度
"""
from eaglet.core import api_resource
from eaglet.decorator import param_required
from business.member_card.want_to_buy import WantToBuy
from business.member_card.member_card import MemberCard

class APurchasingProgress(api_resource.ApiResource):
	"""
	我想买-查看采购进度
	"""
	app = 'member_card'
	resource = 'purchasing_progress'

	@param_required(['id'])
	def get(args):
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']
		id = args['id']
		is_binded = webapp_user.is_binded
		if not is_binded:  #如果没绑定手机则直接返回
			return {'is_binded': False}

		member_id = webapp_user.member.id
		member_card = MemberCard.from_member_id({
			"member_id": member_id
		})
		is_vip = True if member_card else False
		if not is_vip:  #如果不是会员则直接返回
			return {
				'is_binded': is_binded,
				'is_vip': is_vip
			}

		want_to_buy = WantToBuy.from_id({
				"id": id,
				"webapp_owner": webapp_owner
			})

		return {
			'is_binded': is_binded,
			'is_vip': is_vip,
			'data': want_to_buy.to_dict()
		}

# -*- coding: utf-8 -*-
"""
VIP会员-我想买-支持一下
"""
from eaglet.core import api_resource
from eaglet.decorator import param_required
from business.member_card.want_to_buy_support import WantToBuySupport
from business.member_card.want_to_buy import WantToBuy
from business.member_card.member_card import MemberCard

class AWantToBuySupport(api_resource.ApiResource):
	"""
	VIP会员-我想买-支持一下
	"""
	app = 'member_card'
	resource = 'want_to_buy_support'

	@param_required(['want_to_buy_id', 'content'])
	def put(args):
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']
		result = WantToBuySupport.create({
					'webapp_owner': webapp_owner,
					'webapp_user': webapp_user,
					'want_to_buy_id': args['want_to_buy_id'],
					'content': args['content']
				})

		if result:
			want_to_buy = WantToBuy.from_id({
					'webapp_owner': webapp_owner,
					'id': result.want_to_buy_id
				})
			want_to_buy.update_status()
			return result
		else:
			return 500, u'您已经支持过'

# -*- coding: utf-8 -*-
"""
VIP会员-我想买
"""
from eaglet.core import api_resource
from eaglet.decorator import param_required
from business.member_card.want_to_buy import WantToBuy
from business.member_card.member_card import MemberCard

class AWantToBuy(api_resource.ApiResource):
	"""
	VIP会员-我想买
	"""
	app = 'member_card'
	resource = 'want_to_buy'

	def get(args):
		"""
		查看单个“我想买”的详情，如果支持率达到100%就显示“查看采购进度”按钮，如果不是自己提交的我想买，则显示“支持一下”按钮

		@param id
		@return want_to_buy dict
		"""
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']
		id = args.get('id', 0)
		is_binded = webapp_user.is_binded

		member_id = webapp_user.member.id
		member_card = MemberCard.from_member_id({
			"member_id": member_id
		})
		is_vip = True if member_card else False

		is_can_support = False  #是否显示“支持一下”按钮
		is_show_view_progress = False  #是否显示“查看采购进度”按钮
		want_to_buy = None
		supports = None

		if id:
			want_to_buy = WantToBuy.from_id({
					"id": id,
					"webapp_owner": webapp_owner
				})

			if is_binded and is_vip and not want_to_buy.has_supported(member_id) and want_to_buy.member_id != member_id:
				is_can_support = True

			if is_binded and is_vip and want_to_buy.is_success:
				is_show_view_progress = True

			supports = want_to_buy.get_supports()

		return {
			'user_icon': webapp_user.user_icon,
			'user_name':webapp_user.username_for_html,
			'is_binded': is_binded,
			'is_vip': is_vip,
			'is_can_support': is_can_support,
			'is_show_view_progress': is_show_view_progress,
			'want_to_buy': want_to_buy,
			'supports': supports
		}


	@param_required(['source', 'pics', 'is_accept_other_brand'])
	def put(args):
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']

		owner_id = webapp_owner.id
		member_id = webapp_user.member.id

		result = WantToBuy.create({
					'webapp_owner': webapp_owner,
					'webapp_user': webapp_user,
					'source': args['source'],
					'product_name': args.get('product_name', ''),
					'pics': args['pics'],
					'is_accept_other_brand': int(args['is_accept_other_brand'])
				})

		return result

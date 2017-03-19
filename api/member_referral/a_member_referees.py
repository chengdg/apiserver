# -*- coding: utf-8 -*-
from eaglet.core import api_resource

from business.tengyi_member.tengyi_member import TengyiMember


class AMemberReferees(api_resource.ApiResource):
	"""
	腾易微众定制，我的推荐
	"""
	app = 'member_referral'
	resource = 'member_referees'

	def get(args):
		"""
		推荐人信息
		"""
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']
		member_id = webapp_user.member.id

		ty_member = TengyiMember.get(member_id)
		referees = ty_member.get_referees(webapp_owner, {
			'fill_member_info': True
		})

		vips = []
		not_vips = []
		for referee in referees:
			if referee.level == 0:
				not_vips.append({
					'member_id': referee.member_id,
					'member_name': referee.member_info['member_name'],
					'member_icon': referee.member_info['user_icon'],
					'created_at': referee.created_at.strftime('%Y/%m/%d'),
					'is_subscribed': referee.member_info['is_subscribed']
				})
			else:
				vips.append({
					'member_id': referee.member_id,
					'member_name': referee.member_info['member_name'],
					'member_icon': referee.member_info['user_icon'],
					'level': referee.level,
					'created_at': referee.created_at.strftime('%Y/%m/%d'),
					'is_subscribed': referee.member_info['is_subscribed']
				})
		return {
			'member_info': {
				'rebate_info': ty_member.get_rebated_details(webapp_owner),
				'rebate_plan': ty_member.get_rebate_plan()
			},
			'referees_info': {
				'vips': vips,
				'not_vips': not_vips
			}
		}



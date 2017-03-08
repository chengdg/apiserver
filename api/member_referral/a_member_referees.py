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

		referee = TengyiMember.get(member_id)
		referees = referee.get_referees(webapp_owner, {
			'fill_member_info': True
		})

		details = []
		for referee in referees:
			details.append({
				'member_id': referee.member_id,
				'member_name': referee.member_info['member_name'],
				'member_icon': referee.member_info['user_icon'],
				'level': referee.level,
				'created_at': referee.created_at.strftime('%Y/%m/%d')
			})
		return {
			'member_info': {
				'rebate_info': referee.get_rebated_details(webapp_owner)
			},
			'referees_info': details
		}



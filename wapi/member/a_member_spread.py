# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required
from utils import url_helper

import resource
from business.account.member_factory import MemberFactory
from business.account.member import Member
from business.account.system_account import SystemAccount
from business.spread.member_relations import MemberRelation
from business.spread.member_relations_factory import MemberRelatonFactory
from business.spread.member_clicked import MemberClickedUrl
from business.spread.member_clicked_factory import MemberClickedFactory
from business.spread.member_shared import MemberSharedUrl
from business.spread.member_shared_factory import MemberSharedUrlFactory
from business.spread.integral import Integral
from business.spread.member_spread import MemberSpread


class AMemberSpread(api_resource.ApiResource):
	"""
	会员关系
	"""
	app = 'member'
	resource = 'member_spread'

	@param_required(['fmt', 'url', 'webapp_user'])
	def put(args):
		"""
		创建会员关系

		@param mt 当前会员toke
		@param fmt 分享会员token
		@param url 当前url路径
		
		"""

		if not args['fmt'] or args['fmt'] == 'notfmt' or not args['url']:
			return {}

		"""
			TODO:
				将这部分加人到celery
		"""
		member = args['webapp_user'].member

		MemberSpread.process_member_spread({
			'webapp_owner': args['webapp_owner'],
			'webapp_user': args['webapp_user'],
			'fmt': args['fmt'],
			'url': args['url']
			})

		return {}
	
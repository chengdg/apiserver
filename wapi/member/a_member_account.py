# -*- coding: utf-8 -*-

import urllib
import urlparse
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

from wapi.user.access_token import AccessToken

class AMemberAccount(api_resource.ApiResource):
	"""
	会员相关账号
	"""
	app = 'member'
	resource = 'member_accounts'

	@param_required(['webapp_user'])
	def get(args):
		"""
		获取会员详情

		@param
		"""
		webapp_user = args['webapp_user']
		social_account = webapp_user.social_account

		data = {}
		data['webapp_user'] = webapp_user.to_dict()
		data['social_account'] = social_account.to_dict()

		return data


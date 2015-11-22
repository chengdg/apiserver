# -*- coding: utf-8 -*-

import json
from bs4 import BeautifulSoup
from datetime import datetime

from core import inner_resource
from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from wapi.mall import models as mall_models
from wapi.member import models as member_models
from wapi.user import models as user_models
from r_member_share_url import RMemberShareUrl
import settings

class RMemberRelations(inner_resource.Resource):
	"""
	与会员相关的账号，包括member, social_account, weapp_user
	"""
	app = 'member'
	resource = 'member_relations'

	@param_required(['member_id'])
	def get(args):
		member_id = args['member_id']
		member_relation_ids = [r.follower_member_id for r in member_models.MemberFollowRelation.select().dj_where(member_id=member_id)]

		return {'friend_ids':member_relation_ids}
		

	@param_required(['mt', 'fmt', 'is_fans', 'r_url'])
	def post(args):
		mt = args['mt']
		fmt = args['fmt']
		is_fans = args['is_fans']
		r_url = args.get('r_url', None)
		if mt == fmt or fmt == 'notfmt':
			return {"msg": "SUCCESS"}

		if is_fans and str(is_fans) == '1':
			is_fans = True
		else:
			is_fans = False
		"""
			TODO:
				将该处理放到celery
		"""
		print 'mmmmmmmmmmmmmmm', mt, fmt, r_url
		try:
			member = member_models.Member.get(token=mt)
			followed_member = member_models.Member.get(token=fmt)
		except:
			member = None
			followed_member = None
		print member, followed_member,'<<<<<<<<<<<<<<<<<'
		if member and followed_member and member.webapp_id == followed_member.webapp_id:
			if member_models.MemberFollowRelation.select().dj_where(member_id=member.id).count() == 0:
				member_models.MemberFollowRelation.create(
					member_id = member.id,
					follower_member_id = followed_member.id,
					is_fans = False
					)

				member_models.MemberFollowRelation.create(
					member_id = followed_member.id,
					follower_member_id = member.id,
					is_fans = is_fans
					)

			"""
				更新url pv 和 引流
				TODO： 放到celery里
			"""
			RMemberShareUrl.process_share_url_pv(r_url, followed_member.id, member.id, is_fans)

		return {"msg": "SUCCESS"}

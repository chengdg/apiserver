# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required
from utils import url_helper

import resource
from business.account.member_factory import MemberFactory
from business.account.member import Member
from business.account.social_account_info import SocialAccountInfo
from business.spread.member_relations import MemberRelation
from business.spread.member_relations_factory import MemberRelatonFactory
from business.spread.member_clicked import MemberClickedUrl
from business.spread.member_clicked_factory import MemberClickedFactory
from business.spread.member_shared import MemberSharedUrl
from business.spread.member_shared_factory import MemberSharedUrlFactory


class AMemberRelations(api_resource.ApiResource):
	"""
	会员关系
	"""
	app = 'member'
	resource = 'member_relations'

	# @param_required(['member_id'])
	# def get(args):
	# 	"""
	# 	获取好友ids

	# 	@param member_id 会员ID
	# 	"""
	# 	return resource.get('member', 'member_relations', {
	# 		"member_id": args['member_id']
	# 		#"wid": args['wid']
	# 	})

	@param_required(['mt', 'fmt', 'url'])
	def post(args):
		"""
		创建会员关系

		@param mt 当前会员toke
		@param fmt 分享会员token
		@param url 当前url路径
		
		"""


		"""
			TODO:
				将这部分加人到celery
		"""
		member = Member.from_token({
				"webapp_owner": args['webapp_owner'],
				'token': args['mt']
			})

		followed_member = Member.from_token({
				"webapp_owner": args['webapp_owner'],
				'token': args['fmt']
			})

		if member and followed_member and MemberRelation.validate(member.id, followed_member.id):
			member_relations_factory_obj = MemberRelatonFactory.create({
						"member_id":followed_member.id, 
						'follower_member_id':member.id, 
						"is_fans":False})
			member_relations_factory_obj.save()

		#处理分享链接
		url = url_helper.remove_querystr_filed_from_request_url(args['url'])
		shared_url_digest = url_helper.url_hexdigest(url)
		#判断是否已经点击 点击过不做处理
		if MemberClickedUrl.validate(shared_url_digest, followed_member.id, member.id):
			member_clicked_obj = MemberClickedFactory.create({
				'url_member_id': followed_member.id,
				'click_member_id': member.id,
				'url': url,
				'shared_url_digest': shared_url_digest
				})
			member_clicked_obj.save()

			#判断是否会员成功分享过链接
			if MemberSharedUrl.validate(followed_member.id, shared_url_digest):
				member_shared_factory_obj = MemberSharedUrlFactory.create({
					'member_id': followed_member.id,
					'url': url,
					'shared_url_digest': shared_url_digest,
					'followed': False
					}).save()
			else:
				member_shared_factory_obj = MemberSharedUrlFactory.create({
					'member_id': followed_member.id,
					'url': url,
					'shared_url_digest': shared_url_digest,
					'followed': False
					}).update()
		return {}
		# return resource.post('member', 'member_relations', {
		# 	"mt": args['mt'],
		# 	"fmt": args['fmt'],
		# 	"is_fans": args['is_fans'],
		# 	"r_url": args['r_url']
		# })


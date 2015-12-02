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

		is_fans = args.get('is_fans', False)
		"""
			TODO:
				将这部分加人到celery
		"""
		member = args['webapp_user'].member
		# member = Member.from_token({
		# 		"webapp_owner": args['webapp_owner'],
		# 		'token': args['mt']
		# 	})
		if member.token != args['fmt']:

			followed_member = Member.from_token({
					"webapp_owner": args['webapp_owner'],
					'token': args['fmt']
				})

			AMemberSpread.process_member_spread(args['webapp_owner'], args['webapp_user'], followed_member, args['url'])

		return {}
	
	@staticmethod
	def process_member_spread(webapp_owner, webapp_user, followed_member, shared_url, is_fans=False):
		member = webapp_user.member
		if not member or not followed_member or member.id == followed_member.id:
			return

		if MemberRelation.validate(member.id, followed_member.id):
			member_relations_factory_obj = MemberRelatonFactory.create({
						"member_id": followed_member.id, 
						'follower_member_id': member.id, 
						"is_fans": is_fans})
			member_relations_factory_obj.save()

		#处理分享链接
		url = url_helper.remove_querystr_filed_from_request_url(shared_url)
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
					'followed': is_fans
					}).save()
			else:
				member_shared_factory_obj =MemberSharedUrlFactory.create({
					'member_id': followed_member.id,
					'url': url,
					'shared_url_digest': shared_url_digest,
					'followed': is_fans
					}).update()

			#为点击增加积分
			if followed_member.is_subscribed:
				if webapp_owner.integral_strategy_settings:
					print webapp_owner.integral_strategy_settings.click_shared_url_increase_count, '<1<<<<<<<<'
					try:
						integral = Integral.from_model({
							'webapp_owner': webapp_owner, 
							'model': webapp_owner.integral_strategy_settings
							})
					except:
						integral = Integral.from_webapp_id({
							'webapp_owner': webapp_owner, 
							})
				else:
					integral = Integral.from_webapp_id({
						'webapp_owner': webapp_owner, 
						})
				if integral:
					Integral.increase_click_shared_url_count({
						'member': followed_member,
						'follower_member': member,
						'click_shared_url_increase_count': integral.click_shared_url_increase_count
						})
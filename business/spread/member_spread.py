# -*- coding: utf-8 -*-
"""@package business.spread.MemberSpread
会员传播
"""

from wapi.decorators import param_required
from utils import url_helper
import urlparse 

import settings
from business import model as business_model
from business.decorator import cached_context_property
from business.account.member_factory import MemberFactory
from business.account.member import Member
from business.account.system_account import SystemAccount
from business.spread.member_relations import MemberRelation
from business.spread.member_relations_factory import MemberRelatonFactory
from business.spread.member_clicked import MemberClickedUrl
from business.spread.member_clicked_factory import MemberClickedFactory
from business.spread.member_shared import MemberSharedUrl
from business.spread.member_shared_factory import MemberSharedUrlFactory
from business.account.integral import Integral
from business.account.webapp_user_factory import WebAppUserFactory
from business.account.webapp_user import WebAppUser
from business.account.system_account import SystemAccount

class MemberSpread(business_model.Model):
	"""
	会员传播
	"""
	__slots__ = (
	)
	

	@staticmethod
	@param_required(['webapp_owner', 'openid', 'for_oauth', 'url'])
	def process_openid_for(args):
		"""
		处理openid接口

		@param openid 公众号粉丝唯一标识
		@param webapp_owner webapp_owner
		@param url 当前url
		@param for_oauth 是否是授权是调用
		
		"""
		query_strings = dict(urlparse.parse_qs(urlparse.urlparse(args['url']).query))
		fmt = query_strings.get('fmt', None)
		#创建会员
		member = MemberFactory.create({
			"webapp_owner": args['webapp_owner'],
			"openid": args['openid'],
			"for_oauth": args['for_oauth']
			}).save()
		created = member.created

		if created:
			webapp_user = WebAppUserFactory.create({
				'webapp_owner': args['webapp_owner'],
				'member_id': member.id
				}).save()
		else:
			webapp_user = WebAppUser.from_member_id({
				'webapp_owner': args['webapp_owner'],
				'member_id': member.id
				})

		if not webapp_user:
			webapp_user = WebAppUserFactory.create({
				'webapp_owner': args['webapp_owner'],
				'member_id': member.id
				}).save()

		#创建关系
		"""
			将会员关系创建和url处理放到celery
		"""
		MemberSpread.process_member_spread({
			'webapp_owner':  args['webapp_owner'],
			'webapp_user': webapp_user,
			'fmt': fmt,
			'url': args['url'],
			'is_fans': created
			})

	

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'fmt', 'url'])
	#webapp_owner, webapp_user, followed_member, shared_url, is_fans=False
	def process_member_spread(args):
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']
		fmt = args['fmt']
		shared_url = args['url']
		is_fans = args.get('is_fans', False)

		member = webapp_user.member

		if member.token == fmt or fmt == 'notfmt':
			return

		followed_member = Member.from_token({
			"webapp_owner": webapp_owner,
			'token': fmt
		})
		
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
			MemberClickedFactory.create({
				'url_member_id': followed_member.id,
				'click_member_id': member.id,
				'url': url,
				'shared_url_digest': shared_url_digest
				}).save()
			
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


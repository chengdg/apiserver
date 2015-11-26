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

from wapi.user.access_token import AccessToken

class AMemberAccounts(api_resource.ApiResource):
	"""
	会员相关账号
	"""
	app = 'member'
	resource = 'member_accounts'

	@param_required(['openid', 'woid'])
	def get(args):
		"""
		获取会员详情

		@param id 商品ID
		"""

		"""
			微信api和watchdog 测试
			TODO：删掉
		"""
		# from wapi.user.weixin_models import WeixinMpUserAccessToken
		# from core.wxapi.weixin_api import weixin_api
		# mp_access_token = WeixinMpUserAccessToken.get(id=3)
		# wxapi = weixin_api(mp_access_token)
		# userinfo = wxapi.get_user_info(args['openid'])

		if args.has_key('webapp_user'):
			data = {}
			webapp_user = args['webapp_user']
			member =webapp_user.member
			webapp_user.member = member.to_dict()
			social_account = args['social_account']
		else:
			social_account_obj = SocialAccountInfo.get({
				'webapp_owner': args['webapp_owner'],
				'openid': args['openid']
			})
			webapp_user = social_account_obj.webapp_user
			webapp_user.member = webapp_user.member.to_dict()
			social_account = social_account_obj.social_account

		data = {}
		data['webapp_user'] = webapp_user.to_dict()
		data['social_account'] = social_account.to_dict()

		return data


	@param_required(['openid', 'woid', 'for_oauth', 'fmt', 'url'])
	def post(args):
		"""
		创建会员接口

		@param openid 公众号粉丝唯一标识
		@param wid wid
		@param fmt 分享会员token
		@param url 当前url
		@param for_oauth 是否是授权是调用
		
		"""
		#创建会员
		member = MemberFactory.create({
			"webapp_owner": args['webapp_owner'],
			"openid": args['openid'],
			"for_oauth": args['for_oauth']
			}).save()
		created = member.created
		#创建关系
		if args['fmt'] and args['fmt'] != 'notfmt' and args['fmt'] != member.token:
			try:
				followed_member = Member.from_token({
					"webapp_owner": args['webapp_owner'],
					'token': args['fmt']
				})
			except:
				followed_member = None

			"""
				将会员关系创建和url处理放到celery
			"""
			if followed_member and member and MemberRelation.validate(member.id, followed_member.id):
				member_relations_factory_obj = MemberRelatonFactory.create({
					"member_id":followed_member.id, 
					'follower_member_id':member.id, 
					"is_fans":created})
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
							'followed': created
							}).save()
					else:
						member_shared_factory_obj = MemberSharedUrlFactory.create({
							'member_id': followed_member.id,
							'url': url,
							'shared_url_digest': shared_url_digest,
							'followed': created
							}).update()

		social_account_obj = SocialAccountInfo.get({
				'webapp_owner': args['webapp_owner'],
				'openid': args['openid']
			})
		data = {}
		webapp_user = social_account_obj.webapp_user
		webapp_user.member = webapp_user.member.to_dict()

		data['webapp_user'] = webapp_user.to_dict()
		data['social_account'] = social_account_obj.social_account.to_dict()

		#创建会员成功后重新设置AccessToken

		access_token = AccessToken.get({
			'webapp_owner_id': args['webapp_owner'].id,
			'openid': args['openid']
			})
		data.update(access_token)

		return data




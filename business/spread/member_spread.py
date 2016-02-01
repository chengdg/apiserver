# -*- coding: utf-8 -*-
"""@package business.spread.MemberSpread
会员传播
"""

from wapi.decorators import param_required
from utils import url_helper
import urlparse 

from core.watchdog.utils import watchdog_alert, watchdog_warning, watchdog_error
from core.exceptionutil import unicode_full_stack

import settings
from db.member import models as member_models
from db.mall import models as mall_models

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
		if fmt:
			fmt = fmt[0]
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
		if fmt:
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
		
		is_fans = args.get('is_fans', False)

		url_obj = urlparse.urlparse(args['url'])

		if url_obj.query:
			shared_url = url_obj.path + '?' + url_obj.query
		else:
			shared_url = url_obj.path

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



	@staticmethod
	@param_required(['order_id', 'webapp_user', 'url'])
	def record_order_from_spread(args):
		"""静态方法 记录通过订单

		@param[in] order_id 订单id
		@param[in] webapp_user 当前下单用户
		@param[in] url: 通过分享来的url
		"""
		webapp_user = args['webapp_user']
		shared_url = args['url']
		order_id = args['order_id']
		
		#TODO 从url中解析出来fmt
		member = webapp_user.member

		query_strings_dict = dict(urlparse.parse_qs(urlparse.urlparse(shared_url).query))
		fmt = query_strings_dict.get('fmt', None)
		if fmt:
			fmt = fmt[0]
			if fmt.find(',') > -1:
				fmt = fmt.split(',')[0]
		if member.token == fmt or fmt == 'notfmt':
			return
		
		shared_url = url_helper.remove_querystr_filed_from_request_url(shared_url)
		if fmt and fmt != webapp_user.member.token:
			a = mall_models.MallOrderFromSharedRecord.create(order_id=order_id, fmt=fmt, url=shared_url)
		# 更新leader_to_buy 放到会支付成功后 或者异步里

	@staticmethod
	@param_required(['order_id', 'webapp_user'])
	def process_order_from_spread(args):
		"""静态方法 订单完成后处理分享链接相关

		@param[in] order_id 订单id
		@param[in] webapp_user 当前下单用户
		"""
		order_id = args['order_id']
		webapp_user = args['webapp_user']

		mall_order_from_shared = mall_models.MallOrderFromSharedRecord.select().dj_where(order_id=order_id).first()
		if mall_order_from_shared:
			shared_url = mall_order_from_shared.url
			fmt = mall_order_from_shared.fmt

			if shared_url and fmt:
				try:
					followed_member = member_models.Member.get(token=fmt)
					member_models.MemberSharedUrlInfo.update(leadto_buy_count = member_models.MemberSharedUrlInfo.leadto_buy_count + 1).dj_where(shared_url=shared_url,).execute()

					mall_order_from_shared.is_updated = True
					mall_order_from_shared.save()
				except:
					notify_message = u"process_order_from_spread cause:\n{}, fmt:{}".format(unicode_full_stack(), fmt)
					watchdog_error(notify_message)	
					print notify_message
				
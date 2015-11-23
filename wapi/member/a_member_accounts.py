# -*- coding: utf-8 -*-

from core import api_resource
from wapi.decorators import param_required

import resource
from business.account.member_factory import MemberFactory

class AMemberAccounts(api_resource.ApiResource):
	"""
	会员相关账号
	"""
	app = 'member'
	resource = 'member_accounts'

	@param_required(['openid', 'wid'])
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

		#return {}
		return resource.get('member', 'member_accounts', {
			"openid": args['openid'],
			"wid": args['wid']
		})

	@param_required(['openid', 'woid', 'for_oauth', 'fmt', 'r_url'])
	def post(args):
		"""
		创建会员接口

		@param openid 公众号粉丝唯一标识
		@param wid wid
		@param fmt 分享会员token
		@param r_url 当前url
		@param for_oauth 是否是授权是调用
		
		"""

		member = MemberFactory.create({
			"webapp_owner": args['webapp_owner'],
			"openid": args['openid'],
			"for_oauth": args['for_oauth']
			})
		member.save()
		created = member.created
		print 'member created::::', created

		
		print u'create 关系 '

		return {}
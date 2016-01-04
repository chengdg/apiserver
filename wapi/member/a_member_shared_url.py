# -*- coding: utf-8 -*-

import urllib
import urlparse
from core import api_resource
from wapi.decorators import param_required
from utils import url_helper

from business.spread.member_shared import MemberSharedUrl
from business.spread.member_shared_factory import MemberSharedUrlFactory


class AMemberSharedUrl(api_resource.ApiResource):
	"""
	会员分享链接
	"""
	app = 'member'
	resource = 'shared_url'

	@param_required(['webapp_user', 'shared_url', 'title'])
	def put(args):
		"""
		创建会员分享链接

		@param
		"""
		webapp_user = args['webapp_user']
		shared_url = args['shared_url']
		title = args['title']
		#处理分享链接
		url = url_helper.remove_querystr_filed_from_request_url(shared_url)
		shared_url_digest = url_helper.url_hexdigest(url)

		if MemberSharedUrl.validate(webapp_user.member.id, shared_url_digest):
			member_shared_factory_obj = MemberSharedUrlFactory.create({
				'member_id': webapp_user.member.id,
				'url': url,
				'shared_url_digest': shared_url_digest,
				'followed': False,
				'title': title
				}).save()

		return {
			'success': True
		}



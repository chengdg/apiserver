# -*- coding: utf-8 -*-

import json
import urllib
import hashlib
from bs4 import BeautifulSoup
from datetime import datetime
from urlparse import parse_qs, urlparse

from core import inner_resource
from wapi.decorators import param_required
from wapi import wapi_utils
from cache import utils as cache_util
from wapi.mall import models as mall_models
from wapi.member import models as member_models
from wapi.user import models as user_models
import settings

class RMemberShareUrl(inner_resource.Resource):
	"""
	与会员相关的分享url信息
	"""
	app = 'member'
	resource = 'member_share_url'

	@param_required(['member_id'])
	def get(args):
		member_id = args['member_id']
		member_relation_ids = [r.follower_member_id for r in member_models.MemberFollowRelation.select().dj_where(member_id=member_id)]

		return {'friend_ids':member_relation_ids}
		

	@param_required(['r_url', 'umt', 'cmt', 'order_id'])
	def post(args):
		"""
			r_url: click_member_id 点击的url
			umt: url 所属会员id
			cmt: 点击url的会员id
		"""
		r_url = args['r_url']
		umt = args['umt']
		cmt = args['cmt']
		order_id = args['order_id']

		try:
			url_member = member_models.Member.get(token=umt)
			click_member = member_models.Member.get(token=cmt)
		except:
			url_member = None
			click_member = None
		print ')))))))))))))))))))))))>>>>', url_member, click_member
		if url_member and click_member:
			if str(order_id) != '-1':
				if member_models.MallOrderFromSharedRecord.select().dj_where(order_id = order_id, fmt = umt).count() == 0:
					#处理通过分享链接购买
					RMemberShareUrl.process_share_url_lead_to_buy(r_url, url_member.id, click_member.id)

					#记录通过分享链接下的关系
					member_models.MallOrderFromSharedRecord.create(
						order_id = order_id,
						fmt = umt,
						)
			else:
				RMemberShareUrl.process_share_url_pv(r_url, url_member.id, click_member.id)

		return {"msg": "SUCCESS"}

	@staticmethod
	def process_share_url_pv(r_url, url_member_id, click_member_id, follows=True):
		url = RMemberShareUrl.remove_querystr_filed_from_request_url(r_url)
		hexdigest_url = RMemberShareUrl.url_hexdigest(url)
		if member_models.MemberClickedUrl.select().dj_where(url_digest=hexdigest_url, mid=click_member_id, followed_mid=url_member_id).count() == 0:
			member_models.MemberClickedUrl.create(
				url = url,
				url_digest = hexdigest_url,
				mid = click_member_id,
				followed_mid = url_member_id
				)
			if member_models.MemberSharedUrlInfo.select().dj_where(member_id=url_member_id, shared_url_digest=hexdigest_url).count() > 0:
				if follows:
					update = member_models.MemberSharedUrlInfo.update(pv=member_models.MemberSharedUrlInfo.pv+1).dj_where(member_id=url_member_id,shared_url_digest=hexdigest_url)
				else:
					update = member_models.MemberSharedUrlInfo.update(pv=member_models.MemberSharedUrlInfo.pv+1).dj_where(member_id=url_member_id,shared_url_digest=hexdigest_url)
				update.execute()
			else:
				member_models.MemberSharedUrlInfo.create(
					member = url_member_id,
					shared_url = url,
					shared_url_digest = hexdigest_url,
					pv = 1,
					leadto_buy_count = 0,
					)

			"""
				TODO：处理积分
			"""

	@staticmethod
	def process_share_url_lead_to_buy(r_url, url_member_id, click_member_id):
		url = RMemberShareUrl.remove_querystr_filed_from_request_url(r_url)
		hexdigest_url = RMemberShareUrl.url_hexdigest(url)

		if member_models.MemberSharedUrlInfo.select().dj_where(member_id=url_member_id, shared_url_digest=hexdigest_url).count() > 0:
			update = member_models.MemberSharedUrlInfo.update(leadto_buy_count=member_models.MemberSharedUrlInfo.leadto_buy_count+1).dj_where(member_id=url_member_id, shared_url_digest=hexdigest_url)
			update.execute()
		else:
			member_models.MemberSharedUrlInfo.create(
				member = url_member_id,
				shared_url = url,
				shared_url_digest = hexdigest_url,
				pv = 1,
				leadto_buy_count = 1,
				)



	@staticmethod
	def remove_querystr_filed_from_request_url(url):
		if url.find('?') != -1:
			path_list = url.split('?')
			path_url = url.split('?')[0]
			query_str = url.split('?')[1]
		else:
			path_url = url
			query_str = []

		ignore_key = ['from', 'isappinstalled', 'code', 'state', 'appid', 'workspace_id']
		parse_dict = parse_qs(urlparse(query_str).query)
		if not parse_dict:
			return url
		new_data = {}
		for key, value in parse_dict.items():
			if key not in ignore_key:
				new_data[key] = value

		sorted(new_data.iteritems(), key=lambda a:a[0])
		return '%s?%s' % (path_url, urllib.urlencode(new_data, doseq=True))

	@staticmethod
	def url_hexdigest(url):
		return hashlib.md5(url).hexdigest()
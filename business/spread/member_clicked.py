# -*- coding: utf-8 -*-
"""@package business.spread.MemberRelation
会员
"""

#import json
#from bs4 import BeautifulSoup
#import math
#from datetime import datetime

#from wapi.decorators import param_required
##from wapi import wapi_utils
#from cache import utils as cache_util
#from wapi.mall import models as mall_models
#from wapi.mall import promotion_models
from db.member import models as member_models
#import resource
#from core.watchdog.utils import watchdog_alert
from business import model as business_model
#import settings
from business.decorator import cached_context_property
from utils import emojicons_util

class MemberClickedUrl(business_model.Model):
	"""
	会员点击url
	"""
	__slots__ = (
	)

	# @staticmethod
	# def from_models(query):
	# 	pass

	# @staticmethod
	# def from_model(webapp_owner, model):
	# 	member = Member(webapp_owner, model)
	# 	member._init_slot_from_model(model)

	# 	return member

	# @staticmethod
	# def from_id(member_id, webapp_owner):
	# 	try:
	# 		member_db_model = member_models.Member.get(id=member_id)
	# 		return Member.from_model(member_db_model, webapp_owner)
	# 	except:
	# 		return None

	def __init__(self, member_id, follower_member_id,):
		business_model.Model.__init__(self)

	@staticmethod
	def validate(url_digest, url_member_id, click_member_id):
		return member_models.MemberClickedUrl.select().dj_where(url_digest=url_digest, mid=click_member_id, followed_mid=url_member_id).count() == 0

	@staticmethod
	def empty_member_click_url():
		"""工厂方法，创建空的member_click_url对象

		@return MemberClickedUrl
		"""
		member_click_url = MemberClickedUrl(None, None)
		return member_click_url

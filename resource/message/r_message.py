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
from core.cache import utils as cache_util
from wapi.mall import models as mall_models
from wapi.member import models as member_models
from wapi.user import models as user_models
import settings

class RMessage(inner_resource.Resource):
	"""
	与消息的账号
	"""
	app = 'message'
	resource = 'message_messages'

	@param_required(['member_id'])
	def get(args):
		
		return {"result": "SUCCESS"}
		

	@param_required(['type', 'openid', 'appid', 'content'])
	def post(args):
		
		return {"result": "SUCCESS"}

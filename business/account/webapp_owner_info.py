# -*- coding: utf-8 -*-
"""@package business.account.webapp_owner_info
webapp owner的信息

"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
from db.mall import promotion_models
from db.account import models as account_models
import resource
from db.mall import models as mall_models
from db.mall import promotion_models
from db.account import models as account_models
from db.account import weixin_models as weixin_user_models
from db.account import webapp_models as webapp_models
from db.member import models as member_models
import settings
from core.watchdog.utils import watchdog_alert, watchdog_warning, watchdog_error
from core.exceptionutil import unicode_full_stack
from business import model as business_model



class WebAppOwnerInfo(business_model.Model):
	"""
	webapp owner的信息
	"""
	__slots__ = (
		'red_envelope',
		'global_navbar',
		'integral_strategy_settings',
		'pay_interfaces',
		'is_weizoom_card_permission',
		'qrcode_img',
		'member2grade',
		'member_grades'
	)

	@staticmethod
	@param_required(['woid'])
	def get(args):
		"""工厂方法

		@param[in] woid

		@return WebAppOwnerInfo对象
		"""
		webapp_owner_info = WebAppOwnerInfo(args['woid'])
		return webapp_owner_info

	def __init__(self, webapp_owner_id):
		business_model.Model.__init__(self)
		obj = self.__get_from_cache(webapp_owner_id)
		for slot in self.__slots__:
			setattr(self, slot, getattr(obj, slot, None))

	def __get_red_envelope_for_cache(self, webapp_owner_id):
		def inner_func():
			red_envelope = list(promotion_models.RedEnvelopeRule.select().dj_where(owner=webapp_owner_id, status=True,receive_method=False))
			result = {}
			if len(red_envelope):
				red_envelope = red_envelope[0]
				coupon_rule = promotion_models.CouponRule.select().dj_where(id=red_envelope.coupon_rule_id)
				if len(coupon_rule) and coupon_rule[0].remained_count > 0:
					red_envelope.coupon_rule = {'end_date': coupon_rule[0].end_date}
				else:
					red_envelope.coupon_rule = None
				result = red_envelope.to_dict('coupon_rule')
			return { 'value' : result }
		return inner_func

	def __get_webapp_owner_info_from_db(self, webapp_owner_id):
		def inner_func():
			#user profile
			user_profile = account_models.UserProfile.get(user=webapp_owner_id)
			webapp_id = user_profile.webapp_id

			#mpuser preview info
			try:
				mpuser = weixin_user_models.WeixinMpUser.get(owner=webapp_owner_id)
				mpuser_preview_info = weixin_user_models.MpuserPreviewInfo.get(mpuser=mpuser.id)
				try:
					weixin_mp_user_access_token = weixin_user_models.WeixinMpUserAccessToken.get(mpuser=mpuser.id)
				except:
					weixin_mp_user_access_token = weixin_user_models.WeixinMpUserAccessToken()
			except:
				error_msg = u"获得user('{}')对应的mpuser_preview_info构建cache失败, cause:\n{}"\
						.format(webapp_owner_id, unicode_full_stack())
				watchdog_warning(error_msg, user_id=webapp_owner_id)
				mpuser_preview_info = weixin_user_models.MpuserPreviewInfo()
				weixin_mp_user_access_token = weixin_user_models.WeixinMpUserAccessToken()
				mpuser = weixin_user_models.WeixinMpUser()

			#webapp
			try:
				webapp = webapp_models.WebApp.get(owner=webapp_owner_id)
			except:
				error_msg = u"获得user('{}')对应的webapp构建cache失败, cause:\n{}"\
						.format(webapp_owner_id, unicode_full_stack())
				watchdog_error(error_msg, user_id=webapp_owner_id, noraise=True)
				webapp = webapp_models.WebApp()

			#integral strategy
			try:
				integral_strategy_settings = member_models.IntegralStrategySttings.get(webapp_id=webapp_id)
			except:
				error_msg = u"获得user('{}')对应的IntegralStrategySttings构建cache失败, cause:\n{}"\
						.format(webapp_owner_id, unicode_full_stack())
				watchdog_error(error_msg, user_id=webapp_owner_id, noraise=True)
				integral_strategy_settings = member_models.IntegralStrategySttings()

			#member grade
			try:
				member_grades = [member_grade.to_dict() for member_grade in member_models.MemberGrade.select().dj_where(webapp_id=webapp_id)]
			except:
				error_msg = u"获得user('{}')对应的MemberGrade构建cache失败, cause:\n{}"\
						.format(webapp_owner_id, unicode_full_stack())
				watchdog_error(error_msg, user_id=webapp_owner_id, noraise=True)
				member_grades = []

			#pay interface
			try:
				pay_interfaces = [pay_interface.to_dict() for pay_interface in mall_models.PayInterface.select().dj_where(owner_id=webapp_owner_id)]
			except:
				error_msg = u"获得user('{}')对应的PayInterface构建cache失败, cause:\n{}"\
						.format(webapp_owner_id, unicode_full_stack())
				watchdog_error(error_msg, user_id=webapp_owner_id, noraise=True)
				pay_interfaces = []

			# 微众卡权限
			has_permission = account_models.AccountHasWeizoomCardPermissions.is_can_use_weizoom_card_by_owner_id(webapp_owner_id)

			try:
				operation_settings = account_models.OperationSettings.get_settings_for_user(webapp_owner_id)
			except:
				error_msg = u"获得user('{}')对应的OperationSettings构建cache失败, cause:\n{}"\
						.format(webapp_owner_id, unicode_full_stack())
				watchdog_error(error_msg, user_id=webapp_owner_id, noraise=True)
				operation_settings = account_models.OperationSettings()

			#全局导航
			try:
				global_navbar = account_models.TemplateGlobalNavbar.get_object(webapp_owner_id)
			except:
				global_navbar = account_models.TemplateGlobalNavbar()

			try:
				auth_appid = weixin_user_models.ComponentAuthedAppid.select().dj_where(user_id=webapp_owner_id)[0]
				auth_appid_info = weixin_user_models.ComponentAuthedAppidInfo.select().dj_where(auth_appid=auth_appid)[0]
			except:
				auth_appid_info = weixin_user_models.ComponentAuthedAppidInfo()
				
		
			return {
				'value': {
					'weixin_mp_user_access_token': weixin_mp_user_access_token.to_dict(),
					"mpuser_preview_info": mpuser_preview_info.to_dict(),
					'webapp': webapp.to_dict(),
					'user_profile': user_profile.to_dict(),
					'mpuser': mpuser.to_dict(),
					'integral_strategy_settings': integral_strategy_settings.to_dict(),
					'member_grades': member_grades,
					'pay_interfaces': pay_interfaces,
					'has_permission': has_permission,
					'operation_settings': operation_settings.to_dict(),
					'global_navbar': global_navbar.to_dict(),
					'auth_appid_info': auth_appid_info.to_dict()
				}
			}
		return inner_func

	def __get_from_cache(self, woid):
		"""
		webapp_cache.get_webapp_owner_info
		"""
		webapp_owner_id = woid
		webapp_owner_info_key = 'webapp_owner_info_{wo:%s}' % webapp_owner_id
		red_envelope_key = 'red_envelope_{wo:%s}' % webapp_owner_id
		key_infos = [{
			'key': webapp_owner_info_key,
			'on_miss': self.__get_webapp_owner_info_from_db(webapp_owner_id)
		},{
			'key': red_envelope_key,
			'on_miss': self.__get_red_envelope_for_cache(webapp_owner_id)

		}]
		data = cache_util.get_many_from_cache(key_infos)
		red_envelope = data[red_envelope_key]
		data = data[webapp_owner_info_key]

		obj = cache_util.Object()
		obj.mpuser_preview_info = weixin_user_models.MpuserPreviewInfo.from_dict(data['mpuser_preview_info'])
		obj.app = webapp_models.WebApp.from_dict(data['webapp'])

		obj.user_profile = account_models.UserProfile.from_dict(data['user_profile'])
		obj.mpuser = weixin_user_models.WeixinMpUser.from_dict(data['mpuser'])
		obj.weixin_mp_user_access_token = weixin_user_models.WeixinMpUserAccessToken.from_dict(data['weixin_mp_user_access_token'])
		obj.integral_strategy_settings = member_models.IntegralStrategySttings.from_dict(data['integral_strategy_settings'])
		obj.member_grades = member_models.MemberGrade.from_list(data['member_grades'])
		obj.member2grade = dict([(grade.id, grade) for grade in obj.member_grades])
		#obj.pay_interfaces = mall_models.PayInterface.from_list(data['pay_interfaces'])
		obj.pay_interfaces = data['pay_interfaces']
		obj.is_weizoom_card_permission = data['has_permission']
		obj.operation_settings = account_models.OperationSettings.from_dict(data['operation_settings'])
		obj.red_envelope = red_envelope
		obj.global_navbar = account_models.TemplateGlobalNavbar.from_dict(data['global_navbar'])
		obj.auth_appid_info = weixin_user_models.ComponentAuthedAppidInfo.from_dict(data['auth_appid_info'])
		if  obj.auth_appid_info:
			obj.qrcode_img = obj.auth_appid_info.qrcode_url
		else:
			obj.qrcode_img = ''

		return obj






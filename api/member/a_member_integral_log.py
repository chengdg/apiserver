# -*- coding: utf-8 -*-
"""@package apimember.a_member_integral_log
积分日志API

"""

from eaglet.core import api_resource
from eaglet.decorator import param_required
#import resource
from business.account.integral_logs import IntegralLogs


class AMemberIntegralLog(api_resource.ApiResource):
	"""
	积分日志
	"""
	app = 'member'
	resource = 'integral_log'


	@param_required(['webapp_owner', 'webapp_user'])
	def get(args):
		# print '>>>>>>>>>>>>>>>>>>>>'
		# print args
		# print args['webapp_owner']
		# print args['webapp_user']
		# print '>>>>>>>>>>>>>>>>>>>>>'
		integral_logs = IntegralLogs.get({
				'webapp_owner': args['webapp_owner'], 
				'webapp_user': args['webapp_user']
				})


		return {
			'integral_logs': integral_logs.integral_logs
		}
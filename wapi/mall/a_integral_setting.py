# -*- coding: utf-8 -*-
"""@package wapi.mall.a_integral_setting
积分配置API

"""

from core import api_resource
from wapi.decorators import param_required
#import resource
from business.account.integral import Integral


class AIntegralSetting(api_resource.ApiResource):
	"""
	积分配置信息
	"""
	app = 'mall'
	resource = 'integral_setting'


	@param_required(['webapp_owner', 'webapp_user'])
	def get(args):
		"""
		@param 无
		@return  {'integral_strategy_setting': integral.to_dict()}
		"""
		integral = Integral.from_webapp_id({
					'webapp_owner': args['webapp_owner'], 
					})

		return {
			'integral_strategy_setting': integral.to_dict()
		}

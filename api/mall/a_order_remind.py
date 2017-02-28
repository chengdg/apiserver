# -*- coding: utf-8 -*-
"""@package api.mall.a_order_remind
催单接口

"""

from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.mall.order_remind import OrderRemind
#from eaglet.core import watchdog

class AOrderRemind(api_resource.ApiResource):
	"""
	用户催单
	"""
	app = 'mall'
	resource = 'order_remind'

	@param_required(['order_id'])
	def put(args):
		"""
		创建评论
		"""
		webapp_owner = args['webapp_owner']
		order_id = args['order_id']
		webapp_id = webapp_owner.webapp_id

		is_sucess = OrderRemind.create({
			'webapp_id': webapp_id,
			'order_id': order_id
		})

		return is_sucess

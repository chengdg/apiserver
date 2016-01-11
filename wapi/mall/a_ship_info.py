# -*- coding: utf-8 -*-
from core import api_resource
from core.watchdog.utils import watchdog_error
from wapi.decorators import param_required


class AShipInfo(api_resource.ApiResource):
	"""
	收货地址
	"""
	app = 'mall'
	resource = 'ship_info'

	@param_required(['ship_id', 'ship_name', 'ship_address', 'ship_tel', 'area'])
	def post(args):
		"""
		@brief 修改收货地址
		@param ship_id
		@param ship_name
		@param ship_address
		@param ship_tel
		@param area
		@return {result:True}
		"""
		webapp_user = args['webapp_user']
		ship_info_id = int(args['ship_id']),
		new_ship_info = {
			'ship_name': args['ship_name'],
			'ship_address': args['ship_address'],
			'ship_tel': args['ship_tel'],
			'area': args['area']
		}
		area = args['area']
		if '_' not in area:
			webapp_user_id = args['webapp_user'].id
			message = u'错误的收货地址地区信息：webapp_user_id:%s,ship_info_id:%s,area:%s' % (webapp_user_id, ship_info_id, area)
			watchdog_error(message)

		result = webapp_user.modify_ship_info(ship_info_id, new_ship_info)
		if result:
			return {
				'result': result
			}
		else:
			return 500, {}

	@param_required(['ship_name', 'ship_address', 'ship_tel', 'area'])
	def put(args):
		"""
		新建收货地址
		@param ship_name
		@param ship_address
		@param ship_tel
		@param area
		@return {'ship_info_id': ship_info_id}

		"""
		webapp_user = args['webapp_user']
		ship_info = {
			'ship_name': args['ship_name'],
			'ship_address': args['ship_address'],
			'ship_tel': args['ship_tel'],
			'area': args['area']
		}
		result, ship_info_id = webapp_user.create_ship_info(ship_info)

		area = args['area']
		if '_' not in area:
			webapp_user_id = args['webapp_user'].id
			message = u'错误的收货地址地区信息：webapp_user_id:%s,ship_info_id:%s,area:%s' % (webapp_user_id, ship_info_id, area)
			watchdog_error(message)

		if result:
			return {
				'ship_info_id': ship_info_id
			}
		else:
			return 500, {}

	@param_required(['ship_id'])
	def delete(args):
		"""
		删除收货地址
		@param ship_id
		@return 删除后的默认地址

		"""
		webapp_user = args['webapp_user']
		selected_id = webapp_user.delete_ship_info(args['ship_id'])
		return {
			'selected_id': selected_id
		}

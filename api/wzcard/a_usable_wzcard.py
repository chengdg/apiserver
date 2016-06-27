# -*- coding: utf-8 -*-
"""@package apiwzcard.a_usable_wzcard
微众卡查询\创建
"""

# import copy
# from datetime import datetime

from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.wzcard.wzcard import WZCard


class AUsableWZCard(api_resource.ApiResource):
	"""
	可用的微众卡
	"""
	app = 'wzcard'
	resource = 'usable_wzcard'

	@param_required(['wzcard_id', 'password'])
	def get(args):
		"""
		校验微众卡信息
		"""
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']

		exist_cards = args.get('used_cards', '')
		exist_cards = exist_cards.split(',') if exist_cards else []

		request_data = {
			'card_number': args['wzcard_id'],
			'card_password': args['password'],
			'valid_money': args['wzcard_check_money'],
			'exist_cards': exist_cards
		}

		checker = WZCard(webapp_user, webapp_owner)

		card_numbers = exist_cards + [args['wzcard_id']]

		is_success, msg = checker.boring_check(card_numbers)
		if not is_success:
			return {
				'code': 400,
				'msg': msg
			}

		# is_success, code, data = checker.check(request_data)


		resp = checker.check(request_data)

		if resp:
			code = resp['code']
			data = resp['data']
			if code == 200:
				return {
					'id': args['wzcard_id'],
					'code': 200,
					'balance': data['balance']
				}
			else:
				return {
					'code': 400,
					'msg': msg
				}
		else:
			return {
				'code': 400,
				'msg': u'系统繁忙'
			}


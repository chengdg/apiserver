# -*- coding: utf-8 -*-



from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.wzcard.wzcard import WZCard


class BindingCard(api_resource.ApiResource):
	app = 'wzcard'
	resource = 'binding_card'

	@param_required(['card_number', 'card_password'])
	def put(args):
		card_number = args['card_number']
		card_password = args['card_password']

		is_success, error_type, _data = WZCard.bind({
			'card_number': card_number,
			'card_password': card_password,
			'webapp_user': args['webapp_user'],
			'webapp_owner': args['webapp_owner']
		})

		if is_success:
			return {
				'card_number': card_number,
				'face_value': _data['face_value'],
				'balance': _data['balance'],
				'valid_time_from': _data['valid_time_from'],
				'valid_time_to':	_data['valid_time_to']

			}
		else:
			# card_apiserver产生：wzcard:duplicated(卡号重复),nosuch(卡不存在),wrongpass(卡密错误),expired(卡已过期),inactive(卡未激活),banned(商户禁止使用),exceeded(超过一次使用张数),other(其它原因)，见https://git2.weizzz.com:84/weizoom_card/card_apiserver/blob/master/card_api.yaml
			# apiserver产生：'common:wtf'（系统繁忙）、'wzcard:has_bound'（已绑定过）、wzcard:exhausted（余额为0）、wzcard:ten_times_error（已经输入错误10次）
			return 500, {
				'type': error_type
			}

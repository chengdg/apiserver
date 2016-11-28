# -*- coding: utf-8 -*-
"""
个人中心-VIP会员-支付结果
"""
from eaglet.core import api_resource
from eaglet.decorator import param_required


class APayResult(api_resource.ApiResource):
	"""
	个人中心-VIP会员-支付结果
	"""
	app = 'member_card'
	resource = 'pay_result'

	@param_required([])
	def get(args):
		"""
		通过 个人中心-VIP会员 入口进入会员页面。通常情况下，只有绑定了手机号并且已经开通了的会员会进入到这个页面，
		但为了防止非会员通过别人直接分享链接或者其他方式直接打开这个页面，这里面再次对is_binded和is_vip进行了判断，
		如果is_binded为False，前端应该跳转到绑定手机号页面，
		如果is_vip为False，前端应该跳转到会员卡列表页面

		@param 无
		@return member_card dict
		"""
		webapp_user = args['webapp_user']
		member_card = webapp_user.member_card
		is_binded = webapp_user.is_binded

		data = {}
		if is_binded and member_card:
			data = member_card.to_dict()
			data['is_binded'] = is_binded
			data['is_vip'] = True
		else:
			data = {
				'is_binded': is_binded,
				'is_vip': False
			}

		return data

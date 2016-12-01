# -*- coding: utf-8 -*-
"""
个人中心-VIP会员卡列表
"""
from eaglet.core import api_resource
from eaglet.core import watchdog
from eaglet.decorator import param_required
from eaglet.utils.resource_client import Resource

class AMemberCardList(api_resource.ApiResource):
	"""
	个人中心-VIP会员卡列表
	"""
	app = 'member_card'
	resource = 'member_card_list'

	@param_required([])
	def get(args):
		"""
		通过 个人中心-VIP会员 入口进入会员页面。通常情况下，只有绑定了手机号并且已经开通了的会员会进入到这个页面，
		但为了防止非会员通过别人直接分享链接或者其他方式直接打开这个页面，这里面再次对is_binded和is_vip进行了判断，
		如果is_binded为False，前端应该跳转到绑定手机号页面，
		如果is_vip为True，前端应该跳转到会员卡详情页面

		@param 无
		@return member_card dict
		"""
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']
		is_binded = webapp_user.is_binded

		if not is_binded:  #如果没绑定手机则直接返回
			return {'is_binded': False}

		member_card = webapp_user.member_card
		if member_card:  #如果已经是会员了则直接返回
			return {
				'is_binded': True,
				'is_vip': True
			}


		phone_number = webapp_user.phone_number
		member_name = webapp_user.username_for_html
		user_icon = webapp_user.user_icon
		data = {
			'is_binded': True,
			'is_vip': False,
			'phone_number': phone_number,
			'member_name': member_name,
			'user_icon': user_icon
		}
		resp = Resource.use('card_apiserver').get({
					'resource': 'card.membership_batches',
					'data': {'woid': webapp_owner.id}
				})
		if resp:
			code = resp['code']
			r_data = resp['data']
			if code == 200:
				card_infos = r_data['card_infos']
				print ">>>>>>>>>>>>resp>>>>>>>",resp
				print ">>>>>>>>>>>>>>>card_infos>>>>>>>>>>",card_infos
				data['card_infos'] = card_infos
			else:
				watchdog.error(resp)
		return data

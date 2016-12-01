# -*- coding: utf-8 -*-
"""
个人中心-VIP会员-支付结果
"""
from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.member_card.member_card_pay_order import MemberCardPayOrder
from a_payment import get_batch_info

class APayResult(api_resource.ApiResource):
	"""
	个人中心-VIP会员-支付结果
	"""
	app = 'member_card'
	resource = 'pay_result'

	@param_required(['order_id'])
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

		if not is_binded:
			return {
				'is_binded': is_binded,
				'is_vip': False
			}

		order_id = args['order_id']
		pay_order = MemberCardPayOrder.from_order_id({
				'order_id': order_id,
				'webapp_user': webapp_user,
				'webapp_owner': args['webapp_owner']
			})
		batch_id = pay_order.batch_id
		batch_info = get_batch_info(batch_id)
		if member_card: #支付成功页面
			data = {
				'is_binded': is_binded,
				'is_vip': True,  #如果is_vip是True，说明支付成功
				'price': batch_info['open_pay_money'],
				'remained_backcash_times': batch_info['back_times']
			}
		else:  #支付失败页面
			data = {
				'is_binded': is_binded,
				'is_vip': False,  #如果is_vip是False，说明支付失败
				'batch_id': batch_info['id'],
				'price': batch_info['open_pay_money'],
				'name': batch_info['name']
			}

		return data

# -*- coding: utf-8 -*-
"""
个人中心-VIP会员-支付
"""
from eaglet.core import api_resource
from eaglet.core import watchdog
from eaglet.decorator import param_required
from eaglet.utils.resource_client import Resource

from db.member import models as member_models
from business.member_card.member_card_pay_order import MemberCardPayOrder


class APayment(api_resource.ApiResource):
	"""
	个人中心-VIP会员-支付
	"""
	app = 'member_card'
	resource = 'payment'

	@param_required(['batch_id'])
	def get(args):
		"""
		通过 个人中心-VIP会员-会员卡列表 入口进入会员页面。通常情况下，只有绑定了手机号并且已经开通了的会员会进入到这个页面，
		但为了防止非会员通过别人直接分享链接或者其他方式直接打开这个页面，这里面再次对is_binded和is_vip进行了判断，
		如果is_binded为False，前端应该跳转到绑定手机号页面，
		如果is_vip为False，前端应该跳转到会员卡列表页面

		@param 无
		@return 会员卡id、名称和价钱
		"""
		webapp_user = args['webapp_user']
		is_binded = webapp_user.is_binded

		if not is_binded:  #如果没绑定手机则直接返回
			return {'is_binded': False}

		member_card = webapp_user.member_card
		if member_card:  #如果已经是会员了则直接返回
			return {
				'is_binded': True,
				'is_vip': True
			}

		batch_id = args['batch_id']
		batch_info = get_batch_info(batch_id)
		data = {
			'is_binded': True,
			'is_vip': False,
			'batch_id': batch_id,
			'price': batch_info['price'],
			'name': batch_info['name']
		}

		return data

	@param_required(['batch_id'])
	def put(args):
		"""
		购买会员卡下单接口

		@param batch_id
		@return 支付相关信息
		"""
		webapp_user = args['webapp_user']
		webapp_owner = args['webapp_owner']
		batch_id = args['batch_id']
		batch_info = get_batch_info(batch_id)

		owner_id = webapp_owner.id
		member_id = webapp_user.member.id
		batch_name = batch_info['name']
		price = batch_info['price']
		order_id = 'vip_%d_%d' % (owner_id, member_id)

		pay_order = MemberCardPayOrder.get_member_card_pay_order({
						'owner_id': owner_id, 
						'member_id': member_id, 
						'batch_id': batch_id,
						'order_id': order_id,
						'batch_name': batch_name,
						'price': price,
					})

		return {
			'type': 'wxpay',
			'woid': owner_id,
			'order_id': order_id,
			'name': batch_name,
			'price': price,
			'pay_id': 0,  #这个参数没有实际用处，但支付那边需要，暂时先写成0
			'showwxpaytitle': 1,
		}



def get_batch_info(batch_id):
	"""
	根据batch_id获取单个批次卡的详细信息
	"""
	batch_info = None
	resp = Resource.use('card_apiserver').get({
				'resource': 'card.membership_batch',
				'data': {'membership_batch_id': batch_id}
			})
	if resp:
		code = resp['code']
		data = resp['data']['card_info']
		if code == 200:
			batch_info = {
				'batch_id': data['id'],
				'price': data['open_pay_money'],
				'name': data['membership_name']
			}
		else:
			watchdog.error(resp)

	return batch_info
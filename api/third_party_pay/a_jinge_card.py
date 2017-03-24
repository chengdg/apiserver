# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.third_party_pay.jinge_card import JinGeCard
from util import send_phone_msg


class AJinGeCard(api_resource.ApiResource):
	app = 'jinge'
	resource = 'jinge_card'

	@param_required([])
	def get(args):
		"""
		通过 个人中心-锦歌饭卡 入口进入饭卡页面。
		如果is_binded为False，前端应该跳转到绑定手机号页面，
		如果is_active为False，前端应该跳转到初始化密码页面

		@param 无
		@return member_card dict
		"""
		webapp_user = args['webapp_user']
		member_id = webapp_user.member.id
		jinge_card = JinGeCard.from_member_id(member_id)

		if not jinge_card:
			return {
				'is_binded': False
			}
		
		if jinge_card.password:
			data = {
				'card_number': jinge_card.card_number,
				'is_active': True,
				'is_binded': True,
				'balance': jinge_card.balance,
				'name': jinge_card.name,
				'company': jinge_card.company,
				'phone_number': jinge_card.phone_number
			}
		else:
			data = {
				'is_binded': True,
				'is_active': False
			}
			
		return data

	@param_required(['phone_number'])
	def put(args):
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']
		phone_number = args['phone_number']
		captcha = args.get('captcha', None)

		jinge_card = JinGeCard.from_member_id(webapp_user.member.id)
		if captcha:  #提交验证码
			if jinge_card and jinge_card.captcha == captcha:
				#绑定饭卡
				if jinge_card.bind(phone_number):
					return u'绑定成功'
				else:
					return 500, u'绑定失败，请重试'
			else:
				return 500, u'手机验证码错误，请重新输入'


		if jinge_card and jinge_card.card_number:  #只有数据库中有记录而且关联了饭卡卡号才算绑定成功
			return 500, u'该用户已经绑定过饭卡'
		elif JinGeCard.from_phone_number(phone_number):
			return 500, u'该手机号已经绑定过饭卡'
		else:  #获取验证码
			company_name = webapp_owner.mpuser_preview_info.name
			#TODO 新建一个绑定饭卡的短信模板
			result, captcha = send_phone_msg.send_captcha(phone_number,company_name)
			if result and captcha:
				if jinge_card:
					jinge_card.update_phone_captcha(phone_number, captcha)
				else:
					JinGeCard.create(webapp_owner.id, webapp_user.member.id, phone_number)
				
				return {"captcha": captcha}
			else:
				return 500, u'获取短信验证码失败'
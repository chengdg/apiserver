# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.third_party_pay.jinge_card import JinGeCard
from util import jinge_rsa_util
from util import jinge_api_util


class ABindingJinGeCard(api_resource.ApiResource):
	app = 'jinge'
	resource = 'password'

	@param_required(['password'])
	def put(args):
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']
		password = args['password']

		jinge_card = JinGeCard.from_member_id(webapp_user.member.id)
		if jinge_card and jinge_card.card_number and jinge_card.token and not jinge_card.card_password:
			password = jinge_rsa_util.encrypt(password)
			if jinge_api_util.set_password(jinge_card.card_number, jinge_card.token, password):
				if jinge_card.set_password(password):
					return u'设置密码成功'

		return 500, u'设置密码失败'

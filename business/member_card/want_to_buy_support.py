# -*- coding: utf-8 -*-
"""@package business.member_card.want_to_buy
我想买的支持记录
"""
from eaglet.decorator import param_required
from db.member import models as member_models

from business import model as business_model
from business.account.member import Member
import settings

from eaglet.core import watchdog
from util.dateutil import get_readable_time


class WantToBuySupport(business_model.Model):
	"""
	我想买
	"""
	__slots__ = (
		'id',
		'want_to_buy_id',
		'member_id',
		'member_name',
		'member_icon',
		'content',
		'created_at'
	)

	def __init__(self):
		business_model.Model.__init__(self)

	@staticmethod
	@param_required(['webapp_owner', 'model'])
	def from_model(args):
		"""
		工厂对象，根据WantToBuySupport model获取MemberCard业务对象

		@param[in] model: WantToBuySupport model

		@return WantToBuySupport业务对象
		"""
		model = args['model']
		webapp_owner = args['webapp_owner']
		want_to_buy_support = WantToBuySupport()
		want_to_buy_support._init_slot_from_model(model)
		want_to_buy_support.created_at = get_readable_time(model.created_at)

		member = Member.from_model({
				'webapp_owner': webapp_owner,
				'model': model.member
			})
		want_to_buy_support.member_name = member.username_for_html
		want_to_buy_support.member_icon = member.user_icon

		return want_to_buy_support

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'want_to_buy_id', 'content'])
	def create(args):
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']
		member_id = webapp_user.member.id

		want_to_buy_id = args['want_to_buy_id']
		content = args['content']
		if member_models.WantToBuySupport.select().dj_where(want_to_buy_id=want_to_buy_id, member_id=member_id).count() == 0:
			want_to_buy_support = member_models.WantToBuySupport.create(
				want_to_buy=want_to_buy_id,
				member=member_id,
				content=content
			)

			return WantToBuySupport.from_model({
					'webapp_owner': webapp_owner,
					'model': want_to_buy_support
				})

		return None

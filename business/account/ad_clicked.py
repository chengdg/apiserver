# -*- coding: utf-8 -*-
"""@package business.account.ad_clicked

"""


from eaglet.decorator import param_required
from db.member import models as member_models

from business import model as business_model
import settings


class AdClicked(business_model.Model):
	"""
	广告点击
	"""
	__slots__ = (
		'id',
		'member_id',
		'created_at'
	)

	def __init__(self, model):
		business_model.Model.__init__(self)

		self.context['db_model'] = model

	@staticmethod
	@param_required(['model'])
	def from_model(args):
		"""
		工厂对象，根据adclicked model获取AdClicked业务对象

		@param[in] model: adclicked model

		@return AdClicked业务对象
		"""
		model = args['model']

		integral = AdClicked(model)
		integral._init_slot_from_model(model)
		return integral

	@staticmethod
	@param_required(['member_id'])
	def from_member_id(args):
		model = member_models.AdClicked.select().dj_where(member_id=args['member_id']).first()
		if model:
			return AdClicked.from_model({
				"model": model
				})
		return None
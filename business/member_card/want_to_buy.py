# -*- coding: utf-8 -*-
"""@package business.member_card.want_to_buy
我想买
"""
import json
import settings
from eaglet.decorator import param_required
from db.member import models as member_models

from business import model as business_model
from business.account.member import Member
from want_to_buy_support import WantToBuySupport

from eaglet.core import watchdog
from util.dateutil import get_readable_time, now

DATETIME_FORMAT="%Y-%m-%d %H:%M:%S"

class WantToBuy(business_model.Model):
	"""
	我想买
	"""
	__slots__ = (
		'id',
		'owner_id',
		'member_id',
		'member_name',
		'member_icon',
		'source',
		'product_id',
		'product_name',
		'status',
		'support_num',
		'pics',
		'is_accept_other_brand',
		'reach_num_at',
		'purchase_completed_at',
		'shelves_on_at',
		'created_at'
	)

	def __init__(self, webapp_owner, model):
		business_model.Model.__init__(self)
		self.context['webapp_owner'] = webapp_owner
		self.context['db_model'] = model

	@property
	def is_success(self):
		"""
		采购需求是否成功
		"""
		return self.status > 1

	@staticmethod
	@param_required(['webapp_owner', 'model'])
	def from_model(args):
		"""
		工厂对象，根据WantToBuy model获取WantToBuy业务对象

		@param[in] model: WantToBuy model

		@return WantToBuy业务对象
		"""
		webapp_owner = args['webapp_owner']
		model = args['model']
		member = Member.from_model({
				'webapp_owner': webapp_owner,
				'model': model.member
			})
		want_to_buy = WantToBuy(webapp_owner, model)
		want_to_buy._init_slot_from_model(model)
		want_to_buy.member_name = member.username_for_html
		want_to_buy.member_icon = member.user_icon
		if model.pics:
			want_to_buy.pics = json.loads(model.pics)
		else:
			want_to_buy.pics = []
		want_to_buy.created_at = get_readable_time(model.created_at)

		if want_to_buy.reach_num_at:
			want_to_buy.reach_num_at = want_to_buy.reach_num_at.strftime(DATETIME_FORMAT)
		else:
			want_to_buy.reach_num_at = ''

		if want_to_buy.purchase_completed_at:
			want_to_buy.purchase_completed_at = want_to_buy.purchase_completed_at.strftime(DATETIME_FORMAT)
		else:
			want_to_buy.purchase_completed_at = ''

		if want_to_buy.shelves_on_at:
			want_to_buy.shelves_on_at = want_to_buy.shelves_on_at.strftime(DATETIME_FORMAT)
		else:
			want_to_buy.shelves_on_at = ''

		return want_to_buy

	@staticmethod
	@param_required(['webapp_owner', 'id'])
	def from_id(args):
		webapp_owner = args['webapp_owner']
		model = member_models.WantToBuy.select().dj_where(id=args['id']).first()

		return WantToBuy.from_model({
				'webapp_owner': webapp_owner,
				'model': model
			})

	def get_supports(self):
		"""
		获取支持列表
		"""
		models = member_models.WantToBuySupport.select().dj_where(want_to_buy_id=self.id).order_by('-id')
		supports = []
		for model in models:
			supports.append(WantToBuySupport.from_model({
				'webapp_owner': self.context['webapp_owner'],
				'model': model
			}))
		
		return supports

	def has_supported(self, member_id):
		"""
		是否支持过
		"""
		count = member_models.WantToBuySupport.select().dj_where(want_to_buy_id=self.id, member_id=member_id).count()
		if count > 0:
			return True
		else:
			return False

	def update_status(self):
		"""
		更新状态
		"""
		support_count = member_models.WantToBuySupport.select().dj_where(want_to_buy_id=self.id).count()
		db_model = self.context['db_model']
		support_num = db_model.support_num
		db_model.support_num = support_num + 1
		self.support_num = support_num + 1

		if support_count >= 2 and self.status == member_models.STATUS_NOT_REACH:
			reach_num_at = now()
			self.status = member_models.STATUS_REACH
			self.reach_num_at = reach_num_at

			db_model.status = member_models.STATUS_REACH
			db_model.reach_num_at = reach_num_at

		db_model.save()
		

	@staticmethod
	@param_required(['webapp_owner', 'member_id'])
	def get_my_list(args):
		webapp_owner = args['webapp_owner']
		member_id = args['member_id']
		items = member_models.WantToBuy.select().dj_where(
				member_id=member_id, 
				status__in=[member_models.STATUS_NOT_REACH, member_models.STATUS_REACH, member_models.STATUS_PURCHASE]
			).order_by(-member_models.WantToBuy.created_at)

		datas = []
		for item in items:
			datas.append(WantToBuy.from_model({
				'webapp_owner': webapp_owner,
				'model': item
			}))
		return datas

	@staticmethod
	@param_required(['webapp_owner'])
	def get_all_list(args):
		webapp_owner = args['webapp_owner']
		items = member_models.WantToBuy.select().dj_where(
				owner_id=webapp_owner.id, 
				status__in=[member_models.STATUS_NOT_REACH, member_models.STATUS_REACH, member_models.STATUS_PURCHASE]
			).order_by(-member_models.WantToBuy.created_at)

		datas = []
		for item in items:
			datas.append(WantToBuy.from_model({
				'webapp_owner': webapp_owner,
				'model': item
			}))
		return datas

	@staticmethod
	@param_required(['webapp_owner', 'member_id'])
	def get_my_support_list(args):
		webapp_owner = args['webapp_owner']
		member_id = args['member_id']
		items = member_models.WantToBuySupport.select().dj_where(
				member_id=member_id, 
				want_to_buy__status__in=[member_models.STATUS_NOT_REACH, member_models.STATUS_REACH, member_models.STATUS_PURCHASE]
			).order_by(-member_models.WantToBuySupport.created_at)

		datas = []
		for item in items:
			datas.append(WantToBuy.from_model({
				'webapp_owner': webapp_owner,
				'model': item.want_to_buy
			}))
		return datas

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'source', 'pics', 'is_accept_other_brand'])
	def create(args):
		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']
		member_id = webapp_user.member.id
		want_to_buy = member_models.WantToBuy.create(
			owner_id=webapp_owner.id,
			member=member_id,
			source=args['source'],
			product_name=args['product_name'],
			pics=args['pics'],
			is_accept_other_brand=args['is_accept_other_brand']
		)

		return WantToBuy.from_model({
				'webapp_owner': webapp_owner,
				'model': want_to_buy
			})

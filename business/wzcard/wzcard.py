#coding: utf8
"""@package business.card.weizoom_card
微众卡的业务模型
"""

from business import model as business_model
from db.wzcard import models as wzcard_models
from wapi.decorators import param_required
#from db.wzcard.models import WeizoomCardRule, WeizoomCard
import logging
from decimal import Decimal


class WZCard(business_model.Model):
	"""
	微众卡业务模型

	@see WEAPP/market_tools/tools/weizoom_card/models.py
	"""
	__slots__ = (
		'id', # 数据库ID
		'wzcard_id', # 微众卡卡号
		'is_expired',
		#'status',

		'weizoom_card_rule_id',
		'weizoom_card_id',
		'money',
		'password',
		'expire_time',
		'activated_at',
		'created_at',
		'remark',
		'actived_to',
		'department',
		'active_card_user_id',
	)

	def __init__(self, webapp_owner, wzcard_id):
		business_model.Model.__init__(self)

		# webapp_owner是不需要暴露的property，因此放在context中
		self.context['webapp_owner'] = webapp_owner
		self.wzcard_id = wzcard_id

		db_model = wzcard_models.WeizoomCard.get(
			owner=webapp_owner.id,
			weizoom_card_id=wzcard_id)
		self.context['db_model'] = db_model
		#logging.info('db_model: {}'.format(db_model))
		logging.info('db_model.money: {}'.format(db_model.money))
		self._init_slot_from_model(db_model)


	@staticmethod
	@param_required(['webapp_owner', 'wzcard_id'])
	def from_wzcard_id(args):
		"""
		获取微众卡对象的工厂方法

		@return 如果不存在此卡，返回None
		"""
		try:	
			wzcard = WZCard(args['webapp_owner'], args['wzcard_id'])
			return wzcard
		except Exception as e:
			logging.error("Exception: " + str(e))
		return None

	'''
	@staticmethod
	@param_required(['wzcard_id', 'password'])
	def get(args):
		"""
		用微众卡号和密码获取WZCard对象
		"""
		return
	'''


	@property
	def readable_status(self):
		"""
		status->可读的status状态
		"""
		status = self.status
		text = None
		if status == wzcard_models.WEIZOOM_CARD_STATUS_UNUSED:
			text = u"未使用"
		elif status == wzcard_models.WEIZOOM_CARD_STATUS_USED:
			text = u"已使用"
		elif status == wzcard_models.WEIZOOM_CARD_STATUS_EMPTY:
			text = u"已用完"
		elif status == wzcard_models.WEIZOOM_CARD_STATUS_INACTIVE:
			text = u"未激活"
		return text

	@property
	def balance(self):
		"""
		[property] 微众卡余额
		"""
		#logging.info("self.money: {}".format(self.money))
		return self.money

	@balance.setter
	def balance(self, value):
		"""
		[setter] 修改微众卡余额
		"""
		self.money = value
		db_model = self.context['db_model']	
		db_model.money = value
		return

	@property
	def status(self):
		db_model = self.context['db_model']
		return db_model.status

	@status.setter
	def status(self, value):
		#self.status = value
		db_model = self.context['db_model']	
		db_model.status = value
		return

	@staticmethod
	def _get_status(status_str):
		"""
		@see `weapp/features/steps/market_tools_weizoom_card_steps.py`
		"""

		is_expired = False
		status = wzcard_models.WEIZOOM_CARD_STATUS_UNUSED
		if status_str == u"未使用":
			status = wzcard_models.WEIZOOM_CARD_STATUS_UNUSED
		if status_str == u"已使用":
			status = wzcard_models.WEIZOOM_CARD_STATUS_USED
		if status_str == u"已用完":
			status = wzcard_models.WEIZOOM_CARD_STATUS_EMPTY
		if status_str == u"未激活":
			status = wzcard_models.WEIZOOM_CARD_STATUS_INACTIVE

		if status_str == u"已过期":
			is_expired = True
			status = wzcard_models.WEIZOOM_CARD_STATUS_INACTIVE
		return status, is_expired

	def __create(self, args):
		"""
		先将weapp操作代码迁移过来，以后再调整

		@todo 待优化
		@see `weapp/features/steps/market_tools_weizoom_card_steps.py`
		"""
		webapp_owner = args['webapp_owner']
		# 创建规则
		rule, created = wzcard_models.WeizoomCardRule.objects.get_or_create(
			owner=webapp_owner.id,
			name='a',
			money=100,
			count=10,
			remark="",
			expired_time="3000-12-12 00:00:00",
			valid_time_from="2000-1-1 00:00:00",
			valid_time_to="3000-12-12 00:00:00",
		)

		status = args['status']
		status_code, is_expired = WZCard._get_status(status)
		wzcard = wzcard_models.WeizoomCard.objects.create(
			owner_id=webapp_owner.id,
			weizoom_card_rule=rule,
			status = status_code,
			money = args['balance'],
			weizoom_card_id = args['wzcard_id'],
			password = args['password'],
			expired_time = "3000-12-12 00:00:00",
			is_expired = is_expired
		)
		return wzcard


	@property
	def orders(self):
		"""
		微众卡对应的订单
		"""
		pass


	def check_password(self, password):
		"""
		检查密码
		@todo 待实现
		"""
		return True

	def save(self):
		"""
		微众卡信息序列化(比如存到数据库)
		"""
		db_model = self.context['db_model']	
		db_model.save()
		logging.info("saved WZCard DB object, wzcard_id={}, balance={}".format(db_model.weizoom_card_id, db_model.money))
		return


	def pay(self, price_to_pay):
		"""
		用微众卡支付

		@param price_to_pay Decimal最大待付款价格（能付多少付多少）

		@return Decimal类型的支付金额
		@see 参考原Weapp的`def use_weizoom_card()`
		"""
		if isinstance(price_to_pay, float):
			price_to_pay = Decimal(price_to_pay)
		use_price = min(price_to_pay, self.balance)
		self.balance = self.balance - use_price
		if self.balance < 1e-3:
			self.balance = Decimal(0)
			self.status = wzcard_models.WEIZOOM_CARD_STATUS_EMPTY
		else:
			self.status = wzcard_models.WEIZOOM_CARD_STATUS_USED 
		return use_price

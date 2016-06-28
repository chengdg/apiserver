# #coding: utf8
# """@package business.card.weizoom_card
# 微众卡的业务模型
#
# @see 原Weapp的`card_api_view.py`
# """
#
# from business import model as business_model
# from db.wzcard import models as wzcard_models
# from eaglet.decorator import param_required
# #from db.wzcard.models import WeizoomCardRule, WeizoomCard
# import logging
# from decimal import Decimal
# from core.decorator import deprecated
#
# class WZCard(business_model.Model):
# 	"""
# 	微众卡业务模型
#
# 	@see 原WEAPP的`/market_tools/tools/weizoom_card/models.py`
# 	"""
# 	__slots__ = (
# 		'id', # 数据库ID
# 		'wzcard_id', # 微众卡卡号
# 		'is_expired',
# 		#'status',
#
# 		'weizoom_card_rule_id',
# 		'weizoom_card_id',
# 		'money',
# 		'password',
# 		'expire_time',
# 		'activated_at',
# 		'created_at',
# 		'remark',
# 		'actived_to',
# 		'department',
# 		'active_card_user_id',
# 	)
#
# 	def __init__(self, db_model, wzcard_owner=None):
# 		business_model.Model.__init__(self)
#
# 		# webapp_owner是不需要暴露的property，因此放在context中
# 		# wzcard_owner表示创建微众卡的用户
# 		self.context['wzcard_owner'] = wzcard_owner
#
# 		self.wzcard_id = db_model.weizoom_card_id
# 		self.context['db_model'] = db_model
#
# 		self._init_slot_from_model(db_model)
#
#
# 	@staticmethod
# 	@param_required(['id'])
# 	def from_id(args):
# 		"""
# 		获取微众卡对象的工厂方法
#
# 		@return 如果不存在此卡，返回None
# 		"""
# 		try:
# 			db_model = wzcard_models.WeizoomCard.get(id=args['id'])
# 			wzcard = WZCard(db_model)
# 			return wzcard
# 		except Exception as e:
# 			logging.error("Exception: " + str(e))
# 		return None
#
#
# 	@staticmethod
# 	@param_required(['wzcard_id'])
# 	def from_wzcard_id(args):
# 		"""
# 		获取微众卡对象的工厂方法
#
# 		@return 如果不存在此卡，返回None
# 		"""
# 		try:
# 			db_model = wzcard_models.WeizoomCard.get(weizoom_card_id=args['wzcard_id'])
# 			wzcard = WZCard(db_model)
# 			return wzcard
# 		except Exception as e:
# 			logging.error("Exception: " + str(e))
# 		return None
#
#
# 	@property
# 	def readable_status(self):
# 		"""
# 		status->可读的status状态
# 		"""
# 		status = self.status
# 		text = None
# 		if status == wzcard_models.WEIZOOM_CARD_STATUS_UNUSED:
# 			text = u"未使用"
# 		elif status == wzcard_models.WEIZOOM_CARD_STATUS_USED:
# 			text = u"已使用"
# 		elif status == wzcard_models.WEIZOOM_CARD_STATUS_EMPTY:
# 			text = u"已用完"
# 		elif status == wzcard_models.WEIZOOM_CARD_STATUS_INACTIVE:
# 			text = u"未激活"
# 		return text
#
# 	@property
# 	def is_empty(self):
# 		"""
# 		[property] 是否已用完
#
# 		@return True:已用完；False:未用完
# 		"""
# 		return self.status == wzcard_models.WEIZOOM_CARD_STATUS_EMPTY
#
# 	@property
# 	def balance(self):
# 		"""
# 		[property] 微众卡余额
# 		"""
# 		return self.money
#
# 	@balance.setter
# 	def balance(self, value):
# 		"""
# 		[setter] 修改微众卡余额
# 		"""
# 		self.money = value
# 		db_model = self.context['db_model']
# 		db_model.money = value
# 		return
#
# 	@property
# 	def status(self):
# 		"""
# 		[property] 微众卡状态
#
# 		微众卡有几种状态：
#
# 		状态  |  值  | 符号
# 		:----- | :------- | :----------
# 		未使用	 	| 0 | WEIZOOM_CARD_STATUS_UNUSED
# 		已被使用 	| 1 | WEIZOOM_CARD_STATUS_USED
# 		已用完		| 2 | WEIZOOM_CARD_STATUS_EMPTY
# 		未激活		| 3 | WEIZOOM_CARD_STATUS_INACTIVE
#
# 		@see `db/models.py`
# 		"""
# 		db_model = self.context['db_model']
# 		return db_model.status
#
# 	@status.setter
# 	@deprecated
# 	def status(self, value):
# 		"""
# 		[setter] 微众卡状态
#
# 		@todo 改成通过操作调整status
# 		"""
# 		#self.status = value
# 		db_model = self.context['db_model']
# 		db_model.status = value
# 		return
#
# 	@staticmethod
# 	def _get_status(status_str):
# 		"""
# 		status_text -> status值
#
# 		@see `weapp/features/steps/market_tools_weizoom_card_steps.py`
# 		"""
#
# 		is_expired = False
# 		status = wzcard_models.WEIZOOM_CARD_STATUS_UNUSED
# 		if status_str == u"未使用":
# 			status = wzcard_models.WEIZOOM_CARD_STATUS_UNUSED
# 		if status_str == u"已使用":
# 			status = wzcard_models.WEIZOOM_CARD_STATUS_USED
# 		if status_str == u"已用完":
# 			status = wzcard_models.WEIZOOM_CARD_STATUS_EMPTY
# 		if status_str == u"未激活":
# 			status = wzcard_models.WEIZOOM_CARD_STATUS_INACTIVE
#
# 		if status_str == u"已过期":
# 			is_expired = True
# 			status = wzcard_models.WEIZOOM_CARD_STATUS_INACTIVE
# 		return status, is_expired
#
#
# 	def __create(self, args):
# 		"""
# 		先将weapp操作代码迁移过来，以后再调整
#
# 		@todo 待优化
# 		@see `weapp/features/steps/market_tools_weizoom_card_steps.py`
# 		"""
# 		webapp_owner = args['webapp_owner']
# 		# 创建规则
# 		rule, created = wzcard_models.WeizoomCardRule.objects.get_or_create(
# 			owner=webapp_owner.id,
# 			name='a',
# 			money=100,
# 			count=10,
# 			remark="",
# 			expired_time="3000-12-12 00:00:00",
# 			valid_time_from="2000-1-1 00:00:00",
# 			valid_time_to="3000-12-12 00:00:00",
# 		)
#
# 		status = args['status']
# 		status_code, is_expired = WZCard._get_status(status)
# 		wzcard = wzcard_models.WeizoomCard.objects.create(
# 			owner_id=webapp_owner.id,
# 			weizoom_card_rule=rule,
# 			status = status_code,
# 			money = args['balance'],
# 			weizoom_card_id = args['wzcard_id'],
# 			password = args['password'],
# 			expired_time = "3000-12-12 00:00:00",
# 			is_expired = is_expired
# 		)
# 		return wzcard
#
#
# 	@property
# 	def orders(self):
# 		"""
# 		[property] 微众卡对应的订单
#
# 		@todo 待实现
# 		"""
# 		return []
#
# 	def check_password(self, password):
# 		"""
# 		检查密码是否正确
# 		"""
# 		return self.password == password
#
# 	@property
# 	def is_activated(self):
# 		"""
# 		[property] 微众卡是否激活
# 		"""
# 		logging.info("WZCard.status: {}, id: {}".format(self.status, self.id))
# 		return self.status != wzcard_models.WEIZOOM_CARD_STATUS_INACTIVE
#
# 	def save(self):
# 		"""
# 		微众卡信息序列化(比如存到数据库)
# 		"""
# 		db_model = self.context['db_model']
# 		db_model.save()
# 		logging.info("saved WZCard DB object, wzcard_id={}, balance={}".format(db_model.weizoom_card_id, db_model.money))
# 		return
#
# 	def pay(self, price_to_pay):
# 		"""
# 		用微众卡支付
#
# 		@param price_to_pay Decimal最大待付款价格（能付多少付多少）
#
# 		@return Decimal类型的支付金额
# 		@see 参考原Weapp的`def use_weizoom_card()`
#
# 		@todo 记录日志
# 		"""
# 		# 如果price_to_pay是float/str，转成Decimal
# 		price_to_pay = price_to_pay if isinstance(price_to_pay, Decimal) else Decimal(price_to_pay)
# 		if price_to_pay < 1e-3:
# 			# 没有实际支付
# 			return Decimal(0)
#
# 		use_price = min(price_to_pay, self.balance)
# 		if use_price > 0:
# 			self.balance = self.balance - use_price
# 			if self.balance < 1e-3:
# 				self.balance = Decimal(0)
# 				self.status = wzcard_models.WEIZOOM_CARD_STATUS_EMPTY
# 			else:
# 				self.status = wzcard_models.WEIZOOM_CARD_STATUS_USED
# 			# 更新数据库
# 			self.save()
#
# 		return use_price
#
#
# 	def refund(self, amount, reason=None, last_status=None):
# 		"""
# 		微众卡退款（用于release）
#
# 		@param amount 退款金额
# 		@param reason 退款原因
# 		@param last_status 退款之前的状态
#
# 		@return 退款后余额
# 		@note 不同于微众卡"充值"
# 		"""
# 		# 如果amount是float/str，转成Decimal
# 		logging.info(u"to refund wzcard: wzcard_id: {}, amount: {}, reason: {}".format(self.wzcard_id, amount, reason))
# 		amount = amount if isinstance(amount, Decimal) else Decimal(amount)
# 		if amount>0:
# 			self.balance += amount
# 		if last_status:
# 			self.status = last_status
# 		# 更新数据库
# 		is_success = True
# 		try:
# 			self.save()
# 			# TODO: update log with `reason`
# 		except Exception as e:
# 			logging.error(str(e))
# 			is_success = False
# 		return is_success, self.balance


from business import model as business_model
from db.wzcard import models as wzcard_models
from eaglet.decorator import param_required
#from db.wzcard.models import WeizoomCardRule, WeizoomCard
import logging
from decimal import Decimal
from core.decorator import deprecated

class WZCard(business_model.Model):
	__slots__ = (
		'card_number',
		'card_password',
		'source',
	)


	def __init__(self, model):
		business_model.Model.__init__(self)

		self.context['db_model'] = model
		if model:
			self._init_slot_from_model(model)

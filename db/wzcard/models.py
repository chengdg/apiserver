#coding: utf8
"""@package db.wzcard.models
微众卡存储模型
"""

from eaglet.core.db import models
from db.account.models import User

#########################################################################
# WeizoomCardRule ：微众卡规则
#########################################################################
#微众卡类型
WEIZOOM_CARD_EXTERNAL_USER = 0 #外部卡
WEIZOOM_CARD_INTERNAL_USER = 1 #内部卡
WEIZOOM_CARD_GIFT_USER = 2 #赠品卡

#微众卡属性
WEIZOOM_CARD_ORDINARY = 0 #通用卡
WEIZOOM_CARD_SPECIAL = 1 #专属卡
WEIZOOM_CARD_ATTR={
	WEIZOOM_CARD_ORDINARY: u'通用卡',
	WEIZOOM_CARD_SPECIAL: u'专属卡'
}

class WeizoomCardRule(models.Model):
	"""
	微众卡规则
	"""
	owner = models.ForeignKey(User)
	name = models.CharField(max_length=20, db_index=True) #名称
	money = models.DecimalField(max_digits=65, decimal_places=2) #微众卡金额
	count = models.IntegerField(default=0) #发放总数量
	remark = models.CharField(max_length=20, db_index=True) #备注
	expired_time = models.DateTimeField() #过期时间
	valid_time_from = models.DateTimeField() #有效范围开始时间
	valid_time_to = models.DateTimeField() #有效范围结束时间
	created_at = models.DateTimeField(auto_now_add=True) #添加时间
	card_type = models.IntegerField(default=WEIZOOM_CARD_EXTERNAL_USER) #微众卡类型
	card_attr = models.IntegerField(default=0) #微众卡属性
	shop_limit_list = models.CharField(max_length=2048, default='-1') #专属商家
	shop_black_list = models.CharField(max_length=2048, default='-1') #不能使用微众卡的商家
	is_new_member_special = models.BooleanField(default=False) #是否为新会员专属卡
	valid_restrictions = models.DecimalField(max_digits=65, decimal_places=2) #订单满多少可以使用规则

	class Meta(object):
		db_table = 'market_tool_weizoom_card_rule'
		verbose_name = '微众卡规则'
		verbose_name_plural = '微众卡规则'



#微众卡状态
WEIZOOM_CARD_STATUS_UNUSED = 0 #未使用
WEIZOOM_CARD_STATUS_USED = 1 #已被使用
WEIZOOM_CARD_STATUS_EMPTY = 2 #已用完
WEIZOOM_CARD_STATUS_INACTIVE = 3 #未激活

class WeizoomCard(models.Model):
	"""
	微众卡存储模型

	@note WeizoomCardHasAccount.account.id即owner_id
	"""
	owner = models.ForeignKey(User)
	target_user_id = models.IntegerField(default=0, verbose_name="微众卡发放目标")
	weizoom_card_rule = models.ForeignKey(WeizoomCardRule) 
	status = models.IntegerField(default=WEIZOOM_CARD_STATUS_INACTIVE) #微众卡状态
	weizoom_card_id = models.CharField(max_length=50) #微众卡号
	money = models.DecimalField(max_digits=65, decimal_places=2) #剩余金额
	password = models.CharField(max_length=50) #微众卡密码
	expired_time = models.DateTimeField() #过期时间
	is_expired = models.BooleanField(default=False) #是否过期
	activated_at = models.DateTimeField(null=True) #激活时间
	created_at = models.DateTimeField(auto_now_add=True) #添加时间
	remark = models.CharField(max_length=20, db_index=True) #备注
	activated_to = models.CharField(max_length=20) #申请人
	department = models.CharField(max_length=20) #申请部门
	active_card_user_id = models.IntegerField(default=1) #激活卡片人

	class Meta(object):
		db_table = 'market_tool_weizoom_card'
		verbose_name = '微众卡'
		verbose_name_plural = '微众卡'

	# @staticmethod
	# def check_card(weizoom_card_id, password):
	# 	return WeizoomCard.objects.filter(weizoom_card_id=weizoom_card_id, password=password).count() > 0


WEIZOOM_CARD_LOG_TYPE_ACTIVATION = u'激活'
WEIZOOM_CARD_LOG_TYPE_DISABLE = u'停用'
WEIZOOM_CARD_LOG_TYPE_BUY_USE = u'使用'
WEIZOOM_CARD_LOG_TYPE_BUY_RETURN = u'返还'
WEIZOOM_CARD_LOG_TYPE_RETURN_BY_SYSTEM = u'积分兑换'
WEIZOOM_CARD_LOG_TYPE_MANAGER_MODIFY = u'系统管理员修改'
#########################################################################
# WeizoomCardHasOrder : 消费记录 order_id == -1 是积分兑换
#########################################################################
class WeizoomCardHasOrder(models.Model):
	owner_id = models.IntegerField() #商家
	card_id = models.IntegerField() #weizoom card id  
	order_id = models.CharField(max_length=50, default='-1') #订单号  order_id == -1 是积分兑换
	money = models.DecimalField(max_digits=65, decimal_places=2) #金额
	created_at = models.DateTimeField(auto_now_add=True) #添加时间
	event_type = models.CharField(max_length=64, verbose_name='事件类型')
	member_integral_log_id = models.IntegerField(default=0, verbose_name='积分日志id')
	trade_id = models.CharField(max_length=100, default='')  # 交易号
	card_code = models.CharField(max_length=50, default='')     # 微众卡号

	class Meta(object):
		db_table = 'market_tool_weizoom_card_has_order'
		verbose_name = '微众卡支付交易记录'
		verbose_name_plural = '微众卡支付交易记录'


WEIZOOM_CARD_SOURCE_WEAPP = 0	#目前没用到
WEIZOOM_CARD_SOURCE_REBATE = 1	#返利活动
WEIZOOM_CARD_SOURCE_VIRTUAL = 2  #福利卡券
class MemberHasWeizoomCard(models.Model):
	"""
	给会员发放的微众卡
	"""
	member_id = models.IntegerField() #会员id
	member_name = models.CharField(max_length=1024) #会员名称
	card_number = models.CharField(max_length=50) #微众卡卡号
	card_password = models.CharField(max_length=100) #微众卡密码
	relation_id = models.CharField(max_length=128) #关联的活动id
	source = models.IntegerField() #微众卡来源

	created_at = models.DateTimeField(auto_now_add=True) #发放时间

	class Meta(object):
		db_table = 'member_has_weizoom_card'

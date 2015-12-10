#coding: utf8
"""@package db.wzcard.models
微众卡存储模型
"""

from core.db import models
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
	belong_to_owner = models.IntegerField(default=0) #专属商家
	is_new_member_special = models.BooleanField(default=False) #是否为新会员专属卡

	#@staticmethod
	#def get_all_weizoom_card_rules_list(user):
	#	if user is None:
	#		return []
	#	return list(WeizoomCoinRule.objects.filter(owner=user))

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


class AccountHasWeizoomCardPermissions(models.Model):
	"""
	账号对应使用微众卡功能权限
	"""
	owner_id = models.IntegerField(default=0, verbose_name='账号id')
	is_can_use_weizoom_card = models.BooleanField(default=False, verbose_name='是否可以使用微众卡')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

	class Meta(object):
		db_table = 'market_tool_weizoom_card_account_has_permissions'
		verbose_name = '账号对应使用微众卡功能权限'
		verbose_name_plural = '账号对应使用微众卡功能权限'

	#@staticmethod
	#def is_can_use_weizoom_card_by_owner_id(owner_id):
	#	permissions = AccountHasWeizoomCardPermissions.objects.filter(owner_id=owner_id)
	#	if permissions.count() > 0:
	#		return permissions[0].is_can_use_weizoom_card
	#	else:
	#		return False

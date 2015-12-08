#coding: utf8
from core.db import models

import datetime

class User(models.Model):
	"""
	从django.contrib.auth.User迁移过来
	"""
	username = models.CharField(max_length=30)
	first_name = models.CharField(max_length=30, default='')
	last_name = models.CharField(max_length=30, default='')
	email = models.EmailField(default='')
	is_staff = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True,)
	date_joined = models.DateTimeField(default=datetime.datetime.now)

	class Meta:
		db_table = 'auth_user'
		verbose_name = 'user'
		verbose_name_plural = 'users'
		#abstract = True


SYSTEM_VERSION_TYPE_BASE= 'base'
SYSTEM_VERSION_TYPE_PREMIUM = 'premium'
SYSTEM_VERSION_TYPES = (
	(SYSTEM_VERSION_TYPE_BASE, '初级版'),
	(SYSTEM_VERSION_TYPE_PREMIUM, '高级版'),
	)

USER_STATUS_NORMAL = 0
USER_STATUS_BUSY = 1
USER_STATUS_DISABLED = 2
USER_STATUSES = (
	(USER_STATUS_NORMAL, '正常'),
	(USER_STATUS_BUSY, '忙碌'),
	(USER_STATUS_DISABLED, '停用')
)
SELF_OPERATION = 0
THIRD_OPERATION = 1
OTHER_OPERATION = 2

OPERATION_TYPE = {
	SELF_OPERATION: u'自运营',
	THIRD_OPERATION: u'代运营',
	OTHER_OPERATION: u'其它'
}

WEBAPP_TYPE_MALL = 0 #普通商城
WEBAPP_TYPE_WEIZOOM_MALL = 1 #微众商城

class UserProfile(models.Model):
	"""
	用户profile
	"""
	user = models.ForeignKey(User)
	manager_id = models.IntegerField(default=0) #创建该用户的系统用户的id
	webapp_id = models.CharField(max_length=16)
	webapp_type = models.IntegerField(default=0) #商城类型
	app_display_name = models.CharField(max_length=50, verbose_name='用于显示app名称')
	is_active = models.BooleanField(default=True, verbose_name='用户是否有效')
	note = models.CharField(max_length=1024, default='')
	status = models.IntegerField(default=USER_STATUS_NORMAL)
	is_mp_registered = models.BooleanField(default=False, verbose_name='是否已经接入了公众账号') 
	mp_token = models.CharField(max_length=50, verbose_name='绑定公众号使用的token')
	mp_url = models.CharField(max_length=256, verbose_name='公众号绑定的url')
	new_message_count = models.IntegerField(default=0) #新消息数
	webapp_template = models.CharField(max_length=50, default='shop') #webapp的模板
	is_customed = models.IntegerField(default=0) #是否客户自定义CSS样式：1：是；0：否
	is_under_previewed = models.IntegerField(default=0) #是否是预览模式：1：是；0：否
	expire_date_day = models.DateField(auto_now_add=True)
	force_logout_date = models.BigIntegerField(default=0)

	host_name = models.CharField(max_length=1024, default="")
	logout_redirect_to = models.CharField(max_length=1024, default="")
	system_name = models.CharField(max_length=64, default=u'微信营销管理系统', verbose_name='系统名称')
	system_version = models.CharField(max_length=16, default=SYSTEM_VERSION_TYPE_BASE, verbose_name='系统版本')
	
	homepage_template_name = models.CharField(max_length=250) #首页模板名
	backend_template_name = models.CharField(max_length=250) #后端页面模板名
	homepage_workspace_id = models.IntegerField(default=0) #homepage workspace的id
	#add by bert 
	account_type = models.IntegerField(default=SELF_OPERATION)#帐号类型
	is_oauth = models.BooleanField(default=False) #是否授权
	#v2
	sub_account_count = models.IntegerField(default=50) #可创建的子账号的个数
	#wepage
	is_use_wepage = models.BooleanField(default=False) #是否启用wepage

	class Meta(object):
		db_table = 'account_user_profile'

	@property
	def host(self):
		if hasattr(self, '_host'):
			return self._host

		if self.host_name and len(self.host_name.strip()) > 0:
			self._host = self.host_name
		else:
			self._host = settings.DOMAIN

		return self._host

	@property
	def is_manager(self):
		return (self.user_id == self.manager_id) or (self.manager_id == 2) #2 is manager's id


class OperationSettings(models.Model):
	"""
	运营配置
	"""
	owner = models.ForeignKey(User, unique=True)
	non_member_followurl = models.CharField(max_length=1024, default='')
	weshop_followurl = models.CharField(max_length=1024, default='')

	class Meta(object):
		db_table = 'account_operation_settings'

	@staticmethod
	def get_settings_for_user(userid):
		if userid is None:
			return None

		settings_list = list(OperationSettings.select().dj_where(owner_id=userid)) 
		if len(settings_list) == 0:
			return OperationSettings.create(owner=userid)
		else:
			return settings_list[0]


class AccountHasWeizoomCardPermissions(models.Model):
	"""
	账号对应使用微众卡功能权限
	"""
	owner_id = models.IntegerField(default=0, verbose_name='账号id')
	is_can_use_weizoom_card = models.BooleanField(default=False, verbose_name='是否可以使用微众卡')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

	class Meta(object):
		db_table = 'market_tool_weizoom_card_account_has_permissions'

	@staticmethod
	def is_can_use_weizoom_card_by_owner_id(owner_id):
		permissions = AccountHasWeizoomCardPermissions.select().dj_where(owner_id=owner_id)
		if permissions.count() > 0:
			return permissions[0].is_can_use_weizoom_card
		else:
			return False


class TemplateGlobalNavbar(models.Model):
	'''
	全局导航
	'''
	owner = models.ForeignKey(User, related_name='owned_template_global_navbar')
	is_enable = models.BooleanField(default=True, verbose_name='是否启用')
	content = models.TextField(default='', verbose_name='navbar的json字符串')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="修改时间")

	class Meta(object):
		db_table = 'template_global_navbar'

	@staticmethod
	def get_object(user_id):
		if user_id > 0:
			global_navbar, _ = TemplateGlobalNavbar.objects.get_or_create(
				owner_id=user_id
			)
			return global_navbar
		else:
			return None




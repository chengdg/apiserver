#coding: utf8

from datetime import datetime

from db import models
from models import User


AESKEY_NORMAL = 0
AESKEY_BOTH = 1
AESKEY_ENCODE = 2
class WeixinMpUser(models.Model):
	"""
	微信公众账号
	"""
	owner = models.ForeignKey(User, unique=True)
	username = models.CharField(default='', max_length=50) #用户名
	password = models.CharField(default='', max_length=50) #密码
	is_certified = models.BooleanField(default=False, verbose_name='是否进行过微信认证')
	is_service = models.BooleanField(default=False, verbose_name='是否为服务号')
	is_active = models.BooleanField(default=True) #公众号是否有效
	aeskey = models.IntegerField(default=AESKEY_NORMAL)
	encode_aeskey = models.TextField(default='') 
	created_at = models.DateTimeField(auto_now=True) #公众号添加的时间

	def __unicode__(self):
		return self.username

	class Meta(object):
		db_table = 'account_weixin_mp_user'
		

	@staticmethod
	def get_weixin_mp_user(user_id):
		if WeixinMpUser.objects.filter(owner_id=user_id).count() > 0:
			return WeixinMpUser.objects.filter(owner_id=user_id)[0]
		else:
			return None


	@staticmethod
	def get_weixin_mp_user_access_token_by_mp_user(mpuser):
		if WeixinMpUserAccessToken.objects.filter(mpuser=mpuser).count() > 0:
			return WeixinMpUserAccessToken.objects.filter(mpuser=mpuser)[0]
		else:
			return None


DEFAULT_ICON = '/static/img/user-1.jpg'
class MpuserPreviewInfo(models.Model):
	"""
	微信公众账号预览信息
	"""
	mpuser = models.ForeignKey(WeixinMpUser)
	name = models.CharField(max_length=100)#预览显示的名字
	image_path = models.CharField(max_length=500, default=DEFAULT_ICON)#预览显示的图片

	class Meta(object):
		db_table='account_mpuser_preview_info'


class WeixinMpUserAccessToken(models.Model):
	"""
	微信公众号的AccessToken信息

	access_token对应于公众号是全局唯一的票据，重复获取将导致上次获取的access_token失效
	"""
	mpuser = models.ForeignKey(WeixinMpUser)
	app_id = models.CharField(max_length=64)
	app_secret = models.CharField(max_length=64)
	access_token = models.CharField(max_length=1024) #mp平台返回的access_token
	update_time = models.DateTimeField(auto_now=True)
	expire_time = models.DateTimeField()
	created_at = models.DateTimeField(auto_now=True)
	is_active = models.BooleanField(default=True)
	
	def __unicode__(self):
		return self.mpuser.username

	class Meta(object):
		#managed = False
		db_table = 'weixin_mp_user_access_token'


class ComponentInfo(models.Model):
	"""
	<xml><AppId><![CDATA[wx984abb2d00cc47b8]]></AppId>
	<CreateTime>1427710810</CreateTime>
	<InfoType><![CDATA[component_verify_ticket]]></InfoType>
	<ComponentVerifyTicket><![CDATA[Z8RBNjttRu3P5eM8rPe9TW3dA09yuAequP1BmbHhITxs8lZ-
	X-Gxwaegr5lcPkfJ4VAiRLiuLlCrhKmIz-oSpw]]></ComponentVerifyTicket>
	</xml>

	<xml><AppId><![CDATA[wx984abb2d00cc47b8]]></AppId>
	<CreateTime>1427710810</CreateTime>
	<InfoType><![CDATA[component_verify_ticket]]></InfoType>
	<ComponentVerifyTicket><![CDATA[Z8RBNjttRu3P5eM8rPe9TW3dA09yuAequP1BmbHhITxs8lZ-
	X-Gxwaegr5lcPkfJ4VAiRLiuLlCrhKmIz-oSpw]]></ComponentVerifyTicket>
	</xml>
	"""
	app_id = models.CharField(max_length=64)
	app_secret = models.CharField(max_length=64)
	component_verify_ticket = models.TextField() 
	token = models.TextField()
	ase_key = models.TextField()
	last_update_time = models.DateTimeField(default=datetime.now())
	component_access_token = models.TextField()
	is_active = models.BooleanField(default=True)

	def __unicode__(self):
		return self.app_id

	class Meta(object):
		db_table = 'component_info'
		verbose_name = '第三方帐号信息'
		verbose_name_plural = '第三方帐号信息'



class ComponentAuthedAppid(models.Model):
	"""
	参数	说明
	authorization_info	授权信息
	authorizer_appid	授权方appid
	authorizer_access_token	授权方令牌（在授权的公众号具备API权限时，才有此返回值）
	expires_in	有效期（在授权的公众号具备API权限时，才有此返回值）
	authorizer_refresh_token	刷新令牌（在授权的公众号具备API权限时，才有此返回值），刷新令牌主要用于公众号第三方平台获取和刷新已授权用户的access_token，只会在授权时刻提供，请妥善保存。 一旦丢失，只能让用户重新授权，才能再次拿到新的刷新令牌
	func_info	公众号授权给开发者的权限集列表（请注意，当出现用户已经将消息与菜单权限集授权给了某个第三方，再授权给另一个第三方时，由于该权限集是互斥的，后一个第三方的授权将去除此权限集，开发者可以在返回的func_info信息中验证这一点，避免信息遗漏），
	1到8分别代表：
	1消息与菜单权限集
	2用户管理权限集
	3帐号管理权限集
	4网页授权权限集
	5微信小店权限集
	6多客服权限集
	7业务通知权限集
	8微信卡券权限集

	"""
	component_info = models.ForeignKey(ComponentInfo)
	auth_code = models.TextField(default='')
	user_id = models.IntegerField(default=0) #对应帐号user id
	last_update_time = models.DateTimeField(default=datetime.now())
	authorizer_appid = models.CharField(max_length=255, default='')
	authorizer_access_token = models.TextField()
	authorizer_refresh_token = models.TextField()
	func_info = models.TextField()
	created_at = models.DateTimeField(auto_now=True)
	is_active = models.BooleanField(default=False)

	class Meta(object):
		db_table = 'component_authed_appid'
		verbose_name = '委托授权帐号基本信息'
		verbose_name_plural = '委托授权帐号基本信息'


class ComponentAuthedAppidInfo(models.Model):
	"""
	参数	说明
	authorizer_info	授权方昵称
	head_img	授权方头像
	service_type_info	授权方公众号类型，0代表订阅号，1代表由历史老帐号升级后的订阅号，2代表服务号
	verify_type_info	授权方认证类型，-1代表未认证，0代表微信认证，1代表新浪微博认证，2代表腾讯微博认证，3代表已资质认证通过但还未通过名称认证，4代表已资质认证通过、还未通过名称认证，但通过了新浪微博认证，5代表已资质认证通过、还未通过名称认证，但通过了腾讯微博认证
	user_name	授权方公众号的原始ID
	alias	授权方公众号所设置的微信号，可能为空
	qrcode_url	二维码图片的URL，开发者最好自行也进行保存
	authorization_info	授权信息
	appid	授权方appid
	func_info	公众号授权给开发者的权限集列表（请注意，当出现用户已经将消息与菜单权限集授权给了某个第三方，再授权给另一个第三方时，由于该权限集是互斥的，后一个第三方的授权将去除此权限集，开发者可以在返回的func_info信息中验证这一点，避免信息遗漏），1到9分别代表：
	消息与菜单权限集
	用户管理权限集
	帐号管理权限集
	网页授权权限集
	微信小店权限集
	多客服权限集
	业务通知权限集
	微信卡券权限集
	微信扫一扫权限集

	"""
	auth_appid = models.ForeignKey(ComponentAuthedAppid)
	nick_name = models.CharField(max_length=255)
	head_img = models.CharField(max_length=255)
	service_type_info = models.CharField(max_length=255)
	verify_type_info = models.CharField(max_length=255)
	user_name = models.CharField(max_length=255) #授权方公众号的原始ID
	alias = models.TextField()
	qrcode_url = models.CharField(max_length=255)
	appid = models.CharField(max_length=255)
	func_info = models.TextField()
	created_at = models.DateTimeField(auto_now=True)

	class Meta(object):
		db_table = 'component_authed_appid_info'
		verbose_name = '委托授权帐号详细信息'
		verbose_name_plural = '委托授权帐号详细信息'

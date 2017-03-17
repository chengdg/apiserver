#coding: utf8
from datetime import datetime

from eaglet.core.db import models
from db.account.models import User
from core.decorator import cached_property
from util.string_util import hex_to_byte, byte_to_hex

from hashlib import md5
import time
import string

#######################################################################
# 会员账号相关model
#######################################################################
class MemberGrade(models.Model):
	"""
	会员等级
	"""
	webapp_id = models.CharField(max_length=16, verbose_name='所关联的app id')
	name = models.TextField()
	is_auto_upgrade = models.BooleanField(default=False, verbose_name='是否凭经验值自动升级')
	upgrade_lower_bound = models.IntegerField(default=0, verbose_name='该等级的经验值下限')
	shop_discount = models.IntegerField(default=100, verbose_name='购物折扣')
	is_default_grade = models.BooleanField(default=False)
	usable_integral_percentage_in_order = models.IntegerField(verbose_name='一笔交易中能使用的多少积分', default=100) # -1 无限制
	pay_money = models.FloatField(default=0.00)
	pay_times = models.IntegerField(default=0)
	integral = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta(object):
		db_table = 'member_grade'

	def __unicode__(self):
		return u"{}-{}".format(self.webapp_id, self.name)


SOCIAL_PLATFORM_WEIXIN = 0
SOCIAL_PLATFORM_QQ = 1
SOCIAL_PLATFORM_SINAWEIBO = 2
SOCIAL_PLATFORM_PHONE = 3
SOCIAL_PLATFORMS = (
	(SOCIAL_PLATFORM_WEIXIN, '微信'),
	(SOCIAL_PLATFORM_QQ, 'QQ'),
	(SOCIAL_PLATFORM_SINAWEIBO, '新浪微博'),
	(SOCIAL_PLATFORM_PHONE, '手机注册'),
)
class SocialAccount(models.Model):
	"""
	社交平台账号
	"""
	platform = models.IntegerField(default=SOCIAL_PLATFORM_WEIXIN, verbose_name='社会化平台')
	webapp_id = models.CharField(max_length=16)
	token = models.CharField(max_length=64)
	access_token = models.CharField(max_length=64, default='')
	is_for_test = models.BooleanField(default=False)
	openid = models.CharField(max_length=64)
	uuid = models.CharField(max_length=255, default='')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='加入日期')


	class Meta(object):
		db_table = 'binding_social_account'


class ShipInfo(models.Model):
	"""
	收货地址
	"""
	webapp_user_id = models.IntegerField(db_index=True, default=0)
	ship_name = models.CharField(max_length=100) # 收货人姓名
	ship_tel = models.CharField(max_length=100) # 收货人电话
	ship_address = models.CharField(max_length=200) # 收货人地址
	area = models.CharField(max_length=256) #地区
	is_selected = models.BooleanField(default=True) # 是否选中，默认是选中
	is_deleted = models.BooleanField(default=False) # 是否被删除
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta(object):
		db_table = 'member_ship_info'


class WebAppUser(models.Model):
	"""
	WebApp的用户
	"""
	token = models.CharField(max_length=100, default='')
	webapp_id = models.CharField(max_length=16)
	member_id = models.IntegerField(default=0) #会员记录的id
	has_purchased = models.BooleanField(default=False) #是否购买过
	father_id = models.IntegerField(default=0) #会员记录的id
	created_at = models.DateTimeField(auto_now_add=True) #创建时间

	class Meta(object):
		db_table = 'member_webapp_user'

#关注渠道
SOURCE_SELF_SUB = 0  # 直接关注
SOURCE_MEMBER_QRCODE = 1  # 推广扫码
SOURCE_BY_URL = 2  # 会员分享
#status  会员状态
CANCEL_SUBSCRIBED = 0
SUBSCRIBED = 1
NOT_SUBSCRIBED = 2
class Member(models.Model):
	"""
	会员
	"""
	token = models.CharField(max_length=255)
	webapp_id = models.CharField(max_length=16)
	username_hexstr = models.CharField(max_length=2048, verbose_name='会员名称的hex str')
	user_icon = models.CharField(max_length=1024, verbose_name='会员头像', default='')
	integral = models.IntegerField(default=0, verbose_name='积分')
	created_at = models.DateTimeField(auto_now_add=True)
	grade = models.ForeignKey(MemberGrade)
	experience = models.IntegerField(default=0, verbose_name='经验值')
	remarks_name = models.CharField(max_length=32, verbose_name='备注名', default='')
	remarks_extra = models.TextField(verbose_name='备注信息', default='')
	last_visit_time = models.DateTimeField(auto_now_add=True)
	last_message_id = models.IntegerField(default=-1, verbose_name="最近一条消息id")
	session_id = models.IntegerField(default=-1, verbose_name="会话id")
	is_for_test = models.BooleanField(default=False)
	is_subscribed = models.BooleanField(default=True)
	friend_count = models.IntegerField(default=0) #好友数量
	factor = models.FloatField(default=0.00) #社会因子
	source = models.IntegerField(default=-1) #会员来源
	is_for_buy_test = models.BooleanField(default=False)
	update_time = models.DateTimeField(default=datetime.now())#会员信息更新时间 2014-11-11
	pay_money = models.FloatField(default=0.0)
	pay_times =  models.IntegerField(default=0)
	last_pay_time = models.DateTimeField(default=None)#会员信息更新时间 2014-11-11
	unit_price = models.FloatField(default=0.0) #ke dan jia
	city = models.CharField(default='', max_length=50)
	province = models.CharField(default='', max_length=50)
	country = models.CharField(default='', max_length=50)
	sex = models.IntegerField(default=0, verbose_name='性别')
	status = models.IntegerField(default=1)
	purchase_frequency = models.IntegerField(default=0)  # 30天购买次数
	cancel_subscribe_time = models.DateTimeField(blank=True, null=True, default=None, verbose_name="取消关注时间")
	fans_count = models.IntegerField(default=0) #粉丝数量

	class Meta(object):
		db_table = 'member_member'

	def __unicode__(self):
		return u'<member: %s %s>' % (self.webapp_id, self.token)










##############################################################################
# 会员其他信息相关model
##############################################################################
class MemberHasSocialAccount(models.Model):
	"""
	<member, social_account>关联
	"""
	member = models.ForeignKey(Member)
	account = models.ForeignKey(SocialAccount)
	webapp_id = models.CharField(max_length=50)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta(object):
		db_table = 'member_has_social_account'


SEX_TYPE_MEN = 1
SEX_TYPE_WOMEN = 2
SEX_TYPE_UNKOWN = 0


class MemberInfo(models.Model):
	"""
	会员信息
	"""
	member = models.ForeignKey(Member)
	name = models.CharField(max_length=8, verbose_name='会员姓名')
	sex = models.IntegerField(default=SEX_TYPE_UNKOWN, verbose_name='性别')
	age = models.IntegerField(default=-1, verbose_name='年龄')
	address = models.CharField(max_length=32, verbose_name='地址', default='')
	phone_number = models.CharField(max_length=11, default='')
	qq_number = models.CharField(max_length=13, default='')
	weibo_nickname = models.CharField(max_length=16, verbose_name='微博昵称')
	member_remarks = models.CharField(max_length=255, default='')
	is_binded = models.BooleanField(default=False)
	session_id = models.CharField(max_length=1024, default='')
	captcha = models.CharField(max_length=11,default='') #验证码
	binding_time = models.DateTimeField() #绑定时间

	class Meta(object):
		db_table = 'member_info'


class MemberFollowRelation(models.Model):
	"""
	会员关注关系
	"""
	member_id = models.IntegerField()
	follower_member_id = models.IntegerField()
	is_fans = models.BooleanField() #是否是member_id 粉丝
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta(object):
		db_table = 'member_follow_relation'


USABLE_BOTH = 0 #积分优惠券可以同时使用
USABLE_INTEGRAL = 1 #只可使用积分
USABLE_CONPON = 2 #只可使用优惠券
ONLY_ONE = 3 #仅可用一项
class IntegralStrategySttings(models.Model):
	"""
	积分策略配置
	"""
	webapp_id = models.CharField(max_length=20)
	click_shared_url_increase_count_after_buy = models.IntegerField(verbose_name='点击分享链接为购买后的分享者增加的额度', default=0)
	click_shared_url_increase_count_before_buy = models.IntegerField(verbose_name='点击分享链接为未购买的分享者增加的额度', default=0)
	buy_increase_count_for_father = models.IntegerField(verbose_name='成为会员增加额度', default=0)
	increase_integral_count_for_brring_customer_by_qrcode = models.IntegerField(verbose_name='使用二维码带来用户增加的额度', default=0)
	integral_each_yuan = models.IntegerField(verbose_name='一元是多少积分', default=0)
	usable_integral_or_conpon = models.IntegerField(verbose_name='积分与优惠券可同时使用', default=USABLE_BOTH)
	#v2
	be_member_increase_count = models.IntegerField(verbose_name='成为会员增加额度', default=0)
	order_money_percentage_for_each_buy = models.CharField(max_length=25, verbose_name="每次购物后，额外积分（以订单金额的百分比计算）", default="0.0")
	buy_via_offline_increase_count_for_author = models.IntegerField(verbose_name='线下会员购买为推荐者增加的额度', default=0)
	click_shared_url_increase_count = models.IntegerField(verbose_name='分享链接给好友点击', default=0)
	buy_award_count_for_buyer = models.IntegerField(verbose_name='购物返积分额度', default=0)
	buy_via_shared_url_increase_count_for_author = models.IntegerField(verbose_name='通过分享链接购买为分享者增加的额度', default=0)
	buy_via_offline_increase_count_percentage_for_author = models.CharField(max_length=25, verbose_name="线下会员购买为推荐者额外增加的额度(以订单金额的百分比计算）", default="0.0")
	use_ceiling = models.IntegerField(default=-1, verbose_name='订单积分抵扣上限')
	review_increase = models.IntegerField(default=0, verbose_name='商品好评送积分')
	is_all_conditions = models.BooleanField(default=False,verbose_name='自动升级条件')

	class Meta(object):
		db_table = 'member_integral_strategy_settings'


class MemberTag(models.Model):
	"""
	表示会员的标签(分组)
	"""
	webapp_id = models.CharField(max_length=16)
	name = models.CharField(max_length=100)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta(object):
		db_table = 'member_tag'
		verbose_name = '会员分组'
		verbose_name_plural = '会员分组'

	DEFAULT_TAG_NAME = u'未分组'

#########################################################################
# MemberHasTag
#########################################################################
class MemberHasTag(models.Model):
	member = models.ForeignKey(Member)
	member_tag = models.ForeignKey(MemberTag)

	class Meta(object):
		db_table = 'member_has_tag'
		verbose_name = '会员所属分组'
		verbose_name_plural = '会员所属分组'


class MemberSharedUrlInfo(models.Model):
	member = models.ForeignKey(Member)
	shared_url = models.CharField(max_length=1024)
	shared_url_digest = models.CharField(max_length=32)
	pv = models.IntegerField(default=1)
	leadto_buy_count = models.IntegerField(default=0)
	title = models.CharField(max_length=256, default='')
	cr = models.FloatField(default=0.0)
	followers = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta(object):
		db_table = 'member_shared_url_info'
		verbose_name = '分享链接信息'
		verbose_name_plural = '分享链接信息'


class MemberClickedUrl(models.Model):
	url = models.CharField(max_length=1024)
	url_digest = models.CharField(max_length=32) #md5
	mid = models.IntegerField()
	followed_mid = models.IntegerField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta(object):
		db_table = 'member_clicked_url'
		verbose_name = '会员url点击记录'
		verbose_name_plural = '会员url点击记录'


class MallOrderFromSharedRecord(models.Model):
	"""
	add by bert 记录通过分享链接下单 订单号和分享者信息
	"""
	order_id = models.IntegerField()
	fmt = models.CharField(default='', max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间

	class Meta:
		verbose_name = "通过分享链接订单"
		verbose_name_plural = "通过分享链接订单"
		db_table = "mall_order_from_shared_record"


FIRST_SUBSCRIBE = u'首次关注'
#FOLLOWER_CLICK_SHARED_URL = u'好友奖励'
FOLLOWER_CLICK_SHARED_URL = u'好友点击分享链接奖励'
USE = u'购物抵扣'
RETURN_BY_SYSTEM = u'积分返还'
RETURN_BY_CANCEl_ORDER = u'取消订单 返还积分'
AWARD = u'积分领奖'
BUY_AWARD = u'购物返利'
#FOLLOWER_BUYED_VIA_SHARED_URL = u'好友奖励'
FOLLOWER_BUYED_VIA_SHARED_URL = u'好友通过分享链接购买奖励'
BRING_NEW_CUSTOMER_VIA_QRCODE = u'推荐扫码奖励'
MANAGER_MODIFY = '系统管理员修改'
MANAGER_MODIFY_ADD = '管理员赠送'
MANAGER_MODIFY_REDUCT = '管理员扣减'
CHANNEL_QRCODE = u'渠道扫码奖励'
BUY_INCREST_COUNT_FOR_FATHER = u'推荐关注的好友购买奖励'

class MemberIntegralLog(models.Model):
	member = models.ForeignKey(Member)
	webapp_user_id = models.IntegerField(default=0)
	event_type = models.CharField(max_length=64, verbose_name='引起积分变化事件类型')
	integral_count = models.IntegerField(default=0, verbose_name='积分量')
	follower_member_token = models.CharField(max_length=255, null=True, blank=True, verbose_name='所关注的会员的token')
	reason = models.CharField(max_length=255, default='')
	current_integral = models.CharField(default='0', max_length=255)
	manager = models.CharField(default='', max_length=255)
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='记录时间')

	class Meta(object):
		db_table = 'member_integral_log'
		verbose_name = '积分日志'
		verbose_name_plural = '积分日志'


class MemberBrowseRecord(models.Model):
	member = models.ForeignKey(Member)
	title = models.CharField(max_length=256, default='') #页面标题
	url = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta(object):
		db_table = 'member_browse_record'
		verbose_name = '会员浏览记录'
		verbose_name_plural = '会员浏览记录'


class MemberBrowseProductRecord(models.Model):
	member = models.ForeignKey(Member)
	owner_id = models.IntegerField(default=0)  #商家id
	product_id = models.IntegerField(default=0)  #商品id
	referer = models.CharField(max_length=256, default='') #从哪个页面过来的
	title = models.CharField(max_length=256, default='') #页面标题
	url = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta(object):
		db_table = 'member_browse_product_record'
		verbose_name = '会员浏览商品详情记录'
		verbose_name_plural = '会员浏览商品详情记录'


class ChannelDistributionQrcodeSettings(models.Model):
	"""
	渠道分销二维码
	"""
	owner = models.ForeignKey(User)  # 所有者?
	bing_member_title = models.CharField(max_length=512)  # 关联会员头衔
	award_prize_info = models.TextField(default='{"id":-1,"name":"no-prize"}')  # 关注奖励,奖品信息
	reply_type = models.IntegerField(default=0)  # 扫码后行为：0普通关注一致，1回复文字，2回复图文
	reply_detail = models.TextField(default='')  # 回复文字, 当reply_type为1时有效
	reply_material_id = models.IntegerField(default=0) # 图文id，reply_type为2时有效 ?
	coupon_ids = models.TextField()  # 配置过的优惠券id集合
	bing_member_id = models.IntegerField(default=0) # 关联会员:创建二维码时选择关联的会员的ID
	return_standard = models.IntegerField(default=0)  # 多少天结算标准
	group_id = models.IntegerField(default=-1)  # 会员分组
	distribution_rewards = models.BooleanField(default=False)  # 分销奖励 False:没有 True:佣金
	commission_rate = models.IntegerField()  # 佣金返现率
	minimun_return_rate = models.IntegerField()  # 最低返现折扣
	commission_return_standard = models.DecimalField(max_digits=65, decimal_places=2)  # 佣金返现标准
	ticket = models.CharField(default='', max_length=256)  # ticket

	bing_member_count = models.IntegerField(default=0)  # 关注数量,该二维码下边的关注人数
	total_transaction_volume = models.DecimalField(max_digits=65, decimal_places=2, default=0)  # 总交易额:二维码自创建以来的所有交易额
	total_return = models.DecimalField(max_digits=65, decimal_places=2, default=0)  # 返现总额: 二维码所有的返现总额, 只包含已经体现的金额
	will_return_reward = models.DecimalField(max_digits=65, decimal_places=2, default=0)  # 实施奖励
	created_at = models.DateTimeField(auto_now_add=True) # 添加时间

	class Meta:
		db_table = 'market_tool_channel_distribution_qrcode_setting'


class MemberCard(models.Model):
	"""
	会员卡
	"""
	owner_id = models.IntegerField() #会员id
	member_id = models.IntegerField() #会员id
	batch_id = models.CharField(max_length=50, default="") #微众卡批次id alter table member_card  add column batch_id varchar(50) default '';
	card_number = models.CharField(max_length=50) #微众卡卡号
	card_password = models.CharField(max_length=512) #微众卡密码
	card_name = models.CharField(max_length=512) #微众卡名字
	is_active = models.BooleanField(default=True) #会员身份是否有效 以后扩展的备用字段
	created_at = models.DateTimeField(auto_now_add=True) #发放时间

	class Meta(object):
		db_table = 'member_card'

class MemberCardLog(models.Model):
	"""
	会员卡记录，仅交易记录  下单 和 取消订单
	"""
	member_card = models.ForeignKey(MemberCard)  #member card id
	price = models.FloatField(default=0.0)  # 浮动金额
	trade_id = models.CharField(max_length=50, default="") #支付流水号alter table member_card_log  add column trade_id varchar(50) default '';
	order_id = models.CharField(max_length=200, default="") #订单号 alter table member_card_log  add column order_id varchar(200) default '';
	reason = models.CharField(max_length=512)  # 原因
	created_at = models.DateTimeField(auto_now_add=True) #时间
	
	class Meta(object):
		db_table = 'member_card_log'


VIP_PAGE = 1  #VIP会员首页
WANT_TO_BUY = 2  #VIP会员我想买页面
class AdClicked(models.Model):
	"""
	广告点击
	"""
	member_id = models.IntegerField() #会员id
	type = models.IntegerField(default=VIP_PAGE)  #页面
	created_at = models.DateTimeField(auto_now_add=True) #时间
	
	class Meta(object):
		db_table = 'ad_clicked'


class MemberCardPayOrder(models.Model):
	"""
	会员卡支付订单 duhao
	"""
	owner_id = models.IntegerField() #商家id
	member_id = models.IntegerField() #会员id
	batch_id = models.CharField(max_length=50, default="") #微众卡批次id
	order_id = models.CharField(max_length=50) #支付订单id
	batch_name = models.CharField(max_length=200) #会员卡名称
	price = models.FloatField(default=0.0)  #支付金额
	is_paid = models.BooleanField(default=False)  #是否支付成功
	created_at = models.DateTimeField(auto_now_add=True) #创建时间
	paid_at = models.DateTimeField(null=True) #支付时间
	
	class Meta(object):
		db_table = 'member_card_pay_order'


SOURCE_JD = 1  #京东
SOURCE_TMALL = 2  #天猫
SOURCE2NAME = {
	SOURCE_JD: u'京东',
	SOURCE_TMALL: u'天猫'
}

STATUS_NOT_REACH = 1
STATUS_REACH = 2
STATUS_PURCHASE = 3
STATUS_SHELVES_ON = 4
STATUS2TEXT = {
	STATUS_NOT_REACH: u'未达标',
	STATUS_REACH: u'人气达标，采购中',
	STATUS_PURCHASE: u'采购完成，等待上架',
	STATUS_SHELVES_ON: u'上架完成'
}
class WantToBuy(models.Model):
	"""
	我想买
	"""
	owner_id = models.IntegerField() #商家id
	member = models.ForeignKey(Member)
	source = models.IntegerField(default=SOURCE_JD)  #来源
	product_id = models.IntegerField(default=0) #上架后的商品id，预留字段
	product_name = models.CharField(max_length=128) #商品名称
	status = models.IntegerField(default=STATUS_NOT_REACH)  #状态
	support_num = models.IntegerField(default=0)  #支持人数
	pics = models.CharField(max_length=1024) #图片
	is_accept_other_brand = models.BooleanField(default=True)  #是否接受同类其他品牌
	reach_num_at = models.DateTimeField(null=True) #人气达标时间
	purchase_completed_at = models.DateTimeField(null=True) #采购完成时间
	shelves_on_at = models.DateTimeField(null=True) #上架时间
	created_at = models.DateTimeField(auto_now_add=True) #创建时间

	class Meta(object):
		db_table = 'member_want_to_buy'

class WantToBuySupport(models.Model):
	"""
	我想买支持记录
	"""
	want_to_buy = models.ForeignKey(WantToBuy)
	member = models.ForeignKey(Member)
	content = models.CharField(max_length=512) #支持内容
	created_at = models.DateTimeField(auto_now_add=True) #创建时间

	class Meta(object):
		db_table = 'member_want_to_buy_support'


class TengyiMember(models.Model):
	"""
	腾易微众星级会员表
	"""
	member_id = models.IntegerField(default=0)
	recommend_by_member_id = models.IntegerField(default=0) #推荐人id
	level = models.IntegerField(default=1) #星级
	card_number = models.CharField(default='', max_length=50) #绑定会员卡id
	created_at = models.DateTimeField(auto_now_add=True)  # 成为会员的时间

	class Meta(object):
		db_table = 'tengyi_member'

class TengyiMemberRelation(models.Model):
	"""
	腾易微众星级会员推荐关系表(待成为星级会员)
	"""
	member_id = models.IntegerField(default=0)
	recommend_by_member_id = models.IntegerField(default=0)  # 推荐人id
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta(object):
		db_table = 'tengyi_member_relation'

class TengyiRebateLog(models.Model):
	"""
	腾易微众星级会员返利记录表
	"""
	member_id = models.IntegerField(default=0)
	is_self_order = models.BooleanField(default=False) #是否自己的订单返利
	supply_member_id = models.IntegerField(default=0) #返利会员id
	is_exchanged = models.BooleanField(default=False) #是否已返利
	exchanged_at = models.DateTimeField(default=datetime.strptime('2000-01-01', '%Y-%m-%d')) #返利时间
	rebate_money = models.FloatField(default=0) #返利金额
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta(object):
		db_table = 'tengyi_rebate_log'

DEFAULT_DATETIME = datetime.strptime('2000-01-01', '%Y-%m-%d')
class TengyiMemberRebateCycle(models.Model):
	"""
	腾易微众星级会员推荐返利周期
	"""
	member_id = models.IntegerField(default=0)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	is_receive_reward = models.BooleanField(default=False) #是否已获得购物返利
	receive_reward_at = models.DateTimeField(default=DEFAULT_DATETIME) #获得推荐返利时间
	is_recommend_member_receive_reward = models.BooleanField(default=False) #是否被推荐人已获得推荐返利
	recommend_member_rebate_money = models.FloatField(default=0) #推荐人返利金额
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta(object):
		db_table = 'tengyi_member_rebate_cycle'
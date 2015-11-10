#coding: utf8
from datetime import datetime

from db import models
from wapi.user.models import User
from core.decorator import cached_property
from utils.string_util import hex_to_byte, byte_to_hex
import resource

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

	#############################################################################
	# integral_info: 获取积分信息
	#############################################################################
	@property
	def integral_info(self):
		count = Member.objects.get(id=self.member_id).integral
		count_per_yuan = IntegralStrategySttings.objects.get(webapp_id=self.webapp_id).integral_each_yuan
		return {
			'count': count,
			'count_per_yuan': count_per_yuan
		}

	@property
	def member_count(self):
		return Member.select().dj_where(grade_id=self.id, is_for_test=False, is_subscribed=True).count()

	DEFAULT_GRADE_NAME = u'普通会员'
	@staticmethod
	def get_default_grade(webapp_id):
		try:
			return MemberGrade.get(webapp_id=webapp_id, is_default_grade=True)
		except:
			return MemberGrade.create(
				webapp_id = webapp_id,
				name = MemberGrade.DEFAULT_GRADE_NAME,
				upgrade_lower_bound = 0,
				is_default_grade = True,
				is_auto_upgrade = True
			)

	@staticmethod
	def get_all_grades_list(webapp_id):
		if webapp_id is None:
			return []
		member_grades = MemberGrade.select().dj_where(webapp_id=webapp_id).order_by('id')

		for member_grade in member_grades:
			member_grade.pay_money = '%.2f' % member_grade.pay_money
		return member_grades


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
	access_token = models.CharField(max_length=64)
	is_for_test = models.BooleanField(default=False)
	openid = models.CharField(max_length=64)
	uuid = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='加入日期')

	def is_from_weixin(self):
		return SOCIAL_PLATFORM_WEIXIN == self.platform

	def is_from_qq(self):
		return SOCIAL_PLATFORM_QQ == self.platform

	def is_frm_sina_weibo(self):
		return SOCIAL_PLATFORM_SINAWEIBO == self.platform

	class Meta(object):
		db_table = 'binding_social_account'


class WebAppUser(models.Model):
	"""
	WebApp的用户
	"""
	token = models.CharField(max_length=100)
	webapp_id = models.CharField(max_length=16)
	member_id = models.IntegerField(default=0) #会员记录的id
	has_purchased = models.BooleanField(default=False) #是否购买过
	father_id = models.IntegerField(default=0) #会员记录的id
	created_at = models.DateTimeField(auto_now_add=True) #创建时间

	class Meta(object):
		db_table = 'member_webapp_user'

	@staticmethod
	def get_member_by_webapp_user_id(id):
		try:
			webapp_user = WebAppUser.get(id=id)
			if webapp_user.member_id != 0 and webapp_user.member_id != -1:
				return Member.get(id=webapp_user.member_id)
			elif father_id != 0:
				webapp_user = WebAppUser.get(id=webapp_user.id)
				if webapp_user.member_id != 0 and webapp_user.member_id != -1:
					return Member.get(id=webapp_user.member_id)
				else:
					return None
			else:
				return None
		except:
			return None

	@property
	def ship_info(self):
		"""
		收货地址
		"""
		if hasattr(self, '_ship_info'):
			return self._ship_info
		else:
			try:
				_ship_infos = list(self.ship_infos.filter(is_selected=True))
				if len(_ship_infos) > 0:
					self._ship_info = _ship_infos[0]

				return self._ship_info
			except:
				return None

	@property
	def ship_infos(self):
		"""
		收货地址集合
		"""
		if hasattr(self, '_ship_infos'):
			return self._ship_infos
		else:
			try:
				# 删除空的条目
				#ShipInfo.select().dj_where(webapp_user_id=self.id, ship_name='').delete()
				self._ship_infos = ShipInfo.select().dj_where(webapp_user_id=self.id, is_deleted=False)
				return self._ship_infos
			except:
				return None

	def update_ship_info(self, ship_name=None, ship_address=None, ship_tel=None, area=None, ship_id=None):
		"""
		更新收货地址
		"""
		ship_infos = ShipInfo.select().dj_where(webapp_user_id=self.id, is_selected=True)
		ShipInfo.select().dj_where(webapp_user_id=self.id).update(is_selected=False)
		if ship_id > 0:
			ShipInfo.select().dj_where(id=ship_id).update(
				ship_tel = ship_tel,
				ship_address = ship_address,
				ship_name = ship_name,
				area = area,
				is_selected = True
			)
		elif ship_infos.count() > 0 and ship_id is None:
			ship_infos.update(
				ship_tel = ship_tel,
				ship_address = ship_address,
				ship_name = ship_name,
				area = area,
				is_selected = True
			)
		else:
			ship_id = ShipInfo.objects.create(
				webapp_user_id = self.id,
				ship_tel = ship_tel,
				ship_address = ship_address,
				ship_name = ship_name,
				area = area
			).id
		return ship_id

	@property
	def is_member(self):
		return self.member_id > 0

	def can_use_integral(self, integral):
		"""
		检查是否可用数量为integral的积分
		"""
		if not self.is_member:
			return False

		remianed_integral = Member.get(id=self.member_id).integral
		if remianed_integral >= integral:
			return True
		else:
			return False

	@cached_property
	def integral_info(self):
		"""
		积分信息
		"""
		try:
			self.member = Member.get(id=self.member_id)
			member = self.member
			count = member.integral
			target_grade_id = member.grade_id
			target_member_grade = self.webapp_owner_info.member2grade.get(target_grade_id, None)
			if target_member_grade:
				usable_integral_percentage_in_order = target_member_grade.usable_integral_percentage_in_order
			else:
				usable_integral_percentage_in_order = 100
		except:
			count = 0
			usable_integral_percentage_in_order = 100

		#计算积分金额
		if self.webapp_owner_info and hasattr(self.webapp_owner_info, 'integral_strategy_settings'):
			integral_strategy_settings = self.webapp_owner_info.integral_strategy_settings
		else:
			integral_strategy_settings = IntegralStrategySttings.get(webapp_id=self.webapp_id)

		count_per_yuan = integral_strategy_settings.integral_each_yuan

		usable_integral_or_conpon = integral_strategy_settings.usable_integral_or_conpon
		return {
			'count': count,
			'count_per_yuan': count_per_yuan,
			'usable_integral_percentage_in_order' : usable_integral_percentage_in_order,
			'usable_integral_or_conpon' : usable_integral_or_conpon
		}

	def use_integral(self, integral_count):
		"""
		使用积分
		"""
		from integral import use_integral_to_buy

		if integral_count == 0:
			return 0.0

		member = Member.get(id=self.member_id)
		return use_integral_to_buy(member, integral_count)

	#############################################################################
	# coupons: 获取用户的优惠券信息
	#############################################################################
	@property
	def coupons(self):
		"""
		优惠券信息
		"""
		if self.member_id == 0:
			return []
		else:
			return resource.get('member', 'member_coupons', {
				'member': self,
				'return_model': True
			})

	def use_coupon_by_coupon_id(self, member_id, coupon_id, price=0, webapp_owner_id=-1):
		"""
		通过优惠券号使用优惠券
		"""
		if coupon_id > 0:
			try:
				coupon = coupon_model.Coupon.objects.get(owner_id=webapp_owner_id, coupon_id=coupon_id, status=coupon_model.COUPON_STATUS_UNUSED)
			except:
				raise IOError
			coupon.money = float(coupon.money)
			coupon_role = coupon_model.CouponRule.objects.get(id=coupon.coupon_rule_id)
			coupon.valid_restrictions = coupon_role.valid_restrictions
			if coupon.valid_restrictions > price and coupon.valid_restrictions!=-1:
				raise ValueError
			coupon_model.Coupon.select().dj_where(coupon_id=coupon_id).update(status=coupon_model.COUPON_STATUS_USED)
		else:
			coupon = coupon_model.Coupon()
			coupon.money = 0.0
			coupon.id = coupon_id

		return coupon

	def complete_payment(self, request, order=None):
		"""
		完成支付，进行支付后的处理
		"""
		if request is None:
			return

		# from integral import increase_for_buy_via_shared_url
		# #首先进行积分的处理
		# #print '===========innnnnnnnnnnnnnnnnnnnnnnnnnnnnnn'
		# increase_for_buy_via_shared_url(request, order)
		#进行分享链接的相关计算
		from modules.member.util import  process_payment_with_shared_info
		process_payment_with_shared_info(request)

	def set_purchased(self):
		"""
		设置已购买标识
		"""
		if not self.has_purchased:
			WebAppUser.objects.update(has_purchased=True)

	def consume_integral(self, count, type):
		"""
		使用积分
		"""
		member = Member.from_webapp_user(self)
		if member is None:
			return

		try:
			member.consume_integral(count, type)
		except:
			notify_msg = u"消费积分出错，会员id:{}, type:{}".format(member.id, type)
			watchdog_fatal(notify_msg)

def _generate_member_token(member, social_account):
	return "{}{}{}{}".format(
		member.webapp_id,
		social_account.platform,
		time.strftime("%Y%m%d"),
		(''.join(random.sample(string.ascii_letters + string.digits, 6))) + str(member.id))


import random
def _create_random():
	date = str(time.time()*1000)
	sample_list = ['0','1','2','3','4','5','6','7','8','9','a', 'b', 'c', 'd', 'e']
	random_str = ''.join(random.sample(string.ascii_letters + string.digits, 10))
	random_str = date + random_str
	return random_str

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
	user_icon = models.CharField(max_length=1024, verbose_name='会员头像')
	integral = models.IntegerField(default=0, verbose_name='积分')
	created_at = models.DateTimeField(auto_now_add=True)
	grade = models.ForeignKey(MemberGrade)
	experience = models.IntegerField(default=0, verbose_name='经验值')
	remarks_name = models.CharField(max_length=32, verbose_name='备注名')
	remarks_extra = models.TextField(verbose_name='备注信息')
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

	class Meta(object):
		db_table = 'member_member'

	def __unicode__(self):
		return u'<member: %s %s>' % (self.webapp_id, self.username)

	@property
	def get_webapp_user_ids(self):
		return [webapp_user.id for webapp_user in WebAppUser.select().dj_where(member_id=self.id)]


	@staticmethod
	def from_webapp_user(webapp_user):
		if (webapp_user is None) or (not webapp_user.is_member):
			return None

		try:
			return Member.select().dj_where(id=webapp_user.member_id)
		except:
			#TODO 进行异常处理？？
			return None

	@staticmethod
	def members_from_webapp_user_ids(webapp_user_ids):
		if not webapp_user_ids:
			return []

		webappuser2member = dict([(u.id, u.member_id) for u in WebAppUser.select().dj_where(id__in=webapp_user_ids)])
		member_ids = set(webappuser2member.values())
		id2member = dict([(m.id, m) for m in Member.select().dj_where(id__in=member_ids)])

		for webapp_user_id, member_id in webappuser2member.items():
			webappuser2member[webapp_user_id] = id2member.get(member_id, None)

		return webappuser2member

	@staticmethod
	def update_last_visit_time(member):
		if member is None:
			return

		member.last_visit_time = datetime.now()
		member.save()

	@property
	def username(self):
		if hasattr(self, '_username'):
			return self._username

		self._username = hex_to_byte(self.username_hexstr)
		return self._username

	@username.setter
	def username(self, username):
		self.username_hexstr = byte_to_hex(username)

	@staticmethod
	def get_by_username(username):
		hexstr = byte_to_hex(username)
		return list(Member.select().dj_where(username_hexstr=hexstr))

	@cached_property
	def username_for_html(self):
		if hasattr(self, '_username_for_html'):
			return self._username_for_html

		if (self.username_hexstr is not None) and (len(self.username_hexstr) > 0):
			self._username_for_html = encode_emojicons_for_html(self.username_hexstr, is_hex_str=True)
		else:
			self._username_for_html = encode_emojicons_for_html(self.username)

		try:
			#解决用户名本身就是字节码串导致不能正常转换得问题，例如ae
			self._username_for_html.decode('utf8')
		except:
			self._username_for_html = self.username_hexstr

		return self._username_for_html

	@cached_property
	def username_for_title(self):
		try:
			username = unicode(self.username_for_html, 'utf8')
			username = re.sub('<[^<]+?>', '', username)
			return username
		except:
			return self.username_for_html

	@cached_property
	def username_truncated(self):
		try:
			username = unicode(self.username_for_html, 'utf8')
			_username = re.sub('<[^<]+?><[^<]+?>', ' ', username)
			if len(_username) <= 5:
				return username
			else:
				name_str = username
				span_list = re.findall(r'<[^<]+?><[^<]+?>', name_str) #保存表情符

				output_str = ""
				count = 0

				if not span_list:
					return u'%s...' % name_str[:5]

				for span in span_list:
				    length = len(span)
				    while not span == name_str[:length]:
				        output_str += name_str[0]
				        count += 1
				        name_str = name_str[1:]
				        if count == 5:
				            break
				    else:
				        output_str += span
				        count += 1
				        name_str = name_str[length:]
				        if count == 5:
				            break
				    if count == 5:
				        break
				return u'%s...' % output_str
		except:
			return self.username_for_html[:5]

	@cached_property
	def username_size_ten(self):
		try:
			username = unicode(self.username_for_html, 'utf8')
			_username = re.sub('<[^<]+?><[^<]+?>', ' ', username)
			if len(_username) <= 10:
				return username
			else:
				name_str = username
				span_list = re.findall(r'<[^<]+?><[^<]+?>', name_str) #保存表情符

				output_str = ""
				count = 0

				if not span_list:
					return u'%s...' % name_str[:10]

				for span in span_list:
				    length = len(span)
				    while not span == name_str[:length]:
				        output_str += name_str[0]
				        count += 1
				        name_str = name_str[1:]
				        if count == 10:
				            break
				    else:
				        output_str += span
				        count += 1
				        name_str = name_str[length:]
				        if count == 10:
				            break
				    if count == 10:
				        break
				return u'%s...' % output_str
		except:
			return self.username_for_html[:10]

	@property
	def friends(self):
		if hasattr(self, '_friends'):
			return self._friends

		self._friends = MemberFollowRelation.get_follow_members_for(self.id)
		return self._friends

	@staticmethod
	def count(webapp_id):
		return Member.select().dj_where(webapp_id=webapp_id, status__in=[CANCEL_SUBSCRIBED, SUBSCRIBED], is_for_test=False).count()

	@staticmethod
	def update_factor(member):
		friends_count =len(MemberFollowRelation.get_follow_members_for(member.id, '1'))
		friends_from_qrcodes = len(MemberFollowRelation.get_follow_members_for(member.id, '1', True))
		#总点击数
		click_counts = MemberSharedUrlInfo.select().dj_where(member=member).aggregate(Sum("pv"))

		if click_counts["pv__sum"]:
			click_counts = float(click_counts["pv__sum"])
		else:
			click_counts = 0

		if (click_counts + friends_from_qrcodes) != 0:
			factor =  float('%.2f' % (float(friends_count + friends_from_qrcodes) / float(friends_from_qrcodes + click_counts)))
			if member.factor != factor:
				Member.select().dj_where(id=member.id).update(factor=factor)


	def consume_integral(self, count, type):
		if type is None:
			return

		from integral import increase_member_integral
		increase_member_integral(self, -count, type, to_task=False)

	def update_member_info(self, username, phone_number):
		if (username is None) or (phone_number is None):
			return

		MemberInfo.select().dj_where(member=self).update(
			name = username,
			phone_number = phone_number
		)

	@property
	def member_info(self):
		try:
			return MemberInfo.objects.get(member=self)
		except:
			return MemberInfo.objects.create(
				member = Member.objects.get(id=self.id),
				name = ''
				)


	@staticmethod
	def increase_friend_count(member_ids):
		from django.db import connection, transaction
		cursor = connection.cursor()
		cursor.execute('update member_member set friend_count = friend_count + 1 where id in (%s);' % (member_ids))
		transaction.commit_unless_managed()

	@property
	def member_open_id(self):
		try:
			return MemberHasSocialAccount.select().dj_where(member=self)[0].account.openid
		except:
			return None

	@staticmethod
	def get_members(webapp_id):
		return list(Member.select().dj_where(webapp_id=webapp_id, is_subscribed=True, is_for_test=False))

	@staticmethod
	def get_member_list_by_grade_id(grade_id):
		return list(Member.select().dj_where(grade_id=grade_id, is_subscribed=True, is_for_test=False))

	@staticmethod
	def get_member_by_weixin_user_id(id):
		try:
			weixin_user = WeixinUser.objects.get(id=id)
			social_account = SocialAccount.objects.get(openid=weixin_user.username, webapp_id=weixin_user.webapp_id)
			if MemberHasSocialAccount.select().dj_where(account=social_account).count() > 0:
				return MemberHasSocialAccount.select().dj_where(account=social_account)[0].member
			else:
				return None
		except:
			return None

	@staticmethod
	def update_member_grade(member, grade_id):
		"""
		updated by zhu tianqi,修改为会员等级高于目标等级时不降级
		"""
		if member.grade_id < grade_id:
			from django.db import connection, transaction
			cursor = connection.cursor()
			cursor.execute('update member_member set grade_id = %d where id = %d;' % (grade_id, member.id))
			transaction.commit_unless_managed()

	@property
	def is_binded(self):
		if MemberInfo.select().dj_where(member_id=self.id).count() > 0:
			member_info = MemberInfo.select().dj_where(member_id=self.id)[0]
			return member_info.is_binded
		else:
			MemberInfo.objects.create(
				member=self,
				name='',
				weibo_nickname=''
				)
			return False


	@staticmethod
	def create_member(openid, webapp_id, for_oauthed=False):
		token = md5('%s_%s' % (webapp_id, openid)).hexdigest()
		sure_created = False		
		try:
			social_account = SocialAccount.get(webapp_id = webapp_id, openid = openid)
			print 'get_social_account>>>>>>>>>>>>>>>>>:',social_account
		except:
			social_account, sure_created = SocialAccount.get_or_create(
				platform = 0,
				webapp_id = webapp_id,
				openid = openid,
				token = token,
				is_for_test = False,
				access_token = '',
				uuid=''
			)
			print 'create_social_account>>>>>>>>>>>>>>>>>:',social_account
		if not sure_created and MemberHasSocialAccount.filter(webapp_id=webapp_id, account=social_account).count() >  0:
			return True, False
		#默认等级
		member_grade = MemberGrade.get_default_grade(webapp_id)

		if for_oauthed:
			is_subscribed = False
			status = NOT_SUBSCRIBED
		else:
			is_subscribed = True
			status = SUBSCRIBED

		#temporary_token = _create_random()
		member_token = _generate_member_token(social_account, social_account)
		member = Member.create(
			webapp_id = social_account.webapp_id,
			user_icon = '',#social_account_info.head_img if social_account_info else '',
			username_hexstr = '',
			grade = member_grade,
			remarks_name = '',
			token = member_token,
			is_for_test = social_account.is_for_test,
			is_subscribed = is_subscribed,
			status = status
		)
		if not member:
			return None

		MemberHasSocialAccount.create(
					member = member,
					account = social_account,
					webapp_id = webapp_id
					)

		WebAppUser.create(
			token = member.token,
			webapp_id = webapp_id,
			member_id = member.id
			)

		#添加默认分组
		#try:
		default_member_tag = MemberTag.get_default_tag(webapp_id)
		MemberHasTag.add_tag_member_relation(member, [default_member_tag.id])
		return member, True
		# except:
		# 	pass




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

	@staticmethod
	def get_follow_members_for(member_id, is_fans='0', is_from_qrcode=False):
		if member_id is None or member_id <= 0:
			return []

		try:
			if is_fans != '0' and is_fans != None:
				follow_relations = MemberFollowRelation.objects.filter(member_id=member_id, is_fans=True).order_by('-id')
			else:
				follow_relations = MemberFollowRelation.objects.filter(member_id=member_id).order_by('-id')

			follow_member_ids = [relation.follower_member_id for relation in follow_relations]

			if is_from_qrcode:
				return Member.objects.filter(id__in=follow_member_ids,source=SOURCE_MEMBER_QRCODE,status__in=[SUBSCRIBED, CANCEL_SUBSCRIBED])
			else:
				return Member.objects.filter(id__in=follow_member_ids, status__in=[SUBSCRIBED, CANCEL_SUBSCRIBED])
		except:
			return []

	@staticmethod
	def get_follow_members_for_shred_url(member_id):
		if member_id is None or member_id <= 0:
			return []

		try:
			follow_relations = MemberFollowRelation.objects.filter(member_id=member_id, is_fans=True).order_by('-id')
			follow_member_ids = [relation.follower_member_id for relation in follow_relations]
			return Member.objects.filter(id__in=follow_member_ids, source=SOURCE_BY_URL, status__in=[SUBSCRIBED, CANCEL_SUBSCRIBED])
		except:
			return []


	@staticmethod
	def is_fan(member_id, follower_member_id):
		return 1 if MemberFollowRelation.objects.filter(member_id=member_id, follower_member_id=follower_member_id, is_fans=True).count() > 0 else 0

	@staticmethod
	def is_father(member_id, follow_mid):
		return 1 if MemberFollowRelation.objects.filter(member_id=follow_mid, follower_member_id=member_id, is_fans=True).count() > 0 else 0

	@staticmethod
	def get_father_member(member_id):
		member_relation = MemberFollowRelation.objects.filter(follower_member_id=member_id, is_fans=True)[0] if MemberFollowRelation.objects.filter(follower_member_id=member_id, is_fans=True).count() > 0 else None
		if member_relation:
			try:
				return Member.objects.get(id=member_relation.member_id)
			except:
				return None
		return None


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

	@staticmethod
	def get_integral_each_yuan(webapp_id):
		if IntegralStrategySttings.select().dj_where(webapp_id=webapp_id).count() > 0:
			return IntegralStrategySttings.select().dj_where(webapp_id=webapp_id)[0].integral_each_yuan
		else:
			return None

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
	@staticmethod
	def get_default_tag(webapp_id):
		try:
			return MemberTag.get(webapp_id=webapp_id, name="未分组")
		except:
			return MemberTag.create(webapp_id=webapp_id, name="未分组")


	@staticmethod
	def get_member_tags(webapp_id):
		if webapp_id:
			if MemberTag.filter(webapp_id=webapp_id, name="未分组").count() == 0:
				MemberTag.create(webapp_id=webapp_id, name="未分组")
			return list(MemberTag.filter(webapp_id=webapp_id))
		else:
			return []

	@staticmethod
	def get_member_tag(webapp_id, name):
		return MemberTag.filter(webapp_id=webapp_id, name=name)[0] if MemberTag.filter(webapp_id=webapp_id, name=name).count() > 0 else None

	@staticmethod
	def create(webapp_id, name):
		return MemberTag.create(webapp_id=webapp_id, name=name)

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

	@staticmethod
	def get_member_has_tags(member):
		if member:
			return list(MemberHasTag.filter(member=member))
		return []

	@staticmethod
	def get_tag_has_member_count(tag):
		return MemberHasTag.filter(member_tag=tag).count()

	@staticmethod
	def is_member_tag(member, member_tag):
		if member and member_tag:
			return MemberHasTag.filter(member=member, member_tag_id=member_tag.id).count()
		else:
			return False

	@staticmethod
	def delete_tag_member_relation_by_member(member):
		if member:
			MemberHasTag.filter(member=member).delete()

	@staticmethod
	def add_tag_member_relation(member, tag_ids_list):
		print '>>>>>>>>>>>>>>>>>tag_ids_list:::',tag_ids_list
		if member and len(tag_ids_list) > 0:
			for tag_id in tag_ids_list:
				if tag_id:
					if MemberHasTag.select().dj_where(member=member, member_tag_id=tag_id).count() == 0:
						print '>>>>>>>>>>>>>>>>>tag_id:::',tag_id
						MemberHasTag.create(member=member, member_tag=tag_id)
	# @staticmethod
	# def get_member_list_by_tag_id(tag_id):
	# 	if tag_id:
	# 		members = []
	# 		for member_has_tag in MemberHasTag.filter(member_tag_id=tag_id):
	# 			members.append(member_has_tag.member)
	# 		return members
	# 	else:
	# 		return []

	# @staticmethod
	# def add_members_tag(default_tag_id, tag_id, member_ids):
	# 	if tag_id:
	# 		for member_id in member_ids:
	# 			if MemberHasTag.filter(member_tag_id=default_tag_id, member_id=member_id).count() > 0:
	# 				MemberHasTag.filter(member_tag_id=default_tag_id, member_id=member_id).delete()
	# 			if MemberHasTag.filter(member_tag_id=tag_id, member_id=member_id).count() == 0:
	# 				MemberHasTag.create(member_id=member_id, member_tag_id=tag_id)

	# @staticmethod
	# def get_tag_has_sub_member_count(tag):
	# 	if isinstance(tag, MemberTag):
	# 		return MemberHasTag.filter(member_tag=tag, member__status=SUBSCRIBED).count()
	# 	else:
	# 		return MemberHasTag.filter(member_tag_id=tag, member__status=SUBSCRIBED).count()

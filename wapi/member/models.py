#coding: utf8
from db import models
from wapi.user.models import User


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
		if IntegralStrategySttings.objects.filter(webapp_id=webapp_id).count() > 0:
			return IntegralStrategySttings.objects.filter(webapp_id=webapp_id)[0].integral_each_yuan
		else:
			return None


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
		return Member.objects.filter(grade_id=self.id, is_for_test=False, is_subscribed=True).count()

	DEFAULT_GRADE_NAME = u'普通会员'
	@staticmethod
	def get_default_grade(webapp_id):
		try:
			return MemberGrade.objects.get(webapp_id=webapp_id, is_default_grade=True)
		except:
			return MemberGrade.objects.create(
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
		member_grades = MemberGrade.objects.filter(webapp_id=webapp_id).order_by('id')

		for member_grade in member_grades:
			member_grade.pay_money = '%.2f' % member_grade.pay_money
		return member_grades
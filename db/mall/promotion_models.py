#coding: utf8
import copy
from datetime import datetime
import json

from eaglet.core.db import models
from db.account.models import User
from db.mall import models as mall_models
from eaglet.core import watchdog
import settings
from db.mall import models as mall_models
from db.member.models import Member

DEFAULT_DATETIME = datetime.strptime('2000-01-01', '%Y-%m-%d')


#########################################################################
# 促销活动相关model
#########################################################################
PROMOTION_TYPE_ALL = 0
PROMOTION_TYPE_FLASH_SALE = 1
PROMOTION_TYPE_PREMIUM_SALE = 2
PROMOTION_TYPE_PRICE_CUT = 3
PROMOTION_TYPE_COUPON = 4
PROMOTION_TYPE_INTEGRAL_SALE = 5
PROMOTION2TYPE = {
	PROMOTION_TYPE_FLASH_SALE: {
		"name": 'flash_sale',
		"display_name": u'限时抢购'
	},
	PROMOTION_TYPE_PREMIUM_SALE: {
		"name": 'premium_sale',
		"display_name": u'买&nbsp;赠'
	},
	PROMOTION_TYPE_PRICE_CUT: {
		"name": 'price_cut',
		"display_name": u'满&nbsp;减'
	},
	PROMOTION_TYPE_COUPON:  {
		"name": 'coupon',
		"display_name": u'优惠券'
	},
	PROMOTION_TYPE_INTEGRAL_SALE:  {
		"name": 'integral_sale',
		"display_name": u'积分抵扣'
	}
}
PROMOTIONSTR2TYPE = {
	'all': PROMOTION_TYPE_ALL,
	'flash_sale': PROMOTION_TYPE_FLASH_SALE,
	'premium_sale': PROMOTION_TYPE_PREMIUM_SALE,
	'price_cut': PROMOTION_TYPE_PRICE_CUT,
	'coupon': PROMOTION_TYPE_COUPON,
	'integral_sale': PROMOTION_TYPE_INTEGRAL_SALE
}
PROMOTION_STATUS_NOT_START = 1
PROMOTION_STATUS_STARTED = 2
PROMOTION_STATUS_FINISHED = 3
PROMOTION_STATUS_DELETED = 4
PROMOTION_STATUS_DISABLE = 5
PROMOTIONSTATUS2NAME = {
	PROMOTION_STATUS_NOT_START: u'未开始',
	PROMOTION_STATUS_STARTED: u'进行中',
	PROMOTION_STATUS_FINISHED: u'已结束',
	PROMOTION_STATUS_DELETED: u'已删除',
	PROMOTION_STATUS_DISABLE: u'已失效'
}


class Promotion(models.Model):
	"""
	促销活动
	"""
	owner = models.ForeignKey(User)
	name = models.CharField(max_length=256) #活动名
	promotion_title = models.CharField(max_length=256) #促销标题
	status = models.IntegerField(default=PROMOTION_STATUS_NOT_START) #促销状态
	start_date = models.DateTimeField() #开始日期
	end_date = models.DateTimeField() #结束日期
	type = models.IntegerField() #促销类型
	detail_id = models.IntegerField(default=0) #促销数据id
	member_grade_id = models.IntegerField(default=0) #会员等级
	created_at = models.DateTimeField(auto_now_add=True) #添加时间

	class Meta(object):
		db_table = 'mallpromotion_promotion'


class ProductHasPromotion(models.Model):
	"""
	<商品，促销>的关联
	"""
	product = models.ForeignKey(mall_models.Product)
	promotion = models.ForeignKey(Promotion)

	class Meta(object):
		db_table = 'mallpromotion_product_has_promotion'


#########################################################################
# FlashSale：限时抢购
#########################################################################
class FlashSale(models.Model):
	"""
	限时抢购
	"""
	owner = models.ForeignKey(User)
	limit_period = models.IntegerField(default=0) #限购周期
	promotion_price = models.FloatField(default=0.0) #限购价格
	count_per_purchase = models.IntegerField(default=1) #单人限购数量每次
	count_per_period = models.IntegerField(default=0)

	class Meta(object):
		db_table = 'mallpromotion_flash_sale'
		verbose_name = '限时抢购'
		verbose_name_plural = '限时抢购'


class PriceCut(models.Model):
	"""
	满减
	"""
	owner = models.ForeignKey(User)
	price_threshold = models.FloatField(default=0) #价格阈值
	cut_money = models.FloatField(default=0) #减价
	is_enable_cycle_mode = models.BooleanField(default=False) #是否启用循环满减

	class Meta(object):
		db_table = 'mallpromotion_price_cut'
		verbose_name = '满减'
		verbose_name_plural = '满减'


INTEGRAL_SALE_TYPE_PARTIAL = 0 #部分抵扣
INTEGRAL_SALE_TYPE_TOTAL = 1 #全额抵扣
class IntegralSale(models.Model):
	"""
	积分应用
	"""
	owner = models.ForeignKey(User)
	type = models.IntegerField(default=INTEGRAL_SALE_TYPE_PARTIAL) #积分抵扣类型
	discount = models.IntegerField(default=0) #折扣上限
	discount_money = models.FloatField(default=0.0) #折扣金额
	integral_price = models.FloatField(default=0.0) #积分价
	is_permanant_active = models.BooleanField(default=False) #是否永久有效

	class Meta(object):
		db_table = 'mallpromotion_integral_sale'
		verbose_name = '积分应用'
		verbose_name_plural = '积分应用'


class IntegralSaleRule(models.Model):
	"""
	积分应用规则
	"""
	owner = models.ForeignKey(User)
	integral_sale = models.ForeignKey(IntegralSale)
	member_grade_id = models.IntegerField(default=0) #会员等级
	discount = models.FloatField(default=0) #折扣上限
	discount_money = models.FloatField(default=0.0) #折扣金额

	class Meta(object):
		db_table = 'mallpromotion_integral_sale_rule'
		verbose_name = '积分应用规则'
		verbose_name_plural = '积分应用规则'


class PremiumSale(models.Model):
	"""
	买赠
	"""
	owner = models.ForeignKey(User)
	count = models.IntegerField(default=0) #购买基数
	is_enable_cycle_mode = models.BooleanField(default=False) #循环买赠

	class Meta(object):
		db_table = 'mallpromotion_premium_sale'
		verbose_name = '买赠'
		verbose_name_plural = '买赠'


class PremiumSaleProduct(models.Model):
	"""
	买赠的赠品
	"""
	owner = models.ForeignKey(User)
	premium_sale = models.ForeignKey(PremiumSale)
	product = models.ForeignKey(mall_models.Product)
	count = models.IntegerField(default=1, verbose_name='赠送数量')
	unit = models.CharField(max_length=50, verbose_name='赠品单位')

	class Meta(object):
		db_table = 'mallpromotion_premium_sale_product'
		verbose_name = '买赠赠品'
		verbose_name_plural = '买赠赠品'


#########################################################################
# 优惠券相关model
#########################################################################
class CouponRule(models.Model):
	"""
	优惠券规则
	"""
	owner = models.ForeignKey(User)
	name = models.CharField(max_length=20) #名称
	valid_days = models.IntegerField(default=0) #过期天数
	is_active = models.BooleanField(default=True) #是否可用
	created_at = models.DateTimeField(auto_now_add=True) #添加时间
	start_date = models.DateTimeField() #有效期开始时间
	end_date = models.DateTimeField() #有效期结束时间
	# v2
	valid_restrictions = models.IntegerField(default=-1) #订单满多少可以使用规则
	money = models.DecimalField() #金额
	count = models.IntegerField(default=0) #发放总数量
	remained_count = models.IntegerField(default=0) #剩余数量
	limit_counts = models.IntegerField(default=0) #每人限领
	limit_product = models.BooleanField(default=False) #限制指定商品
	limit_product_id = models.CharField(max_length=2048,default=0) #限制指定商品ID
	remark = models.TextField(default='') #备注
	get_person_count = models.IntegerField(default=0) #领取人数
	get_count = models.IntegerField(default=0) #领取次数
	use_count = models.IntegerField(default=0) #使用次数

	class Meta(object):
		db_table = 'market_tool_coupon_rule'


#优惠券状态
COUPON_STATUS_UNUSED = 0 #已领取
COUPON_STATUS_USED = 1 #已被使用
COUPON_STATUS_EXPIRED = 2 #已过期
COUPON_STATUS_DISCARD = 3 #作废 手机端用户不显示
COUPON_STATUS_UNGOT = 4 #未领取
COUPON_STATUS_Expired = 5 #已失效
COUPONSTATUS = {
	COUPON_STATUS_UNUSED: {
		"name": u'未使用'
	},
	COUPON_STATUS_USED: {
		"name": u'已使用'
	},
	COUPON_STATUS_EXPIRED: {
		"name": u'已过期'
	},
	COUPON_STATUS_DISCARD: {
		"name": u'作废'
	},
	COUPON_STATUS_UNGOT: {
		"name": u'未领取'
	},
	COUPON_STATUS_Expired: {
		"name": u'已失效'
	}
}
class Coupon(models.Model):
	"""
	优惠券
	"""
	owner = models.ForeignKey(User)
	coupon_rule = models.ForeignKey(CouponRule) #coupon rule
	member_id = models.IntegerField(default=0) #优惠券分配的member的id
	coupon_record_id = models.IntegerField(default=0) #优惠券记录的id
	status = models.IntegerField(default=COUPON_STATUS_UNUSED) #优惠券状态
	coupon_id = models.CharField(max_length=50) #优惠券号
	provided_time = models.DateTimeField(default=DEFAULT_DATETIME) #领取时间
	start_time = models.DateTimeField() #优惠券有效期开始时间
	expired_time = models.DateTimeField() #过期时间
	money = models.FloatField() #金额
	is_manual_generated = models.BooleanField(default=False) #是否手工生成
	created_at = models.DateTimeField(auto_now_add=True) #添加时间

	class Meta(object):
		db_table = 'market_tool_coupon'


FORBIDDEN_STATUS_NOT_START = 1
FORBIDDEN_STATUS_STARTED = 2
FORBIDDEN_STATUS_FINISHED = 3
FORBIDDENSTATUS2NAME = {
	FORBIDDEN_STATUS_NOT_START: u'未开始',
	FORBIDDEN_STATUS_STARTED: u'进行中',
	FORBIDDEN_STATUS_FINISHED: u'已结束'
}
class ForbiddenCouponProduct(models.Model):
	owner = models.ForeignKey(User)
	product = models.ForeignKey(mall_models.Product)
	status = models.IntegerField(default=FORBIDDEN_STATUS_NOT_START) #促销状态
	start_date = models.DateTimeField() #开始日期
	end_date = models.DateTimeField() #结束日期
	is_permanant_active = models.BooleanField(default=False) #永久有效
	created_at = models.DateTimeField(auto_now_add=True) #添加时间

	class Meta(object):
		db_table = 'mall_forbidden_coupon_product'


class RedEnvelopeRule(models.Model):
	"""
	红包规则
	"""
	owner = models.ForeignKey(User)
	name = models.CharField(max_length=128)
	coupon_rule_id = models.IntegerField(default=0)
	limit_time = models.BooleanField(default=False)
	start_time = models.DateTimeField(default=DEFAULT_DATETIME)
	end_time = models.DateTimeField(default=DEFAULT_DATETIME)
	limit_order_money = models.DecimalField(default=0.0)
	use_info = models.TextField()
	share_title = models.CharField(max_length=256)
	share_pic = models.CharField(max_length=256)
	is_delete = models.BooleanField(default=False)
	status = models.BooleanField(default=False) #状态默认关闭
	receive_method = models.BooleanField(default=False) #领取方式默认为下单领取
	order_index = models.IntegerField(default=0) #记录排序，置后为-1
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta(object):
		db_table = 'mall_red_envelope_rule'



class RedEnvelopeParticipences(models.Model):
	"""
	红包领用记录
	"""
	owner = models.ForeignKey(User)
	coupon = models.ForeignKey(Coupon)
	red_envelope_rule_id = models.IntegerField(default=0)
	red_envelope_relation_id = models.IntegerField(default=0)
	member = models.ForeignKey(Member)
	is_new = models.BooleanField(default=False)
	introduced_by = models.IntegerField(default=0)  #由谁引入
	introduce_new_member = models.IntegerField(default=0) #引入新关注
	introduce_used_number = models.IntegerField(default=0) #引入使用人数
	introduce_received_number = models.IntegerField(default=0) #引入领取人数
	introduce_sales_number = models.FloatField(default=0.0) #引入消费额
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta(object):
		db_table = 'mall_red_envelope_participences'


class RedEnvelopeToOrder(models.Model):
	"""
	红包关联订单记录表
	"""
	owner = models.ForeignKey(User)
	member_id = models.IntegerField(default=0)
	order_id = models.IntegerField(default=0) #订单领取记录订单id
	material_id = models.IntegerField(default=0) #图文领取记录图文id
	red_envelope_rule_id = models.IntegerField(default=0)
	count = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta(object):
		db_table = 'mall_red_envelope_to_order'
		verbose_name = '红包关联订单记录'
		verbose_name_plural = '红包关联订单记录'
class VirtualProduct(models.Model):
	"""
	福利卡券活动
	"""
	owner = models.ForeignKey(User)
	name = models.CharField(max_length=128) #活动名称
	product = models.ForeignKey(mall_models.Product)  #活动关联的商品
	is_finished = models.BooleanField(default=False)  #活动是否结束
	created_at = models.DateTimeField(auto_now_add=True)  #创建时间

	class Meta(object):
		db_table = 'mallpromotion_virtual_product'


CODE_STATUS_NOT_GET = 0 #未领取
CODE_STATUS_GET = 1 #已领取
CODE_STATUS_OVERDUE = 2 #已过期
CODE_STATUS_EXPIRED = 3 #已失效
CODE2TEXT = {
	CODE_STATUS_NOT_GET: u'未领取',
	CODE_STATUS_GET: u'已领取',  #已领取的就不判断是否过期，即使过期了数据库里依然是已领取状态，但是用户卡包里显示已过期
	CODE_STATUS_OVERDUE: u'已过期',  #已过期的一定是没有被领取过的
	CODE_STATUS_EXPIRED: u'已失效'
}

class VirtualProductHasCode(models.Model):
	"""
	福利卡券活动关联的卡券码
	"""
	owner = models.ForeignKey(User)
	virtual_product = models.ForeignKey(VirtualProduct)
	code = models.CharField(max_length=128) #卡号
	password = models.CharField(max_length=128) #密码
	start_time = models.DateTimeField() #有效期起始时间
	end_time = models.DateTimeField()#有效期结束时间
	status = models.IntegerField(default=CODE_STATUS_NOT_GET) #状态
	get_time = models.DateTimeField(null=True) #领取/发放时间
	member_id = models.CharField(max_length=20, default='') #会员id
	oid = models.CharField(max_length=20, default='') #订单id
	order_id = models.CharField(max_length=35, default='') #订单order_id
	created_at = models.DateTimeField(auto_now_add=True)  #创建时间

	class Meta(object):
		db_table = 'mallpromotion_virtual_product_has_code'
#coding: utf8
from db import models
from wapi.user.models import User

print 'load mall models'

class ProductCategory(models.Model):
	"""
	商品分类
	"""
	owner = models.ForeignKey(User, related_name='owned_product_categories')
	name = models.CharField(max_length=256)  # 分类名称
	pic_url = models.CharField(max_length=1024, default='')  # 分类图片
	product_count = models.IntegerField(default=0)  # 包含商品数量
	display_index = models.IntegerField(default=1)  # 显示的排序
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间

	class Meta(object):
		db_table = 'mall_product_category'



PRODUCT_STOCK_TYPE_LIMIT = 1
PRODUCT_STOCK_TYPE_UNLIMIT = 0
PRODUCT_SHELVE_TYPE_ON = 1
PRODUCT_SHELVE_TYPE_OFF = 0
PRODUCT_SHELVE_TYPE_RECYCLED = 2
PRODUCT_DEFAULT_TYPE = 'object'
PRODUCT_DELIVERY_PLAN_TYPE = 'delivery'
PRODUCT_TEST_TYPE = 'test'
PRODUCT_INTEGRAL_TYPE = 'integral'
POSTAGE_TYPE_UNIFIED = 'unified_postage_type'
POSTAGE_TYPE_CUSTOM = 'custom_postage_type'

PRODUCT_TYPE2TEXT = {
	PRODUCT_DEFAULT_TYPE: u'普通商品',
	PRODUCT_DELIVERY_PLAN_TYPE: u'套餐商品',
	PRODUCT_INTEGRAL_TYPE: u'积分商品'
}
MAX_INDEX = 2**16 - 1

class Product(models.Model):
	"""
	商品

	表名：mall_product
	"""
	owner = models.ForeignKey(User, related_name='user-product')
	name = models.CharField(max_length=256)  # 商品名称
	physical_unit = models.CharField(default='', max_length=256)  # 计量单位
	price = models.FloatField(default=0.0)  # 商品价格
	introduction = models.CharField(max_length=256)  # 商品简介
	weight = models.FloatField(default=0.0)  # 重量
	thumbnails_url = models.CharField(max_length=1024)  # 商品缩略图
	pic_url = models.CharField(max_length=1024)  # 商品图
	detail = models.TextField(default='')  # 商品详情
	remark = models.TextField(default='')  # 备注
	display_index = models.IntegerField(default=0, blank=True)  # 显示的排序
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间
	shelve_type = models.IntegerField(default=PRODUCT_SHELVE_TYPE_OFF)  # 0:下架（待售） 1:上架（在售） 2:回收站
	shelve_start_time = models.CharField(max_length=50, null=True)  # 定时上架:上架时间
	shelve_end_time = models.CharField(max_length=50, null=True)  # 定时上架:下架时间
	stock_type = models.IntegerField(
		default=PRODUCT_STOCK_TYPE_UNLIMIT)  # 0:无限 1:有限
	stocks = models.IntegerField(default=-1)  # 起购数量
	is_deleted = models.BooleanField(default=False)  # 是否删除
	is_support_make_thanks_card = models.BooleanField(
		default=False)  # 是否支持制作感恩贺卡
	type = models.CharField(
		max_length=50,
		default=PRODUCT_DEFAULT_TYPE)  # 产品的类型
	update_time = models.DateTimeField(auto_now=True)  # 商品信息更新时间 2014-11-11
	postage_id = models.IntegerField(default=-1)  # 运费id ，-1为使用统一运费
	is_use_online_pay_interface = models.BooleanField(default=True)  # 在线支付方式
	is_use_cod_pay_interface = models.BooleanField(default=False)  # 货到付款支付方式
	# v2
	# product_mode = models.ForeignKey(ProductModel, blank=True, null=True)
	promotion_title = models.CharField(max_length=256, default='')  # 促销标题
	user_code = models.CharField(max_length=256, default='')  # 编码
	bar_code = models.CharField(max_length=256, default='')  # 条码
	unified_postage_money = models.FloatField(default=0.0)  # 统一运费金额
	postage_type = models.CharField(max_length=125, default=POSTAGE_TYPE_UNIFIED)  # 运费类型
	weshop_sync = models.IntegerField(default=0)  # 0不同步 1普通同步 2加价同步
	weshop_status = models.IntegerField(default=0)  # 0待售 1上架 2回收站
	is_member_product = models.BooleanField(default=False)  # 是否参加会员折扣
	supplier = models.IntegerField(default=0) # 供货商
	purchase_price = models.FloatField(default=0.0) # 进货价格

	class Meta(object):
		db_table = 'mall_product'

	def fill_model(self):
		pass

	@staticmethod
	def fill_display_price(products):
		"""根据商品规格，获取商品价格
		"""
		# 获取所有models
		product2models = {}
		product_ids = [product.id for product in products]
		for model in ProductModel.select().dj_where(product__in=product_ids):
			if model.is_deleted:
				# model被删除，跳过
				continue

			product_id = model.product_id
			if product_id in product2models:
				models = product2models[product_id]
			else:
				models = {
					'standard_model': None,
					'custom_models': [],
					'is_use_custom_model': False}
				product2models[product_id] = models

			if model.name == 'standard':
				models['standard_model'] = model
			else:
				models['is_use_custom_model'] = True
				models['custom_models'].append(model)

		# 为每个product确定显示价格
		for product in products:
			product_id = product.id
			if product_id in product2models:
				models = product2models[product.id]
				if models['is_use_custom_model']:
					custom_models = models['custom_models']
					if len(custom_models) == 1:
						product.display_price = custom_models[0].price
					else:
						prices = sorted(
							[model.price
							 for model in custom_models])
						# 列表页部分显示商品的最小价格
						# add by liupeiyu at 19.0
						# product.display_price = '%s-%s' % (prices[0], prices[-1])
						product.display_price = prices[0]
				else:
					product.display_price = models['standard_model'].price
			else:
				product.display_price = product.price


class CategoryHasProduct(models.Model):
	"""
	<category, product>关系
	"""
	product = models.ForeignKey(Product)
	category = models.ForeignKey(ProductCategory)
	display_index = models.IntegerField(default=0, null=True)  # 分组商品排序
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta(object):
		db_table = 'mall_category_has_product'


class ProductSwipeImage(models.Model):
	"""
	商品轮播图
	"""
	product = models.ForeignKey(Product)
	url = models.CharField(max_length=256, default='')
	link_url = models.CharField(max_length=256, default='')
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间
	# v2
	width = models.IntegerField()  # 图片宽度
	height = models.IntegerField()  # 图片高度

	class Meta(object):
		db_table = 'mall_product_swipe_image'





#########################################################################
# 商品规格相关Model
#########################################################################
PRODUCT_MODEL_PROPERTY_TYPE_TEXT = 0
PRODUCT_MODEL_PROPERTY_TYPE_IMAGE = 1
class ProductModelProperty(models.Model):
	"""
	商品规格属性
	"""
	owner = models.ForeignKey(User)
	name = models.CharField(max_length=256)  # 商品规格属性名
	type = models.IntegerField(default=PRODUCT_MODEL_PROPERTY_TYPE_TEXT)  # 属性类型
	is_deleted = models.BooleanField(default=False)  # 是否删除
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间

	class Meta(object):
		db_table = 'mall_product_model_property'

	@property
	def values(self):
		return list(
			ProductModelPropertyValue.objects.filter(
				property=self,
				is_deleted=False))

	@property
	def is_image_property(self):
		return self.type == PRODUCT_MODEL_PROPERTY_TYPE_IMAGE


class ProductModelPropertyValue(models.Model):
	"""
	商品规格属性值
	"""
	property = models.ForeignKey(ProductModelProperty, related_name='model_property_values')
	name = models.CharField(max_length=256)  # 商品名称
	pic_url = models.CharField(max_length=1024)  # 商品图
	is_deleted = models.BooleanField(default=False)  # 是否已删除
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间

	class Meta(object):
		db_table = 'mall_product_model_property_value'


class ProductModel(models.Model):
	"""
	商品规格
	"""
	owner = models.ForeignKey(User)
	product = models.ForeignKey(Product)
	name = models.CharField(max_length=255)  # 商品规格名
	is_standard = models.BooleanField(default=True)  # 是否是标准规格
	price = models.FloatField(default=0.0)  # 商品价格
	market_price = models.FloatField(default=0.0)  # 商品市场价格
	weight = models.FloatField(default=0.0)  # 重量
	stock_type = models.IntegerField(default=PRODUCT_STOCK_TYPE_UNLIMIT)  # 0:无限 1:有限
	stocks = models.IntegerField(default=-1)  # 有限：数量
	is_deleted = models.BooleanField(default=False)  # 是否已删除
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间
	# v2
	user_code = models.CharField(max_length=256, default='')  # 编码

	class Meta(object):
		db_table = 'mall_product_model'

	def __getitem__(self, name):
		return getattr(self, name, None)


class ProductModelHasPropertyValue(models.Model):
	"""
	<商品规格，商品规格属性值>关系
	"""
	model = models.ForeignKey(ProductModel)
	property_id = models.IntegerField(default=0)
	property_value_id = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间

	class Meta(object):
		db_table = 'mall_product_model_has_property'


class ProductProperty(models.Model):
	"""
	商品属性
	"""
	owner = models.ForeignKey(User)
	product = models.ForeignKey(Product)
	name = models.CharField(max_length=256)  # 商品属性名
	value = models.CharField(max_length=256)  # 商品属性值
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间

	class Meta(object):
		db_table = 'mall_product_property'
		verbose_name = '商品属性'
		verbose_name_plural = '商品属性'


class ProductPropertyTemplate(models.Model):
	"""
	商品属性模板
	"""
	owner = models.ForeignKey(User)
	name = models.CharField(max_length=256)  # 商品属性名
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间

	class Meta(object):
		db_table = 'mall_product_property_template'


class TemplateProperty(models.Model):
	"""
	模板中的属性
	"""
	owner = models.ForeignKey(User)
	template = models.ForeignKey(ProductPropertyTemplate)
	name = models.CharField(max_length=256)  # 商品属性名
	value = models.CharField(max_length=256)  # 商品属性值
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间

	class Meta(object):
		db_table = 'mall_product_template_property'





#########################################################################
# 微众商城相关Model
#########################################################################
class WeizoomMall(models.Model):
	"""
	微众商城用户
	"""
	webapp_id = models.CharField(max_length=20)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta(object):
		db_table = 'weizoom_mall'

	@staticmethod
	def is_weizoom_mall(webapp_id):
		if WeizoomMall.objects.filter(webapp_id=webapp_id).count() > 0:
			return WeizoomMall.objects.filter(webapp_id=webapp_id)[0].is_active
		else:
			return False
		

class WeizoomMallHasOtherMallProduct(models.Model):
	"""
	<微众商城, 商品>关系
	"""
	weizoom_mall = models.ForeignKey(WeizoomMall)
	webapp_id = models.CharField(max_length=20)
	is_checked = models.BooleanField(default=False,)  # 是否审核通过
	product_id = models.IntegerField(default=-1)  # 商品id
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间

	class Meta(object):
		db_table = 'weizoom_mall_has_other_mall_product'
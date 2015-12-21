#coding: utf8
import copy
from datetime import datetime
import json

from core.db import models
from db.account.models import User, UserProfile
from core.watchdog.utils import watchdog_fatal
import settings
from utils import area_util

DEFAULT_DATETIME = datetime.strptime('2000-01-01', '%Y-%m-%d')


#########################################################################
# 商城相关Model
#########################################################################

MALL_CONFIG_PRODUCT_COUNT_NO_LIMIT = 999999999
MALL_CONFIG_PRODUCT_NORMAL = 7
class MallConfig(models.Model):
	"""
	商城配置
	"""
	owner = models.ForeignKey(User, related_name='mall_config')
	max_product_count = models.IntegerField(default=MALL_CONFIG_PRODUCT_NORMAL)  # 最大商品数量
	is_enable_bill = models.BooleanField(default=False)  # 是否启用发票功能
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间
	# new add at 13  by bert
	order_expired_day = models.IntegerField(default=0)  # 未付款订单过期时间(单位是小时)

	class Meta(object):
		db_table = 'mall_config'

	@staticmethod
	def set_max_product_count_for(user, max_product_count):
		if user is None or max_product_count < 0:
			return

		MallConfig.update(max_product_count=max_product_count).dj_where(owner=user.id)

	@staticmethod
	def get_order_expired_day(user):
		if user is None:
			return -1

		if MallConfig.select().dj_where(owner=user.id).count() > 0:
			return MallConfig.select().dj_where(owner=user)[0].order_expired_day








#########################################################################
# 地域相关Model
#########################################################################
class City(models.Model):
	name = models.CharField(max_length=50)
	zip_code = models.CharField(max_length=50)
	province_id = models.IntegerField(db_index=True)

	class Meta(object):
		db_table = 'city'
		verbose_name = '城市列表'
		verbose_name_plural = '城市列表'

class Province(models.Model):
	name = models.CharField(max_length=50)

	class Meta(object):
		db_table = 'province'
		verbose_name = '省份列表'
		verbose_name_plural = '省份列表'


class District(models.Model):
	name = models.CharField(max_length=50)
	city_id = models.IntegerField(db_index=True)

	class Meta(object):
		db_table = 'district'
		verbose_name = '区县列表'
		verbose_name_plural = '区县列表'









#########################################################################
# 运费相关Model
#########################################################################
class PostageConfig(models.Model):
	"""
	运费配置
	"""
	owner = models.ForeignKey(User)
	name = models.CharField(max_length=256)  # 名称
	first_weight = models.FloatField(default=0.0)  # 首重
	first_weight_price = models.FloatField(default=0.0)  # 首重价格
	is_enable_added_weight = models.BooleanField(default=True)  # 是否启用续重机制
	added_weight = models.CharField(max_length=256, default='0')  # 续重
	added_weight_price = models.CharField(max_length=256, default='0')  # 续重价格
	display_index = models.IntegerField(default=1)  # 显示的排序
	is_used = models.BooleanField(default=True)  # 是否启用
	is_system_level_config = models.BooleanField(default=False)  # 是否是系统创建的不可修改的配置
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间
	update_time = models.DateTimeField(auto_now=True)  # 更新时间
	is_enable_special_config = models.BooleanField(default=True)  # 是否启用续重机制
	is_enable_free_config = models.BooleanField(default=True)  # 是否启用包邮机制
	is_deleted = models.BooleanField(default=False) #是否删除

	class Meta(object):
		db_table = 'mall_postage_config'

	def get_special_configs(self):
		return SpecialPostageConfig.select().dj_where(postage_config=self)

	def get_free_configs(self):
		return FreePostageConfig.select().dj_where(postage_config=self)


class SpecialPostageConfig(models.Model):
	"""
	特殊地区运费配置
	"""
	owner = models.ForeignKey(User)
	postage_config = models.ForeignKey(PostageConfig)
	first_weight_price = models.FloatField(default=0.0)  # 首重价格
	added_weight_price = models.CharField(max_length=256)  # 续重价格
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间
	# v2
	destination = models.CharField(max_length=512)  # 目的省份的id集合
	first_weight = models.FloatField(default=0.0)  # 首重
	added_weight = models.FloatField(default=0.0)  # 续重

	class Meta(object):
		db_table = 'mall_postage_config_special'

	def get_special_has_provinces(self):
		return PostageConfigSpecialHasProvince.select().dj_where(postage_config_special=self)

	def get_provinces_array(self):
		provinces = []
		for special_has_provinces in self.get_special_has_provinces():
			provinces.append({
				'id': special_has_provinces.province.id, 
				'name': special_has_provinces.province.name
			})
		return provinces

	@property
	def destination_str(self):
		province_ids = self.destination.split(',')
		provinces = area_util.get_provinces_by_ids(province_ids)
		self._dest_str = u', '.join(provinces)
		return self._dest_str


class FreePostageConfig(models.Model):
	"""
	特殊地区包邮配置
	"""
	owner = models.ForeignKey(User)
	postage_config = models.ForeignKey(PostageConfig)
	destination = models.CharField(max_length=512)  # 目的省份的id集合
	condition = models.CharField(max_length=25, default='count')  # 免邮条件类型, 共有'count', 'money'两种
	condition_value = models.CharField(max_length=25)  # 免邮条件值
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间

	class Meta(object):
		db_table = 'mall_free_postage_config'

	@property
	def destination_str(self):
		province_ids = self.destination.split(',')
		provinces = area_util.get_provinces_by_ids(province_ids)
		self._dest_str = u', '.join(provinces)
		return self._dest_str


# class PostageConfigSpecialHasProvince(models.Model):
# 	owner = models.ForeignKey(User)
# 	postage_config = models.ForeignKey(PostageConfig)
# 	postage_config_special = models.ForeignKey(SpecialPostageConfig)
# 	province = models.ForeignKey(Province)
# 	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间

# 	class Meta(object):
# 		db_table = 'mall_postage_config_special_has_province'
# 		verbose_name = '运费特殊配置对应省份'
# 		verbose_name_plural = '运费特殊配置对应省份'










#########################################################################
# 商品相关Model
#########################################################################
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
	display_index = models.IntegerField(default=0)  # 显示的排序
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
	type = models.CharField(max_length=50,default=PRODUCT_DEFAULT_TYPE)  # 产品的类型
	update_time = models.DateTimeField(auto_now=True)  # 商品信息更新时间 2014-11-11
	postage_id = models.IntegerField(default=-1)  # 运费id ，-1为使用统一运费
	is_use_online_pay_interface = models.BooleanField(default=True)  # 在线支付方式
	is_use_cod_pay_interface = models.BooleanField(default=False)  # 货到付款支付方式
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

	@property
	def is_sellout(self):
		return self.total_stocks <= 0

	@is_sellout.setter
	def is_sellout(self, value):
		pass

	@property
	def total_stocks(self):
		if not hasattr(self, '_total_stocks'):
			self._total_stocks = 0
			if self.is_use_custom_model:
				models = self.custom_models
			else:
				models = self.models

			if len(models) == 0:
				self._total_stocks = 0
				return self._total_stocks
			is_dict = (type(models[0]) == dict)

			for model in models:
				stock_type = model['stock_type'] if is_dict else model.stock_type
				stocks = model['stocks'] if is_dict else model.stocks
				if stock_type == PRODUCT_STOCK_TYPE_UNLIMIT:
					self._total_stocks = u'无限'
					return self._total_stocks
				else:
					self._total_stocks += stocks
		return self._total_stocks

	@total_stocks.setter
	def total_stocks(self, value):
		self._total_stocks = value

	@property
	def is_use_custom_model(self):
		if not hasattr(self, '_is_use_custom_model'):
			self._is_use_custom_model = (
				ProductModel.select().dj_where(
					product=self,
					is_standard=False,
					is_deleted=False).count() > 0)  # 是否使用定制规格
		return self._is_use_custom_model

	@is_use_custom_model.setter
	def is_use_custom_model(self, value):
		self._is_use_custom_model = value

	# 如果规格有图片就显示，如果没有，使用缩略图
	@property
	def order_thumbnails_url(self):
		'''
		if hasattr(self, 'custom_model_properties') and self.custom_model_properties:
			for model in self.custom_model_properties:
				if model['property_pic_url']:
					return model['property_pic_url']
		'''
		if not hasattr(self, '_order_thumbnails_url'):
			self._order_thumbnails_url = self.thumbnails_url
		return self._order_thumbnails_url

	@order_thumbnails_url.setter
	def order_thumbnails_url(self, url):
		'''
		if hasattr(self, 'custom_model_properties') and self.custom_model_properties:
			for model in self.custom_model_properties:
				if model['property_pic_url']:
					return model['property_pic_url']
		'''
		self._order_thumbnails_url = url

	def fill_specific_model(self, model_name, models=None):
		if not models:
			models = self.models

		candidate_models = filter(lambda m: m['name'] == model_name, models)
		if len(candidate_models) > 0:
			model = candidate_models[0]
			product = self
			product.price = model['price']
			product.weight = model['weight']
			product.stock_type = model['stock_type']
			if not hasattr(product, 'min_limit'):
				product.min_limit = product.stocks
			product.stocks = model['stocks']
			product.model_name = model_name
			product.model = model
			product.is_model_deleted = False
			product.market_price = model.get('market_price', 0.0)

			if model_name == 'standard':
				product.custom_model_properties = None
			else:
				product.custom_model_properties = [{'property_value': property_value['name']} for property_value in model['property_values']]

	def fill_standard_model(self):
		"""
		填充标准商品规格信息
		"""
		try:
			product_model = ProductModel.get(product=self.id, is_standard=True)

			self.price = product_model.price
			self.weight = product_model.weight
			self.stock_type = product_model.stock_type
			self.min_limit = self.stocks
			self.stocks = product_model.stocks
			self.market_price = product_model.market_price
			return product_model
		except:
			if settings.DEBUG:
				raise
			else:
				fatal_msg = u"商品填充标准规格信息错误，商品id:{}, cause:\n{}".format(self.id, unicode_full_stack())
				watchdog_fatal(fatal_msg)

	def fill_model(self, show_delete=False):
		"""
		填充所有商品规格信息
		"""
		standard_model = self.fill_standard_model()

		if self.is_use_custom_model:
			self.custom_models = ProductModel.select().dj_where(product=self.id, name__not='standard', is_deleted=show_delete)
		else:
			self.custom_models = []

		self.models = []
		self.models.append({
			"id": standard_model.id,
			"name": "standard",
			"original_price": self.price,
			"price": self.price,
			"weight": self.weight,
			"stock_type": self.stock_type,
			"stocks": self.stocks,
			"market_price": self.market_price,
			"user_code": self.user_code
		})

		self.custom_properties = []
		self.product_model_properties = []
		recorded_model_property = set()  # 保存已记录的model property
		if len(self.custom_models) > 0:
			# 获取系统所有property
			id2property = dict([(property.id, property) for property in ProductModelProperty.select().dj_where(owner=self.owner_id, is_deleted=False)])
			properties = id2property.values()
			properties.sort(lambda x, y: cmp(x.id, y.id))
			for property in properties:
				self.custom_properties.append({
					"id": property.id,
					"name": property.name
				})
			self.custom_properties_json_str = json.dumps(self.custom_properties)

			property_ids = id2property.keys()
			id2value = dict([(value.id, value) for value in ProductModelPropertyValue.select().dj_where(property_id__in=property_ids, is_deleted=False)])

			# 获取系统所有<property, [values]>
			id2property = {}
			for property in properties:
				id2property[
					property.id] = {
					"id": property.id,
					"name": property.name,
					"values": []}
			stock_custom_model_names = []  # 无限库存或库存不为>0的custom_model_name集合
			property_value_ids = []
			for custom_model in self.custom_models:
				if custom_model.stock_type == 0 or custom_model.stocks > 0:
					stock_custom_model_names.append(str(custom_model.name))
				for model_property_info in custom_model.name.split('_'):
					property_id, property_value_id = model_property_info.split(':')
					property_value_ids.append(int(property_value_id))
			self.stock_custom_model_names = stock_custom_model_names

			# 解决规格顺序错乱的BUG
			values = id2value.values()
			if values:
				values.sort(lambda x, y: cmp(x.id, y.id))

			for value in values:
				# 增加该规格值是否属于该产品
				is_belong_product = (value.id in property_value_ids)
				id2property[value.property_id]['values'].append({
					"id": value.id,
					"name": value.name,
					"image": value.pic_url,
					"is_belong_product": is_belong_product
				})
			self.model_properties = id2property.values()
			self.model_properties.sort(lambda x, y: cmp(x['id'], y['id']))

			# 获取商品关联的所有的model和property
			for custom_model in self.custom_models:
				if custom_model.name == 'standard':
					continue

				model_dict = {
					"id": custom_model.id,
					"name": custom_model.name,
					"original_price": custom_model.price,
					"price": custom_model.price,
					"weight": custom_model.weight,
					"stock_type": custom_model.stock_type,
					"stocks": custom_model.stocks,
					"user_code": custom_model.user_code,
					"market_price": custom_model.market_price
				}

				model_dict['property_values'] = []
				try:
					for model_property_info in custom_model.name.split('_'):
						property_id, property_value_id = model_property_info.split(':')
						if not id2value.has_key(int(property_value_id)):
							continue
						model_dict['property_values'].append({
							"propertyId": property_id,
							"propertyName": id2property[int(property_id)]['name'],
							"id": property_value_id,
							"name": id2value[int(property_value_id)].name
						})

						# 记录商品的model property
						if not property_id in recorded_model_property:
							model_property = id2property[int(property_id)]
							self.product_model_properties.append(model_property)
							recorded_model_property.add(property_id)

					self.models.append(model_dict)
				except:
					fatal_msg = u"商品填充所有商品规格信息错误，商品id:{}, 错误的mall_product_model.id:{}, cause:\n{}".format(
						self.id,
						custom_model.id,
						unicode_full_stack())
					watchdog_fatal(fatal_msg)

		self.models_json_str = json.dumps(self.models)
		self.product_model_properties_json_str = json.dumps(self.product_model_properties)

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
					'is_use_custom_model': False
				}
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

	@staticmethod
	def fill_model_detail(webapp_owner_id, products, product_ids, id2property={}, id2propertyvalue={}, is_enable_model_property_info=False):
		_id2property = {}
		_id2propertyvalue = {}
		if is_enable_model_property_info:
			for id, property in id2property.items():
				_id2property[id] = {
					"id": property.id,
					"name": property.name,
					"values": []
				}

			for id, value in id2propertyvalue.items():
				_property_id, _value_id = id.split(':')
				_property = _id2property[_property_id]
				data = {
					'propertyId': _property['id'],
					'propertyName': _property['name'],
					"id": value.id,
					"name": value.name,
					"image": value.pic_url,
					"is_belong_product": False
				}
				_id2propertyvalue[id] = data
				_property['values'].append(data)

		# 获取所有models
		product2models = {}
		for model in ProductModel.select().dj_where(product_id__in=product_ids):
			if model.is_deleted:
				# model被删除，跳过
				continue

			model_dict = {
				"id": model.id,
				"name": model.name,
				"price": model.price,
				"original_price": model.price,
				"weight": model.weight,
				"stock_type": model.stock_type,
				"stocks": model.stocks if model.stock_type == PRODUCT_STOCK_TYPE_LIMIT else u'无限',
				"user_code": model.user_code,
				"market_price": model.market_price
			}

			'''
			获取model关联的property信息
				model.property_values = [{
					'propertyId': 1,
					'propertyName': '颜色',
					'id': 1,
					'value': '红'
				}, {
					'propertyId': 2,
					'propertyName': '尺寸',
					'id': 3,
					'value': 'S'
				}]

				model.property2value = {
					'颜色': '红',
					'尺寸': 'S'
				}
			'''
			if is_enable_model_property_info and model.name != 'standard':
				ids = model.name.split('_')
				property_values = []
				property2value = {}
				for id in ids:
					# id的格式为${property_id}:${value_id}
					_property_id, _value_id = id.split(':')
					_property = _id2property[_property_id]
					_value = _id2propertyvalue[id]
					property2value[_property['name']] = {
						'id': _value['id'],
						'name': _value['name']
					}
					property_values.append({
						'propertyId': _property['id'],
						'propertyName': _property['name'],
						'id': _value['id'],
						'name': _value['name']
					})
					_value['is_belong_product'] = True
				model_dict['property_values'] = property_values
				model_dict['property2value'] = property2value

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
				models['standard_model'] = model_dict
			else:
				models['is_use_custom_model'] = True
				models['custom_models'].append(model_dict)

		# 为每个product确定显示信息
		for product in products:
			product.sales = -1  # 实现sales逻辑
			product.system_model_properties = _id2property.values()
			product_id = product.id
			if product_id in product2models:
				models = product2models[product.id]
				product.models = [models['standard_model']]
				if models['is_use_custom_model']:
					product._is_use_custom_model = True
					product.custom_models = models['custom_models']
					product.standard_model = models['standard_model']
					custom_models = models['custom_models']
					product.models.extend(custom_models)
					if len(custom_models) == 1:
						target_model = custom_models[0]
						display_price_range = target_model['price']
					else:
						# 列表页部分显示商品的最小价格那个model的信息
						custom_models.sort(lambda x, y: cmp(x['price'], y['price']))
						target_model = custom_models[0]
						low_price = target_model['price']
						high_price = custom_models[-1]['price']
						if low_price == high_price:
							display_price_range = low_price
						else:
							display_price_range = '%s ~ %s' % (low_price, high_price)
				else:
					product._is_use_custom_model = False
					target_model = models['standard_model']
					product.standard_model = target_model
					display_price_range = target_model['price']

				product.current_used_model = target_model
				product.display_price = target_model['price']
				product.display_price_range = display_price_range
				product.user_code = target_model['user_code']
				product.stock_type = target_model['stock_type']
				product.min_limit = product.stocks
				product.stocks = u'无限' if target_model[
					'stock_type'] == PRODUCT_STOCK_TYPE_UNLIMIT else target_model['stocks']
			else:
				# 所有规格都已经被删除
				product._is_use_custom_model = False
				product.current_used_model = {}
				product.display_price = product.price
				product.display_price_range = product.price
				product.user_code = product.user_code
				product.stock_type = PRODUCT_STOCK_TYPE_LIMIT
				product.stocks = 0
				product.min_limit = 0
				product.standard_model = {}
				product.models = []

	@staticmethod
	def fill_image_detail(webapp_owner_id, products, product_ids):
		for product in products:
			product.swipe_images = [{
				'id': img.id, 
				'url': '%s%s' % (settings.IMAGE_HOST, img.url),
				'linkUrl': img.link_url, 
				'width': img.width, 
				'height': img.height
			} for img in ProductSwipeImage.select().dj_where(product_id=product.id)]

	@staticmethod
	def fill_property_detail(webapp_owner_id, products, product_ids):
		for product in products:
			product.properties = [{
				"id": property.id, 
				"name": property.name,
				"value": property.value
			} for property in ProductProperty.select().dj_where(product_id=product.id)]

	@staticmethod
	def fill_category_detail(webapp_owner_id, products, product_ids, only_selected_category=False):
		categories = list(ProductCategory.select().dj_where(owner=webapp_owner_id).order_by('id'))

		# 获取product关联的category集合
		id2product = dict([(product.id, product) for product in products])
		for product in products:
			product.categories = []
			product.id2category = {}
			id2product[product.id] = product
			if not only_selected_category:
				for category in categories:
					category_data = {
						'id': category.id,
						'name': category.name,
						'is_selected': False
					}
					product.categories.append(category_data)
					product.id2category[category.id] = category_data

		category_ids = [category.id for category in categories]
		id2category = dict([(category.id, category) for category in categories])
		for relation in CategoryHasProduct.select().dj_where(product_id__in=product_ids).order_by('id'):
			category_id = relation.category_id
			product_id = relation.product_id
			if not category_id in id2category:
				# 微众商城分类，在商户中没有
				continue
			category = id2category[category_id]
			if not only_selected_category:
				id2product[product_id].id2category[
					category.id]['is_selected'] = True
			else:
				id2product[product_id].categories.append({
					'id': category.id,
					'name': category.name,
					'is_selected': True
				})

	@staticmethod
	def fill_promotion_detail(webapp_owner, products, product_ids):
		pass
		'''
		from mall.promotion import models as promotion_models
		today = datetime.today()
		id2product = dict([(product.id, product) for product in products])

		type2promotions = {}
		id2promotion = {}
		product_promotion_relations = list(
			promotion_models.Promotion.objects.filter(
				product_id__in=product_ids))
		promotion_ids = [relation.promotion_id
						 for relation in product_promotion_relations]
		promotions = list(
			promotion_models.Promotion.objects.filter(
				product_id__in=product_ids))
		for promotion in promotions:
			type2promotions.setdefault(promotion.type, []).append(promotion)
			id2promotion[promotion.id] = promotion

		for relation in product_promotion_relations:
			product = id2product[relation.product_id]
			promotion = id2promotion[relation.promotion_id]
			product.promotion = {
				'id': promotion.id,
				'type': promotion.type_name,
				'name': promotion.name,
				'status_value': promotion.status,
				'status': promotion.status_name,
				'start_date': promotion.start_date.strftime("%Y-%m-%d %H:%M"),
				'end_date': promotion.end_date.strftime('%Y-%m-%d %H:%M')
			}

		for type, promotions in type2promotions.items():
			if type == promotion_models.PROMOTION_TYPE_FLASH_SALE:
				model2product = dict(
					[(product.current_used_model['id'], product) for product in products])
				product_model_ids = [product.current_used_model['id']
									 for product in products]
				model_promotion_details = promotion_models.ProductModelFlashSaleDetail.objects.filter(
					owner=webapp_owner,
					product_model_id__in=product_model_ids)
				for model_promotion_detail in model_promotion_details:
					model2product[promotion_detail.product_model_id].promotion[
						'price'] = model_promotion_detail.promotion_price
			else:
				pass
		'''

	@staticmethod
	def fill_sales_detail(webapp_owner_id, products, product_ids):
		id2product = dict([(product.id, product) for product in products])
		for product in products:
			product.sales = 0

		for sales in ProductSales.select().dj_where(product_id__in=product_ids):
			product_id = sales.product_id
			if id2product.has_key(product_id):
				id2product[product_id].sales = sales.sales

	@staticmethod
	def fill_details(webapp_owner_id, products, options):
		id2property = None
		id2propertyvalue = None
		is_enable_model_property_info = options.get('with_model_property_info',False)
		if is_enable_model_property_info:
			# 获取model property，为后续使用做准备
			properties = list(ProductModelProperty.select().dj_where(owner_id=webapp_owner_id))
			property_ids = [property.id for property in properties]
			id2property = dict([(str(property.id), property)
							   for property in properties])
			id2propertyvalue = {}
			for value in ProductModelPropertyValue.select().dj_where(property__in=property_ids):
				id = '%d:%d' % (value.property_id, value.id)
				id2propertyvalue[id] = value

		product_ids = [product.id for product in products]

		for product in products:
			product.detail_link = '/mall2/product/?id=%d&source=onshelf' % product.id

		if options.get('with_price', False):
			Product.fill_display_price(products)

		if options.get('with_product_model', False):
			Product.fill_model_detail(
				webapp_owner_id,
				products,
				product_ids,
				id2property,
				id2propertyvalue,
				is_enable_model_property_info)

		if options.get('with_product_promotion', False):
			Product.fill_promotion_detail(webapp_owner_id, products, product_ids)

		if options.get('with_image', False):
			Product.fill_image_detail(webapp_owner_id, products, product_ids)

		if options.get('with_property', False):
			Product.fill_property_detail(webapp_owner_id, products, product_ids)

		if options.get('with_selected_category', False):
			Product.fill_category_detail(
				webapp_owner_id,
				products,
				product_ids,
				True)

		if options.get('with_all_category', False):
			Product.fill_category_detail(
				webapp_owner_id,
				products,
				product_ids,
				False)

		if options.get('with_sales', False):
			Product.fill_sales_detail(webapp_owner_id, products, product_ids)

	def format_to_dict(self):
		return {
			'id': self.id,
			'is_deleted': self.is_deleted,
			'name': self.name,
			'model_name': getattr(self, 'model_name', 'standard'),
			'weshop_sync': self.weshop_sync,
			'shelve_type': self.shelve_type,
			'shelve_start_time': self.shelve_start_time,
			'shelve_end_time': self.shelve_end_time,
			'detail': self.detail,
			'thumbnails_url': self.thumbnails_url if 'http:' in self.thumbnails_url else '%s%s' % (settings.IMAGE_HOST, self.thumbnails_url),
			'order_thumbnails_url': self.order_thumbnails_url if 'http:' in self.order_thumbnails_url else '%s%s' % (settings.IMAGE_HOST, self.order_thumbnails_url),
			'pic_url': self.pic_url if 'http:' in self.pic_url else '%s%s' % (settings.IMAGE_HOST, self.pic_url),
			'detail_link': '/mall2/product/?id=%d&source=onshelf' % self.id,
			'categories': getattr(self, 'categories', []),
			'properties': getattr(self, 'properties', []),
			'product_model_properties': getattr(self, 'product_model_properties', None),
			'display_price': self.display_price,
			'display_price_range': self.display_price_range,
			'user_code': self.user_code,
			'bar_code': self.bar_code,
			'min_limit': self.min_limit,
			'stocks': self.stocks if self.stock_type else '无限',
			'sales': getattr(self, 'sales', 0),
			'is_use_custom_model': self.is_use_custom_model,
			'models': self.models,
			'custom_models': self.models[1:],
			'total_stocks': self.total_stocks,
			'is_sellout': self.is_sellout,
			'standard_model': self.standard_model,
			'current_used_model': self.current_used_model,
			'created_at': self.created_at if type(self.created_at) == str else datetime.strftime(self.created_at, '%Y-%m-%d %H:%M'),
			'display_index': self.display_index,
			'is_member_product': self.is_member_product,
			'purchase_price': self.purchase_price,
			'swipe_images': getattr(self, 'swipe_images', []),
			'promotion': getattr(self, 'promotion', None),
			'promotion_title': getattr(self, 'promotion_title', ''),
			'product_review': getattr(self, 'product_review', None),
			'price_info': getattr(self, 'price_info', None)
		}


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


class ProductSales(models.Model):
	"""
	商品销量
	"""
	product = models.ForeignKey(Product)
	sales = models.IntegerField(default=0) #销量

	class Meta(object):
		db_table = 'mall_product_sales'


class MemberProductWishlist(models.Model):
	owner = models.ForeignKey(User)
	member_id = models.IntegerField(default=0) #会员ID
	product_id = models.IntegerField(default=0) #商品ID
	is_collect = models.BooleanField(default=False) #商品是否被收藏
	add_time = models.DateTimeField(auto_now_add=True) #商品收藏的时间
	delete_time = models.DateTimeField(default=DEFAULT_DATETIME) #商品取消收藏的时间
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间

	class Meta(object):
		db_table = 'mall_member_product_wishlist'


PAY_INTERFACE_ALIPAY = 0
PAY_INTERFACE_TENPAY = 1
PAY_INTERFACE_WEIXIN_PAY = 2
PAY_INTERFACE_COD = 9
PAY_INTERFACE_PREFERENCE = 10
PAY_INTERFACE_WEIZOOM_COIN = 3

PAYTYPE2LOGO = {
	PAY_INTERFACE_ALIPAY: '/standard_static/img/mockapi/alipay.png',
	PAY_INTERFACE_TENPAY: '/standard_static/img/mockapi/tenpay.png',
	PAY_INTERFACE_WEIXIN_PAY: '/standard_static/img/mockapi/weixin_pay.png',
	PAY_INTERFACE_COD: '/standard_static/img/mockapi/cod.png',
	PAY_INTERFACE_WEIZOOM_COIN: '/standard_static/img/mockapi/wzcoin.png',
}
PAYTYPE2NAME = {
	-1: u'',
	PAY_INTERFACE_PREFERENCE: u'优惠抵扣',
	PAY_INTERFACE_ALIPAY: u'支付宝',
	PAY_INTERFACE_TENPAY: u'财付通',
	PAY_INTERFACE_WEIXIN_PAY: u'微信支付',
	PAY_INTERFACE_COD: u'货到付款',
	PAY_INTERFACE_WEIZOOM_COIN: u"微众卡支付"
}
PAYNAME2TYPE = {
	u'优惠抵扣':PAY_INTERFACE_PREFERENCE,
	u'支付宝': PAY_INTERFACE_ALIPAY,
	u'财付通': PAY_INTERFACE_TENPAY,
	u'微信支付': PAY_INTERFACE_WEIXIN_PAY,
	u'货到付款': PAY_INTERFACE_COD,
	u"微众卡支付": PAY_INTERFACE_WEIZOOM_COIN
}

VALID_PAY_INTERFACES = [
	PAY_INTERFACE_WEIXIN_PAY,
	PAY_INTERFACE_COD,
	PAY_INTERFACE_WEIZOOM_COIN,
	PAY_INTERFACE_ALIPAY]
ONLINE_PAY_INTERFACE = [
	PAY_INTERFACE_WEIXIN_PAY,
	PAY_INTERFACE_ALIPAY,
	PAY_INTERFACE_WEIZOOM_COIN,
	PAY_INTERFACE_TENPAY]
	
class PayInterface(models.Model):
	"""
	支付方式
	"""
	owner = models.ForeignKey(User)
	type = models.IntegerField()  # 支付接口类型
	description = models.CharField(max_length=50)  # 描述
	is_active = models.BooleanField(default=True)  # 是否启用
	related_config_id = models.IntegerField(default=0)  # 各种支付方式关联配置信息的id
	created_at = models.DateTimeField(auto_now_add=True)  # 创建日期

	class Meta(object):
		db_table = 'mall_pay_interface'

	def pay(self, order, webapp_owner_id):
		if PAY_INTERFACE_ALIPAY == self.type:
			return '/webapp/alipay/?woid={}&order_id={}&related_config_id={}'.format(webapp_owner_id, order.order_id, self.related_config_id)
		elif PAY_INTERFACE_TENPAY == self.type:
			from account.models import UserProfile
			user_profile = UserProfile.objects.get(user_id=webapp_owner_id)
			call_back_url = "http://{}/tenpay/mall/pay_result/get/{}/{}/".format(
				user_profile.host,
				webapp_owner_id,
				self.related_config_id)
			notify_url = "http://{}/tenpay/mall/pay_notify_result/get/{}/{}/".format(
				user_profile.host,
				webapp_owner_id,
				self.related_config_id)
			pay_submit = TenpaySubmit(
				self.related_config_id,
				order,
				call_back_url,
				notify_url)
			tenpay_url = pay_submit.submit()

			return tenpay_url
		elif PAY_INTERFACE_COD == self.type:
			return './?woid={}&module=mall&model=pay_result&action=get&pay_interface_type={}&order_id={}'.format(
				webapp_owner_id,
				PAY_INTERFACE_COD,
				order.order_id)
		elif PAY_INTERFACE_WEIXIN_PAY == self.type:
			return '/webapp/wxpay/?woid={}&order_id={}&pay_id={}&showwxpaytitle=1'.format(
				webapp_owner_id,
				order.order_id,
				self.id)
		else:
			return ''

	def parse_pay_result(self, request):
		error_msg = ''
		if PAY_INTERFACE_ALIPAY == self.type:
			order_id = request.GET.get('out_trade_no', None)
			trade_status = request.GET.get('result', '')
			is_trade_success = ('success' == trade_status.lower())
		elif PAY_INTERFACE_TENPAY == self.type:
			trade_status = int(request.GET.get('trade_status', -1))
			is_trade_success = (0 == trade_status)
			error_msg = request.GET.get('pay_info', '')
			order_id = request.GET.get('out_trade_no', None)
		elif PAY_INTERFACE_COD == self.type:
			is_trade_success = True
			order_id = request.GET.get('order_id')
		elif PAY_INTERFACE_WEIXIN_PAY == self.type:
			is_trade_success = True
			order_id = request.GET.get('order_id')
		else:
			pass

		#兼容改价
		try:
			order_id = order_id.split('-')[0]
		except:
			pass

		return {
			'is_success': is_trade_success,
			'order_id': order_id,
			'error_msg': error_msg
		}

	def parse_notify_result(self, request):
		error_msg = ''
		if PAY_INTERFACE_ALIPAY == self.type:
			config = UserAlipayOrderConfig.objects.get(
				id=self.related_config_id)
			notify = AlipayNotify(request, config)
		elif PAY_INTERFACE_TENPAY == self.type:
			notify = TenpayNotify(request)
		elif PAY_INTERFACE_WEIXIN_PAY == self.type:
			notify = WxpayNotify(request)
		else:
			notify = None

		if notify:
			order_id = notify.get_payed_order_id()
			is_trade_success = notify.is_pay_succeed()
			error_msg = notify.get_pay_info()
			reply_response = notify.get_reply_response()
			order_payment_info = notify.get_order_payment_info()
		else:
			order_id = ''
			is_trade_success = False
			error_msg = ''
			reply_response = ''
			order_payment_info = None

		#兼容改价
		try:
			order_id = order_id.split('-')[0]
		except:
			pass

		return {
			'order_id': order_id,
			'is_success': is_trade_success,
			'error_msg': error_msg,
			'reply_response': reply_response,
			'order_payment_info': order_payment_info
		}

	def get_str_name(self):
		return PAYTYPE2NAME[self.type]


V2 = 0
V3 = 1
class UserWeixinPayOrderConfig(models.Model):
	owner = models.ForeignKey(User)
	app_id = models.CharField(max_length=32, verbose_name='微信公众号app_id')
	app_secret = models.CharField(max_length=64)
	partner_id = models.CharField(max_length=32, verbose_name='合作商户id')
	partner_key = models.CharField(max_length=32, verbose_name='合作商初始密钥')	
	paysign_key = models.CharField(max_length=128, verbose_name='支付专用签名串')	
	pay_version  = models.IntegerField(default=V2)

	class Meta(object):
		db_table = 'account_weixin_pay_order_config'











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
# 订单相关Model
#########################################################################
ORDER_STATUS_NOT = 0  # 待支付：已下单，未付款
ORDER_STATUS_CANCEL = 1  # 已取消：取消订单(回退销量)
ORDER_STATUS_PAYED_SUCCESSED = 2  # 已支付：已下单，已付款，已不存此状态
ORDER_STATUS_PAYED_NOT_SHIP = 3  # 待发货：已付款，未发货
ORDER_STATUS_PAYED_SHIPED = 4  # 已发货：已付款，已发货
ORDER_STATUS_SUCCESSED = 5  # 已完成：自下单10日后自动置为已完成状态
ORDER_STATUS_REFUNDING = 6  # 退款中
ORDER_STATUS_REFUNDED = 7  # 退款完成(回退销量)

ORDER_BILL_TYPE_NONE = 0  # 无发票
ORDER_BILL_TYPE_PERSONAL = 1  # 个人发票
ORDER_BILL_TYPE_COMPANY = 2  # 公司发票
STATUS2TEXT = {
	ORDER_STATUS_NOT: u'待支付',
	ORDER_STATUS_CANCEL: u'已取消',
	ORDER_STATUS_PAYED_SUCCESSED: u'已支付',
	ORDER_STATUS_PAYED_NOT_SHIP: u'待发货',
	ORDER_STATUS_PAYED_SHIPED: u'已发货',
	ORDER_STATUS_SUCCESSED: u'已完成',
	ORDER_STATUS_REFUNDING: u'退款中',
	ORDER_STATUS_REFUNDED: u'退款成功',
}

AUDIT_STATUS2TEXT = {
	ORDER_STATUS_REFUNDING: u'退款中',
	ORDER_STATUS_REFUNDED: u'退款成功',
}

REFUND_STATUS2TEXT = {
	ORDER_STATUS_REFUNDING: u'退款中',
	ORDER_STATUS_REFUNDED: u'退款成功',
}

ORDERSTATUS2TEXT = STATUS2TEXT

ORDERSTATUS2MOBILETEXT = copy.copy(ORDERSTATUS2TEXT)
ORDERSTATUS2MOBILETEXT[ORDER_STATUS_PAYED_SHIPED] = u'待收货'

PAYMENT_INFO = u'下单'

THANKS_CARD_ORDER = 'thanks_card'  # 感恩贺卡类型的订单

ORDER_TYPE2TEXT = {
	PRODUCT_DEFAULT_TYPE: u'普通订单',
	PRODUCT_DELIVERY_PLAN_TYPE: u'套餐订单',
	PRODUCT_TEST_TYPE: u'测试订单',
	THANKS_CARD_ORDER: u'贺卡订单',
	PRODUCT_INTEGRAL_TYPE: u'积分商品'
}

ORDER_SOURCE_OWN = 0
ORDER_SOURCE_WEISHOP = 1
ORDER_SOURCE2TEXT = {
	ORDER_SOURCE_OWN: u'本店',
	ORDER_SOURCE_WEISHOP: u'商城',
}

QUALIFIED_ORDER_STATUS = [ORDER_STATUS_PAYED_NOT_SHIP, ORDER_STATUS_PAYED_SHIPED, ORDER_STATUS_SUCCESSED]

class Order(models.Model):
	"""
	订单

	表名: mall_order
	"""
	order_id = models.CharField(max_length=100)  # 订单号
	webapp_user_id = models.IntegerField()  # WebApp用户的id
	webapp_id = models.CharField(max_length=20, verbose_name='店铺ID')  # webapp,订单成交的店铺id
	webapp_source_id = models.CharField(max_length=20, default=0, verbose_name='商品来源店铺ID')  # 订单内商品实际来源店铺的id，已废弃
	buyer_name = models.CharField(max_length=100)  # 购买人姓名
	buyer_tel = models.CharField(max_length=100, default='')  # 购买人电话,已废弃
	ship_name = models.CharField(max_length=100)  # 收货人姓名
	ship_tel = models.CharField(max_length=100)  # 收货人电话
	ship_address = models.CharField(max_length=200)  # 收货人地址
	area = models.CharField(max_length=100)
	status = models.IntegerField(default=ORDER_STATUS_NOT)  # 订单状态
	order_source = models.IntegerField(default=ORDER_SOURCE_OWN)  # 订单来源 0本店 1商城 已废弃，新订单使用默认值兼容老数据
	bill_type = models.IntegerField(default=ORDER_BILL_TYPE_NONE)  # 发票类型，已废弃
	bill = models.CharField(max_length=100, default='')  # 发票信息 已废弃
	remark = models.TextField(default='')  # 备注
	product_price = models.FloatField(default=0.0)  # 商品金额（应用促销后的商品总价）
	coupon_id = models.IntegerField(default=0)  # 优惠券id，用于支持返还优惠券
	coupon_money = models.FloatField(default=0.0)  # 优惠券金额
	postage = models.FloatField(default=0.0)  # 运费
	integral = models.IntegerField(default=0)  # 积分
	integral_money = models.FloatField(default=0.0)  # 积分对应金额
	member_grade = models.CharField(max_length=50, default='')  # 会员等级
	member_grade_discount = models.IntegerField(default=100)  # 折扣
	member_grade_discounted_money = models.FloatField(default=0.0)  # 折扣金额，已废弃
	# 实付金额: final_price = (product_price + postage) - (coupon_money + integral_money + weizoom_card_money)
	final_price = models.FloatField(default=0.0)
	pay_interface_type = models.IntegerField(default=-1)  # 支付方式
	express_company_name = models.CharField(max_length=50, default='')  # 物流公司名称
	express_number = models.CharField(max_length=100, default='')  # 快递单号
	leader_name = models.CharField(max_length=256, default='')  # 订单负责人
	customer_message = models.CharField(max_length=1024)  # 商家留言
	payment_time = models.DateTimeField(default=DEFAULT_DATETIME)  # 订单支付时间
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间
	type = models.CharField(max_length=50, default=PRODUCT_DEFAULT_TYPE)  # 产品的类型，已废弃
	integral_each_yuan = models.IntegerField(verbose_name='一元是多少积分', default=-1)
	reason = models.CharField(max_length=256, default='')  # 取消订单原因
	update_at = models.DateTimeField(auto_now=True)  # 订单信息更新时间 2014-11-11
	weizoom_card_money = models.FloatField(default=0.0)  # 微众卡抵扣金额
	promotion_saved_money = models.FloatField(default=0.0)  # 促销优惠金额（只在含限时抢购商品时产生）
	edit_money = models.FloatField(default=0.0)  # 商家修改差价：final_price（计算公式得） - final_price（商家修改成的）= edit_money
	origin_order_id = models.IntegerField(default=0) # 原始(母)订单id，用于微众精选拆单
	# origin_order_id=-1表示有子订单，>0表示有父母订单，=0为默认数据
	supplier = models.IntegerField(default=0) # 订单供货商，用于微众精选拆单
	is_100 = models.BooleanField(default=True) # 是否是快递100能够查询的快递

	class Meta(object):
		db_table = 'mall_order'
		verbose_name = '订单'
		verbose_name_plural = '订单'

	@property
	def has_sub_order(self):
		"""
		判断该订单是否有子订单
		"""
		return self.origin_order_id == -1 and self.status > 0 #未支付的订单按未拆单显示

	@property
	def is_sub_order(self):
		return self.origin_order_id > 0

	@staticmethod
	def get_sub_order_ids(origin_order_id):
		orders = Order.objects.filter(origin_order_id=origin_order_id)
		sub_order_ids = [order.order_id for order in orders]
		return sub_order_ids


	@staticmethod
	def by_webapp_user_id(webapp_user_id, order_id=None):
		if order_id:
			return Order.objects.filter(Q(webapp_user_id__in=webapp_user_id) | Q(id__in=order_id)).filter(origin_order_id__lte=0)
		if isinstance(webapp_user_id, int) or isinstance(webapp_user_id, long):
			return Order.objects.filter(webapp_user_id=webapp_user_id, origin_order_id__lte=0)
		else:
			return Order.objects.filter(webapp_user_id__in=webapp_user_id, origin_order_id__lte=0)

	@staticmethod
	def by_webapp_id(webapp_id):
		# print webapp_id.isdight()
		if str(webapp_id) == '3394':
			return Order.objects.filter(webapp_id=webapp_id)
		if isinstance(webapp_id, list):
			return Order.objects.filter(webapp_source_id__in=webapp_id, origin_order_id__lte=0)
		else:
			return Order.objects.filter(webapp_source_id=webapp_id, origin_order_id__lte=0)

	##########################################################################
	# get_coupon: 获取定单使用的优惠券信息
	##########################################################################
	def get_coupon(self):
		if self.coupon_id == 0:
			return None
		else:
			from mall.promotion import models as coupon_model
			coupon = coupon_model.Coupon.objects.filter(id=self.coupon_id)
			if len(coupon) == 1:
				return coupon[0]
			return None

	##########################################################################
	# get_weizoom_card_id: 获取定单使用的微众卡的id
	##########################################################################
	# def get_used_weizoom_card_id(self):
	# 	if self.pay_interface_type == PAY_INTERFACE_WEIZOOM_COIN:
	# 		from market_tools.tools.weizoom_card import models as weizoom_card_model
	# 		weizoom_card_id = weizoom_card_model.WeizoomCardHasOrder.objects.get(
	# 			order_id=self.order_id).card_id
	# 		weizoom_card_number = weizoom_card_model.WeizoomCard.objects.get(
	# 			id=weizoom_card_id).weizoom_card_id
	# 		return weizoom_card_id, weizoom_card_number
	# 	else:
	# 		return None, None

	@staticmethod
	def fill_payment_time(orders):
		order_ids = [order.order_id for order in orders]
		order2paylog = dict(
			[
				(pay_log.order_id, pay_log)
				for pay_log in OrderOperationLog.objects.filter(
					order_id__in=order_ids, action='支付')])
		for order in orders:
			if order.order_id in order2paylog:
				order.payment_time = order2paylog[order.order_id].created_at
			else:
				order.payment_time = ''

	##########################################################################
	# get_orders_by_coupon_ids: 通过优惠券id获取订单列表
	##########################################################################
	@staticmethod
	def get_orders_by_coupon_ids(coupon_ids):
		if len(coupon_ids) == 0:
			return None
		else:
			return list(Order.objects.filter(coupon_id__in=coupon_ids))

	@property
	def get_pay_interface_name(self):
		return PAYTYPE2NAME.get(self.pay_interface_type, u'')

	@property
	def get_str_area(self):
		from utils import regional_util
		if self.area:
			return regional_util.get_str_value_by_string_ids(self.area)
		else:
			return ''

	# 订单金额
	def get_total_price(self):
		return self.member_grade_discounted_money + self.postage

	# 支付金额
	# 1、如果是本店的订单，就显示 支付金额
	# 2、如果是商城下的单，显示  订单金额
	def get_final_price(self, webapp_id):
		if self.webapp_id == webapp_id:
			return self.final_price
		else:
			return self.get_total_price()

	# 订单使用积分
	# 1、如果是本店的订单，返回使用积分
	# 2、如果是商城下的单，返回空
	def get_use_integral(self, webapp_id):
		if self.webapp_id == webapp_id:
			return self.integral
		else:
			return ''

	def get_products(self):
		return OrderHasProduct.objects.filter(order=self)

	@staticmethod
	def get_order_has_price_number(order):
		numbers = OrderHasProduct.objects.filter(
			order=order).aggregate(
			Sum("total_price"))
		number = 0
		if numbers["total_price__sum"] is not None:
			number = numbers["total_price__sum"]

		return number

	@staticmethod
	def get_order_has_product(order):
		relations = list(OrderHasProduct.objects.filter(order=order))
		product_ids = [r.product_id for r in relations]
		return Product.objects.filter(id__in=product_ids)

	@staticmethod
	def get_order_has_product_number(order):
		numbers = OrderHasProduct.objects.filter(
			order=order).aggregate(
			Sum("number"))
		number = 0
		if numbers["number__sum"] is not None:
			number = numbers["number__sum"]
		return number

	def get_status_text(self):
		return STATUS2TEXT[self.status]

	# add by bert at member_4.0
	@staticmethod
	def get_orders_final_price_sum(webapp_user_ids):
		numbers = Order.by_webapp_user_id(webapp_user_ids).filter(
			status__gte=ORDER_STATUS_PAYED_SUCCESSED).aggregate(
			Sum("final_price"))
		number = 0
		if numbers["final_price__sum"] is not None:
			number = numbers["final_price__sum"]
		return number

	@staticmethod
	def get_pay_numbers(webapp_user_ids):
		return Order.objects.filter(
			webapp_user_id__in=webapp_user_ids,
			status__gte=ORDER_STATUS_PAYED_SUCCESSED, origin_order_id__lte=0).count()

	@staticmethod
	def get_webapp_user_ids_pay_times_greater_than(webapp_id, pay_times):
		list_info = Order.by_webapp_user_id(webapp_id).filter(
			status__gte=ORDER_STATUS_PAYED_SUCCESSED).values('webapp_user_id').annotate(
			dcount=Count('webapp_user_id'))
		webapp_user_ids = []
		if list_info:
			for vlaue in list_info:
				if vlaue['dcount'] >= int(pay_times):
					webapp_user_ids.append(vlaue['webapp_user_id'])
		return webapp_user_ids

	@staticmethod
	def get_webapp_user_ids_pay_days_in(webapp_id, days):
		date_day = datetime.today()-timedelta(days=int(days))
		return [
			order.webapp_user_id for order in Order.objects.filter(
				webapp_id=webapp_id,
				status__gte=ORDER_STATUS_PAYED_SUCCESSED,
				payment_time__gte=date_day, origin_order_id__lte=0)]

	@property
	def get_express_details(self):
		if hasattr(self, '_express_details'):
			return self._express_details

		self._express_details = express_util.get_express_details_by_order(self)
		return self._express_details

	@property
	def get_express_detail_last(self):
		if len(self.get_express_details) > 0:
			return self.get_express_details[-1]

		return None

	@staticmethod
	def get_orders_from_webapp_user_ids(webapp_user_ids):
		return Order.objects.filter(webapp_user_id__in=webapp_user_ids)

	def __str__(self):
		r = {}
		for k in self._data.keys():
			try:
				 r[k] = str(getattr(self, k))
			except:
				 r[k] = json.dumps(getattr(self, k))
		return str(r)

# def belong_to(webapp_id):
# 	"""
# 	webapp_id为request中的商铺id
# 	返回输入该id的所有Order的QuerySet
# 	"""
# 	if webapp_id == '3394':
# 		return Order.objects.filter(webapp_id=webapp_id)
# 	else:
# 		return Order.objects.filter(webapp_source_id=webapp_id, origin_order_id__lte=0)


# Order.objects.belong_to = belong_to


# added by chuter
########################################################################
# OrderPaymentInfo: 订单支付信息
########################################################################
class OrderPaymentInfo(models.Model):
	order = models.ForeignKey(Order)
	transaction_id = models.CharField(max_length=32)  # 交易号
	appid = models.CharField(max_length=64)  # 公众平台账户的AppId
	openid = models.CharField(max_length=100)  # 购买用户的OpenId
	out_trade_no = models.CharField(max_length=100)  # 该平台中订单号

	class Meta(object):
		db_table = 'mall_order_payment_info'
		verbose_name = '订单支付信息'
		verbose_name_plural = '订单支付信息'


class OrderHasProduct(models.Model):
	"""
	<order, product>关联
	"""
	order = models.ForeignKey(Order)
	product = models.ForeignKey(Product, related_name='product')
	product_name = models.CharField(max_length=256)  # 商品名
	product_model_name = models.CharField(max_length=256, default='')  # 商品规格名
	price = models.FloatField()  # 商品单价
	total_price = models.FloatField()  # 订单价格
	is_shiped = models.IntegerField(default=0)  # 是否出货
	number = models.IntegerField(default=1)  # 商品数量
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间
	promotion_id = models.IntegerField(default=0)  # 促销信息id
	promotion_money = models.FloatField(default=0.0)  # 促销抵扣金额
	grade_discounted_money = models.FloatField(default=0.0)  # 折扣金额
	integral_sale_id = models.IntegerField(default=0) #使用的积分应用的id

	class Meta(object):
		db_table = 'mall_order_has_product'

	# 填充特定的规格信息
	@property
	def get_specific_model(self):
		if hasattr(self, '_product_specific_model'):
			return self._product_specific_model
		else:
			try:
				self._product_specific_model = self.product.fill_specific_model(
					self.product_model_name)
				return self._product_specific_model
			except:
				return None

	# 如果规格有图片就显示，如果没有，使用缩略图
	@property
	def order_thumbnails_url(self):
		if hasattr(self, '_order_thumbnails_url'):
			return self._order_thumbnails_url
		else:
			if self.get_specific_model:
				for model in self.get_specific_model:
					if model['property_pic_url']:
						self._order_thumbnails_url = model['property_pic_url']
						return self._order_thumbnails_url
			# 没有图片使用商品的图片
			self._order_thumbnails_url = self.product.thumbnails_url
			return self._order_thumbnails_url


class OrderHasPromotion(models.Model):
	"""
	<order, promotion>关联
	"""
	order = models.ForeignKey(Order)
	webapp_user_id = models.IntegerField()  # WebApp用户的id
	promotion_id = models.IntegerField(default=0)  #促销id
	promotion_type = models.CharField(max_length=125, default='') #促销类型
	promotion_result_json = models.TextField(default='{}') #促销结果
	created_at = models.DateTimeField(auto_now_add=True) #创建时间
	integral_money = models.FloatField(default=0.0) # 积分抵扣钱数
	integral_count = models.IntegerField(default=0) # 使用的积分

	class Meta(object):
		db_table = 'mall_order_has_promotion'

	@property
	def promotion_result(self):
		data = json.loads(self.promotion_result_json)
		data['type'] = self.promotion_type
		return data




#########################################################################
# 购物相关Model
#########################################################################
class ShoppingCart(models.Model):
	"""
	购物车
	"""
	webapp_user_id = models.IntegerField(default=0)  # WebApp用户
	product = models.ForeignKey(Product)  # 商品
	product_model_name = models.CharField(max_length=125)  # 商品规格名
	count = models.IntegerField(default=1)  # 商品数量
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间

	class Meta(object):
		db_table = 'mall_shopping_cart'



#########################################################################
# 商品评价相关Model
#########################################################################
SCORE = (
	('1', '1分'),
	('2', '2分'),
	('3', '3分'),
	('4', '4分'),
	('5', '5分'),
)

class OrderReview(models.Model):
	owner_id = models.IntegerField()  # 订单的主人
	order_id = models.IntegerField()  # 订单号
	member_id = models.IntegerField()  # 会员ID
	serve_score = models.CharField(  # 服务态度评分
		max_length=1,
		default='5'
	)
	deliver_score = models.CharField(  # 发货速度评分
		max_length=1,
		default='5'
	)
	process_score = models.CharField(  # 物流服务评分
		max_length=1,
		default='5'
	)

	class Meta(object):
		db_table = 'mall_order_review'


# 审核状态
PRODUCT_REVIEW_STATUS_BLOCKED = '-1'
PRODUCT_REVIEW_STATUS_UNPROCESSED = '0'
PRODUCT_REVIEW_STATUS_PASSED = '1'
PRODUCT_REVIEW_STATUS_PASSED_PINNED= '2'

PRODUCT_REVIEW_STATUS = (
	(PRODUCT_REVIEW_STATUS_BLOCKED, 		'已屏蔽'),
	(PRODUCT_REVIEW_STATUS_UNPROCESSED, 	'待审核'),
	(PRODUCT_REVIEW_STATUS_PASSED,			'已通过'),
	(PRODUCT_REVIEW_STATUS_PASSED_PINNED, '通过并置顶'),
)


class ProductReview(models.Model):
	"""
	商品评价
	"""
	member_id = models.IntegerField()
	owner_id = models.IntegerField()
	order_review = models.ForeignKey(OrderReview)
	order_id = models.IntegerField()  # 订单ID
	product_id = models.IntegerField()
	order_has_product = models.ForeignKey(OrderHasProduct)
	product_score = models.CharField(max_length=1, default='5')
	review_detail = models.TextField()  # 评价详情
	created_at = models.DateTimeField(auto_now=True)  # 评价时间
	top_time = models.DateTimeField(default=DEFAULT_DATETIME) # 置顶时间
	status = models.CharField(  # 审核状态
		max_length=2,
		choices=PRODUCT_REVIEW_STATUS,
		default='0')

	class Meta(object):
		db_table = 'mall_product_review'


class ProductReviewPicture(models.Model):
	"""
	商品评价图片
	"""
	product_review = models.ForeignKey(ProductReview)
	order_has_product = models.ForeignKey(OrderHasProduct)
	att_url = models.CharField(max_length=1024)  # 附件地址

	class Meta:
		verbose_name = "商品评价图片"
		verbose_name_plural = "商品评价图片"
		db_table = "mall_product_review_picture"




########################################################################
# OrderOperationLog:订单操作日志
########################################################################
class OrderOperationLog(models.Model):
	order_id = models.CharField(max_length=50)
	remark = models.TextField(default='')
	action = models.CharField(max_length=50)
	operator = models.CharField(max_length=50)
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间

	class Meta(object):
		db_table = 'mall_order_operation_log'
		verbose_name = '订单后台操作日志'
		verbose_name_plural = '订单后台操作日志'


########################################################################
# OrderStatusLog:订单状态日志
########################################################################
class OrderStatusLog(models.Model):
	order_id = models.CharField(max_length=50)
	from_status = models.IntegerField()
	to_status = models.IntegerField()
	remark = models.TextField(default='')
	operator = models.CharField(max_length=50)
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间

	class Meta(object):
		db_table = 'mall_order_status_log'
		verbose_name = '订单状态日志'
		verbose_name_plural = '订单状态日志'


########################################################################
# Supplier:供货商信息
########################################################################
class Supplier(models.Model):
	owner = models.ForeignKey(User)
	name = models.CharField(max_length=16)  # 供货商名称
	responsible_person = models.CharField(max_length=100) # 供货商负责人
	supplier_tel = models.CharField(max_length=100) # 供货商电话
	supplier_address = models.CharField(max_length=256) # 供货商地址
	remark = models.CharField(max_length=256) # 备注
	is_delete = models.BooleanField(default=False)  # 是否已经删除
	created_at = models.DateTimeField(auto_now_add=True)  # 添加时间

	class Meta(object):
		verbose_name = "供货商"
		verbose_name_plural = "供货商操作"
		db_table = "mall_supplier"

	def get_supplier_name(supplier_id):
		supplier = Supplier.select().dj_where(id=supplier_id).first()
		
		if supplier:
			return supplier.name
		else:
			return ''
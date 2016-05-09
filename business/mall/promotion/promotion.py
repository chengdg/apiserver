# -*- coding: utf-8 -*-
"""@package business.mall.promotion.promotion
促销

"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from eaglet.decorator import param_required
#from wapi import wapi_utils
from eaglet.core.cache import utils as cache_util
from db.mall import models as mall_models
from db.mall import promotion_models
from eaglet.core import watchdog
from business import model as business_model
import settings


class Promotion(business_model.Model):
	"""
	促销
	"""
	__slots__ = (
		'id',
		'owner_id',
		'type',
		'display_type',
		'type_name',
		'name',
		'promotion_title',
		'status',
		'display_status',
		'start_date',
		'end_date',
		'member_grade_id',
		'created_at'
	)

	def __init__(self):
		business_model.Model.__init__(self)

	def __get_real_status(self):
		"""
		根据当前时间与start_date, end_date的关系，获取真实的status
		"""

		#TODO2: 处理promotion从数据库promotion_result加载的情况，后续将去掉这里的对self.start_date的判断逻辑
		if not self.start_date:
			return promotion_models.PROMOTION_STATUS_FINISHED

		now = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
		if self.start_date > now:
			return promotion_models.PROMOTION_STATUS_NOT_START
		elif self.end_date < now:
			return promotion_models.PROMOTION_STATUS_FINISHED
		else:
			return promotion_models.PROMOTION_STATUS_STARTED

	def _init_promotion_slot_from_model(self, promotion_model):
		self._init_slot_from_model(promotion_model, Promotion.__slots__)
		self.start_date = self.start_date.strftime("%Y-%m-%d %H:%M:%S")
		self.end_date = self.end_date.strftime("%Y-%m-%d %H:%M:%S")
		self.created_at = self.created_at.strftime("%Y-%m-%d %H:%M:%S")
		self.status = self.status if self.status == promotion_models.PROMOTION_STATUS_FINISHED else self.__get_real_status()
		self.display_status = promotion_models.PROMOTIONSTATUS2NAME.get(self.status, u'未知')
		self.display_type = promotion_models.PROMOTION2TYPE.get(self.type, {'display_name':u'未知'})['display_name']
		self.type_name = promotion_models.PROMOTION2TYPE.get(self.type, {'name':u'unknown'})['name']

		self.context['detail_id'] = promotion_model.detail_id

	def _after_fill_specific_detail(self):
		pass

	def fill_specific_detail(self, specific_model):
		"""
		填充促销特定信息
		"""
		if specific_model:
			self._init_slot_from_model(specific_model)

		self._after_fill_specific_detail()

	def is_active(self):
		"""
		判断促销当前是否有效
		"""
		if self.status == promotion_models.PROMOTION_STATUS_FINISHED or self.status == promotion_models.PROMOTION_STATUS_DELETED:
			return False

		#self.__update_status_if_necessary()

		now = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
		if self.start_date > now:
			return False
		if self.end_date < now:
			return False

		return True

	def allocate(self, webapp_user, product):
		"""
		为webapp_user, product分配促销

		Parameters
			webapp_user
			product: ReservedProduct对象

		Returns
			is_success: 如果分配成功，返回True；否则，返回False
			result: 分配成功，返回{}; 否则，返回失败原因
		"""
		raise NotImplementedError("%s must implement allocate method" % str(self.__class__))

	def can_apply_promotion(self, promotion_product_group):
		"""
		判断是否可以在promotion product group上应用促销

		Parameters
			[in] promotion_product_group: 待执行促销活动的PromotionProductGroup对象

		Returns
			如果可以应用促销，返回True; 否则，返回False
		"""

		raise NotImplementedError("%s must implement can_apply_promotion method" % str(self.__class__))

	def apply_promotion(self, promotion_product_group, purchase_info=None):
		"""
		为同属一个PromotionProductGroup的product集合执行促销活动，返回促销结果

		Parameters
			[in, out] promotion_product_group: 待执行促销活动的PromotionProductGroup对象
			[in] purchase_info: 购买信息(PurchaseInfo对象)

		Returns
			促销结果

		Note
			purchase_info中可能会携带前端计算出来的promotion result信息，比如对于integral sale，促销结果就是在前端计算的
		"""
		raise NotImplementedError("%s must implement apply_promotion method" % str(self.__class__))

	def _get_detail_data(self):
		raise NotImplementedError("_get_detail_data must be implemented by Promotion's subclass " + str(type(self)))

	@property
	def detail(self):
		return self._get_detail_data()

	def can_use_for(self, webapp_user):
		"""
		判断当前webapp_user是否可以使用该促销

		Parameters
			[in] webapp_user

		Returns
			True: webapp_user可以使用该促销
			False: webapp_user不能使用该促销

		Note
			两种情况下，webapp_user才能使用促销
			1. 促销指定对所有人开放
			2. webapp_user的会员等级等于促销指定开放的会员等级
		"""
		if self.member_grade_id <= 0:
			return True

		if webapp_user.is_match_member_grade(self.member_grade_id):
			return True
		else:
			return False

	@property
	def DetailClass(self):
		"""
		[property] 促销的detail类
		"""
		if self.type == promotion_models.PROMOTION_TYPE_FLASH_SALE:
			return promotion_models.FlashSale
		elif self.type == promotion_models.PROMOTION_TYPE_PRICE_CUT:
			return promotion_models.PriceCut
		elif self.type == promotion_models.PROMOTION_TYPE_INTEGRAL_SALE:
			return promotion_models.IntegralSale
		elif self.type == promotion_models.PROMOTION_TYPE_PREMIUM_SALE:
			return promotion_models.PremiumSale
		elif self.type == promotion_models.PROMOTION_TYPE_COUPON:
			return promotion_models.CouponRule
		else:
			return None

	def to_dict(self):
		data = {}
		data.update(super(Promotion, self).to_dict(slots=Promotion.__slots__))
		data.update(super(Promotion, self).to_dict(slots=self.__slots__))
		data['detail'] = self.detail

		return data

	def after_from_dict(self):
		self.status = self.__get_real_status()

	@classmethod
	def from_dict(cls, dict):
		slots = []
		slots.extend(Promotion.__slots__)
		slots.extend(cls.__slots__)

		instance = cls()
		for slot in slots:
			value = dict.get(slot, None)
			setattr(instance, slot, value)
		instance.after_from_dict()
		return instance
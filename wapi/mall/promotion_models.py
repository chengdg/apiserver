#coding: utf8
import copy
from datetime import datetime
import json

from db import models
from wapi.user.models import User
from core.watchdog.utils import watchdog_fatal
import settings
from wapi.mall import models as mall_models


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

	def __update_status_if_necessary(self):
		if self.is_permanant_active:
			if self.status != FORBIDDEN_STATUS_STARTED:
				self.status = FORBIDDEN_STATUS_STARTED
				self.save()
			return
		now = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

		if type(self.end_date) == datetime:
			end_date = self.end_date.strftime('%Y-%m-%d %H:%M:%S')
		else:
			end_date = self.end_date

		if type(self.start_date) == datetime:
			start_date = self.start_date.strftime('%Y-%m-%d %H:%M:%S')
		else:
			start_date = self.start_date

		if start_date <= now and end_date > now and self.status == FORBIDDEN_STATUS_NOT_START:
			# 未开始状态,但是时间已经再开始,由于定时任务尚未执行
			self.status = FORBIDDEN_STATUS_STARTED
			self.save()
		elif end_date <= now and (self.status == FORBIDDEN_STATUS_NOT_START or self.status == FORBIDDEN_STATUS_STARTED):
			# 未开始,进行中状态,但是时间到期了,由于定时任务尚未执行
			self.status = FORBIDDEN_STATUS_FINISHED
			self.save()

	@property
	def status_name(self):
		self.__update_status_if_necessary()
		return FORBIDDENSTATUS2NAME.get(self.status, u'未知')

	@property
	def is_active(self):
		if self.is_permanant_active and self.status != FORBIDDEN_STATUS_FINISHED:
			return True

		if self.status == FORBIDDEN_STATUS_FINISHED:
			return False

		self.__update_status_if_necessary()

		if self.status == FORBIDDEN_STATUS_NOT_START or self.status == FORBIDDEN_STATUS_FINISHED:
			return False

		return True

	@property
	def is_overdue(self):
		if self.status == FORBIDDEN_STATUS_FINISHED:
			return True

		if self.is_permanant_active:
			return False

		self.__update_status_if_necessary()

		if self.status == FORBIDDEN_STATUS_FINISHED:
			return True

		return False

	def to_dict(self):
		Product.fill_details(self.owner_id, [self.product], {
			'with_product_model': True,
			"with_model_property_info": True,
			'with_sales': True
		})
		return {
			'id': self.id,
			'product': self.product.format_to_dict(),
			'status': self.status,
			'status_name': self.status_name,
			'start_date': self.start_date.strftime('%Y-%m-%d %H:%M:%S'),
			'end_date': self.end_date.strftime('%Y-%m-%d %H:%M:%S'),
			'is_permanant_active': self.is_permanant_active,
			'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
		}
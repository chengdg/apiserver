# -*- coding: utf-8 -*-
from eaglet.core import watchdog
from eaglet.core.exceptionutil import unicode_full_stack
from eaglet.peewee import Clause,SQL
from business import model as business_model
from eaglet.decorator import param_required

import db.mall.models as mall_models
from util.mysql_str_util import filter_invalid_str

ProductSearchRecordLimit = 10


class ProductSearch(business_model.Model):
	__slots__ = (
	)

	def __init__(self, webapp_owner, webapp_user):
		business_model.Model.__init__(self)
		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user'])
	def get(args):
		"""
		工厂方法，创建ProductSearch对象

		@return ProductSearch对象
		"""
		searcher = ProductSearch(args['webapp_owner'], args['webapp_user'])

		return searcher

	def filter_products(self, args):
		raw_products = args['products']
		product_name = filter_invalid_str(args['product_name'], '').strip()

		products = filter(lambda x: product_name in x['name'], raw_products)
		try:
			self.__log_record(product_name)
		except:
			msg = unicode_full_stack()
			watchdog.alert(msg)

		return products

	def __log_record(self, product_name):
		webapp_user_id = self.context['webapp_user'].id
		woid = self.context['webapp_owner'].id

		mall_models.ProductSearchRecord.create(webapp_user_id=webapp_user_id, woid=woid, content=product_name)

	@staticmethod
	@param_required(['webapp_user_id'])
	def get_records_by_webapp_user(args):
		webapp_user_id = args['webapp_user_id']
		# records = mall_models.ProductSearchRecord.select(mall_models.ProductSearchRecord.content).distinct().order_by(
		# 	-mall_models.ProductSearchRecord.id).dj_where(
		# 	webapp_user_id=webapp_user_id,
		# 	is_deleted=False).limit(ProductSearchRecordLimit)

		# see https://github.com/coleifer/peewee/issues/928
		records = mall_models.ProductSearchRecord.select(Clause(SQL('distinct binary'), mall_models.ProductSearchRecord.content).alias('content')).order_by(
			-mall_models.ProductSearchRecord.id).dj_where(
			webapp_user_id=webapp_user_id,
			is_deleted=False)

		records = records[:10]
		return [str(record.content) for record in records]

	@staticmethod
	@param_required(['webapp_user_id'])
	def delete_record_by_webapp_user(args):
		webapp_user_id = args['webapp_user_id']
		mall_models.ProductSearchRecord.update(is_deleted=True).dj_where(webapp_user_id=webapp_user_id).execute()

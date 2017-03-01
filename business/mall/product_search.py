# -*- coding: utf-8 -*-
import json

from eaglet.core import watchdog
from eaglet.core.exceptionutil import unicode_full_stack
from eaglet.peewee import Clause,SQL
from business import model as business_model
from eaglet.decorator import param_required
from eaglet.core import paginator

import settings
import db.mall.models as mall_models
from util.mysql_str_util import filter_invalid_str
from util import redis_util
from eaglet.core.cache import utils as cache_util
from bdem import msgutil

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
		# records = mall_models.ProductSearchRecord.select(Clause(SQL('distinct binary'), mall_models.ProductSearchRecord.content).alias('content')).order_by(
		# 	-mall_models.ProductSearchRecord.id).dj_where(
		# 	webapp_user_id=webapp_user_id,
		# 	is_deleted=False)

		# records = mall_models.ProductSearchRecord.select(Clause(SQL('binary'), mall_models.ProductSearchRecord.content).alias('content')).group_by(mall_models.ProductSearchRecord.content).order_by(
		# 	-mall_models.ProductSearchRecord.id).dj_where(
		# 	webapp_user_id=webapp_user_id,
		# 	is_deleted=False).limit(ProductSearchRecordLimit)
		# return [str(record.content) for record in records]

		record_objects = mall_models.ProductSearchRecord.select().dj_where(webapp_user_id=webapp_user_id, is_deleted=False).order_by(-mall_models.ProductSearchRecord.id)

		records = []
		i = 0
		for r in record_objects:
			if i < ProductSearchRecordLimit:
				if r.content not in records:
					records.append(r.content)
					i += 1
			else:
				break

		return records

	@staticmethod
	@param_required(['webapp_user_id'])
	def delete_record_by_webapp_user(args):
		webapp_user_id = args['webapp_user_id']
		mall_models.ProductSearchRecord.update(is_deleted=True).dj_where(webapp_user_id=webapp_user_id).execute()

	def search_products(self, category_id, corp_id, cur_page, search_name):
		key = '{wo:%s}_{co:%s}_products' % (corp_id, category_id)
		if not cache_util.exists_key(key):
			# 发送消息让manager_cache缓存分组数据
			topic_name = settings.TOPIC_NAME
			msg_name = 'refresh_category_product'
			data = {
				"corp_id": corp_id,
				"product_ids": category_id
			}
			msgutil.send_message(topic_name, msg_name, data)
			return None, None
		if not cache_util.exists_key('all_simple_products'):
			# TODO发送消息让manager_cache缓存所有简单商品数据
			topic_name = settings.TOPIC_NAME
			msg_name = 'refresh_all_simple_products'
			
			msgutil.send_message(topic_name, msg_name, {})
			return None, None
		all_simple_products = redis_util.hgetall('all_simple_products')
		product_ids = []
		for k, v in all_simple_products.iterms():
			info = json.dumps(v)
			product_name = info.get('name')
			if search_name in product_name:
				product_ids.append(info.get('id'))
		
		# 获取分页信息
		page_info, page_product_ids = paginator.paginate(product_ids, cur_page, 6)
		
		# 获取对应的简单商品数据
		# {
		# 	"id": product.id,
		# 	"name": name,
		# 	"display_price": display_price,
		# 	"thumbnails_url": thumbnails_url,
		# }
		
		simple_product_info = [json.loads(v) for k, v in
							   redis_util.hmget('all_simple_products', page_product_ids).items()]
		
		result = sorted(simple_product_info, key=lambda key: page_product_ids.index(key.get('id')))
		return page_info, result

# -*- coding: utf-8 -*-
import json
import pickle

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
from util import redis_util

ProductSearchRecordLimit = 10


class NewProductSearch(business_model.Model):
	__slots__ = (
	)

	def __init__(self, webapp_owner, webapp_user, cur_page):
		business_model.Model.__init__(self)
		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user
		self.context['cur_page'] = cur_page

	@staticmethod
	@param_required(['webapp_owner', 'webapp_user', 'cur_page'])
	def get(args):
		"""
		工厂方法，创建ProductSearch对象

		@return ProductSearch对象
		"""
		searcher = NewProductSearch(args['webapp_owner'], args['webapp_user'], args['cur_page'])

		return searcher

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

	def search_products(self, category_id, cur_page, search_name):
		try:
			self.__log_record(search_name)
		except:
			msg = unicode_full_stack()
			watchdog.alert(msg)
		cache_no_data = False
		webapp_owner = self.context['webapp_owner']
		category_products_key = '{wo:%s}_{co:%s}_pids' % (webapp_owner.id, 0)
		if not cache_util.exists_key(category_products_key):
			# 发送消息让manager_cache缓存分组数据
			topic_name = settings.TOPIC_NAME
			msg_name = 'refresh_category_product'
			data = {
				"corp_id": webapp_owner.id,
				"category_id": category_id
			}
			msgutil.send_message(topic_name, msg_name, data)
			cache_no_data = True
		if not cache_util.exists_key('all_simple_effective_products'):
			# TODO发送消息让manager_cache缓存所有简单商品数据
			topic_name = settings.TOPIC_NAME
			msg_name = 'all_simple_effective_products'
			
			msgutil.send_message(topic_name, msg_name, {})
			cache_no_data = True
		# 用于搜索的额所有有效商品数据
		all_simple_products = redis_util.hgetall('all_simple_effective_products')
		#  分类所拥有的商品id
		category_product_ids = list(redis_util.lrange(category_products_key, 0, -1))
		if category_product_ids and category_product_ids[0] == 'NONE':
			# 说明分组无商品
			page_info, page_product_ids = paginator.paginate([], cur_page, 6)
			
			return page_info, []
		# 搜索结果id
		product_ids = []
		for product_id, product_name in all_simple_products.items():
			
			if search_name in product_name and product_id in category_product_ids:
				product_ids.append(product_id)
		
		
		# 获取分页信息
		page_info, page_product_ids = paginator.paginate(product_ids, cur_page, 6)
		
		if not page_product_ids:
			return page_info, []
		# TODO 可抽取公用方法
		keys = [':1:apiproduct_simple_detail_{pid:%s}' % product_id for product_id in page_product_ids]
		redis_products = redis_util.mget(keys)
		# 缓存没有此商品详情的key,故需mall_cache_manager缓存数据
		# 这里使用page_product_ids  严重注意这个问题,屌丝!
		no_redis_product_ids = [page_product_ids[index] for index, r in enumerate(redis_products) if r is None]
		if no_redis_product_ids:
			cache_no_data = True
			# 发送消息让manager_cache缓存分组数据
			topic_name = settings.TOPIC_NAME
			msg_name = 'refresh_product_detail'
			data = {
				"corp_id": webapp_owner.id,
				"product_ids": no_redis_product_ids
			}
			msgutil.send_message(topic_name, msg_name, data)
		if cache_no_data:
			page_info, page_product_ids = paginator.paginate([], cur_page, 6)
			return page_info, None
		products = [pickle.loads(product) for product in redis_products]
		result = sorted(products, key=lambda k: page_product_ids.index(str(k.get('id'))))
		return page_info, result

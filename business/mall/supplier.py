# -*- coding: utf-8 -*-
"""@package business.mall.supplier
供货商
"""
import pickle

from business import model as business_model
from eaglet.core.cache import utils as cache_util
from bdem import msgutil
from eaglet.core import paginator

import settings

from db.mall import models as mall_models
from util import redis_util


class Supplier(business_model.Model):
	"""供货商
	"""
	__slots__ = (
	)

	@staticmethod
	def get_supplier_name(supplier_id):
		supplier = mall_models.Supplier.select().dj_where(id=supplier_id).first()
		
		if supplier:
			return supplier.name
		else:
			return ''
		
	def get_products_by_page(self, supplier_id, webapp_owner, cur_page, cur_page_count):
		"""
		获取供货商下所有商品
		"""
		
		# TODO 发送消息并拆分代码
		key = "supplier_products:{%s}" % supplier_id
		if not cache_util.exists_key(key):
			products = mall_models.Product.select().dj_where(supplier=supplier_id)
			product_ids = [product.id for product in products]
			redis_util.sadd(key, *product_ids)
		else:
			product_ids = redis_util.smemebers(key_name=key)
		# 获取该平台所有上架商品
		all_product_key = '{wo:%s}_{co:%s}_pids' % (webapp_owner.id, 0)
		no_cache = False
		if not cache_util.exists_key(key):
			# 发送消息让manager_cache缓存分组数据
			topic_name = settings.TOPIC_NAME
			msg_name = 'refresh_supplier_products'
			data = {
				"corp_id": webapp_owner.id,
				"category_id": 0
			}
			msgutil.send_message(topic_name, msg_name, data)
			no_cache = True
		all_product_ids = redis_util.lrange(all_product_key, 0, -1)
		all_product_ids = [] if all_product_ids is None else all_product_ids
		# 该平台该供货商所有商品id
		product_ids = list(set(product_ids).intersection(set(all_product_ids)))
		page_info, page_product_ids = paginator.paginate(product_ids, cur_page, cur_page_count)
		keys = [':1:apiproduct_simple_detail_{pid:%s}' % product_id for product_id in page_product_ids]
		print keys, '--------------------------------jdkf'
		if not keys:
			page_info, page_product_ids = paginator.paginate([], cur_page, cur_page_count)
			return [], True, page_info
		redis_products = redis_util.mget(keys)
		# 缓存没有此商品详情的key,故需mall_cache_manager缓存数据
		no_redis_product_ids = [page_product_ids[index] for index, r in enumerate(redis_products) if r is None]
		if no_redis_product_ids:
			# 发送消息让manager_cache缓存数据
			topic_name = settings.TOPIC_NAME
			msg_name = 'refresh_product_detail'
			data = {
				"corp_id": webapp_owner.id,
				"product_ids": no_redis_product_ids
			}
			msgutil.send_message(topic_name, msg_name, data)
			no_cache = True
		if no_cache:
			page_info, page_product_ids = paginator.paginate([], cur_page, cur_page_count)
			return [], True, page_info
		# 返回商品数据
		products = [pickle.loads(product) for product in redis_products]
		# result = sorted(products, key=lambda k: page_product_ids.index(str(k.get('id'))))
		return products, False, page_info

	
	
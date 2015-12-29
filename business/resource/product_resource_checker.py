#coding: utf8
"""
检查product resource资源是否可用
"""
from db.mall import models as mall_models
import logging

class ProductResourceChecker(object):

	def __init__(self):
		pass

	def __check_shelve_type(self, product):
		if product.shelve_type == mall_models.PRODUCT_SHELVE_TYPE_OFF:
			return False, {
				'is_succeeded': False,
				'type': 'product:is_off_shelve',
				'msg': u'',
				'short_msg': u'商品已下架'
			}

		return True, {
			'is_succeeded': True
		}

	def __check_product_status(self, product):
		if product.is_deleted:
			return False, {
				'is_succeeded': False,
				'type': 'product:is_deleted',
				'msg': u'商品已删除',
				'short_msg': u'商品已删除'
			}

		return True, {
			'is_succeeded': True
		}


	def check(self, product):
		"""
		检查商品资源是否可分配

		@note 从product_resource.py迁移
		"""
		is_succeeded, reason = self.__check_product_status(product)
		if not is_succeeded:
			return False, reason
			
		is_succeeded, reason = self.__check_shelve_type(product)
		if not is_succeeded:
			return False, reason

		return True, reason
		

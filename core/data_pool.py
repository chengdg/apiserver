# -*- coding: utf-8 -*-
from core.cache import utils as cache_utils
from datetime import datetime


class DataPool(object):
	"""
	使用内存库作为数据池,以redis集合作为基础
	@note:类似集合，适用于单向添加
	"""

	def __init__(self, name, expire=None):
		"""
		@param name: 键名
		@param expire: 过期时间，单位秒
		@return: DataPool对象
		"""
		self.name = name
		self.expire = expire
		self.__created_at = datetime.now()
		self.__has_init = cache_utils.exists_key(self.name)

	def release(self):
		"""
		释放内存中的该集合
		"""
		cache_utils.delete_cache(self.name)

	def is_member(self, member):
		"""
		@param member: 值
		@return member是否是该集合的成员
		"""
		return cache_utils.sismember(self.name, member)

	def __len__(self):
		return cache_utils.scard(self.name)

	@property
	def length(self):
		"""
		@return: 集合成员数
		"""
		return self.__len__()

	def add(self, *values):
		"""
		@param values: 值元组
		@return: 成功添加的数量
		"""
		add_count = cache_utils.sadd(self.name, *values)
		if not self.__has_init:
			self.__has_init = True
			if self.expire:
				real_expire = (datetime.now() - self.__created_at).seconds
				cache_utils.set_key_expire(self.name, real_expire)
			return add_count

	def remove(self, *values):
		"""
		@param values: 删除值元组
		@return:成功删除的数量
		"""
		return cache_utils.srem(self.name, *values)

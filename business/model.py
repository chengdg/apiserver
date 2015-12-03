# -*- coding: utf-8 -*-
import logging

class Model(object):
	__slots__ = ('context', )
	
	def __init__(self):
		self.context = {}

		for slot in self.__slots__:
			#logging.info("setting '%s'" % slot)
			setattr(self, slot, None)

	def _init_slot_from_model(self, model):
		for slot in self.__slots__:
			value = getattr(model, slot, None)
			if value != None:
				if 'id' == slot:
					value = int(value)
				setattr(self, slot, value)

	def after_from_dict(self):
		"""
		from_dict调用结束前的hook函数，允许sub class修改from_dict的结果
		"""
		pass

	@classmethod
	def from_dict(cls, dict):
		instance = cls()
		for slot in cls.__slots__:
			value = dict.get(slot, None)

			setattr(instance, slot, value)
		instance.after_from_dict()
		return instance

	def to_dict(self, *extras):
		result = dict()
		for slot in self.__slots__:
			result[slot] = getattr(self, slot, None)

		for item in extras:
			result[item] = getattr(self, item, None)
			
		return result		

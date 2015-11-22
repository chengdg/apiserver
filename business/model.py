# -*- coding: utf-8 -*-

class Model(object):
	__slots__ = ('context', )
	
	def __init__(self):
		self.context = {}

		for slot in self.__slots__:
			setattr(self, slot, None)

	def _init_slot_from_model(self, model):
		for slot in self.__slots__:
			value = getattr(model, slot, None)
			if value != None:
				if 'id' == slot:
					value = int(value)
				setattr(self, slot, value)

	@classmethod
	def from_dict(cls, dict):
		instance = cls()
		for slot in cls.__slots__:
			value = dict.get(slot, None)

			setattr(instance, slot, value)
		return instance

	def to_dict(self, *extras):
		result = dict()
		for slot in self.__slots__:
			result[slot] = getattr(self, slot, None)

		for item in extras:
			result[item] = getattr(self, item, None)
			
		return result		

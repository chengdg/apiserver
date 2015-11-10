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
			if value:
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
		'''
		if dict == None:
			return None
		#obj = cls.__new__(cls)
		obj = cls()
		for key, value in dict.items():
			try:
				setattr(obj, key, value)
			except AttributeError:
				pass
		return obj
		'''

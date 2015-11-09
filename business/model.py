# -*- coding: utf-8 -*-

class Model(object):
	__slots__ = ('context',)
	
	def __init__(self):
		for slot in self.__slots__:
			setattr(self, slot, None)
		self.context = {}

#coding: utf8
"""@package business.mall.order_exception.OrderException
OrderExcetpion
"""

class OrderException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

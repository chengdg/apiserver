# -*- coding: utf-8 -*-
"""@package business.mall.supplier
供货商
"""

from db.mall import models as mall_models

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
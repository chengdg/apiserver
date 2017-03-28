# -*- coding: utf-8 -*-

__author__ = 'robert'

import datetime
import array

from util.command import BaseCommand

from eaglet.core.cache import utils as cache_util
from bson import json_util
import json
from db.mall import models as mall_models
import copy


class Command(BaseCommand):
	help = "python manage.py temp_resolve_sub_order"
	args = ''
	
	def handle(self, *args, **kargs):
		# order_id , supplier
		order_id_2_supplier = {684928: 100001637,}
		temp_orders = mall_models.Order.select().dj_where(id__in=order_id_2_supplier.keys())
	
		for order in temp_orders:
			supplier_id = order_id_2_supplier[order.id]
			order_id = order.order_id + '^%ss' % str(supplier_id)
		
			sub_order = copy.deepcopy(order)
			sub_order.id = None
			sub_order.order_id = order_id
			sub_order.supplier = supplier_id
			sub_order.origin_order_id = order.id
			sub_order.member_card_money = 0
			sub_order.member_grade_discount = 0
			sub_order.save()
			
			order_has_products = mall_models.OrderHasProduct.select().dj_where(order_id=order.id)
			for product in order_has_products:
				temp_relation = copy.deepcopy(product)
				temp_relation.id = None
				temp_relation.order = sub_order
				temp_relation.save()
		print 'Finished!'

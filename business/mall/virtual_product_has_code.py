# -*- coding: utf-8 -*-
"""
福利卡券活动关联的卡券码

"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from eaglet.decorator import param_required
#from wapi import wapi_utils
from eaglet.core.cache import utils as cache_util
from db.mall import models as mall_models
from db.mall import promotion_models
from eaglet.core import watchdog
from business import model as business_model
from business.mall.product import Product as business_product
import settings
from util import msg_crypt


crypt = msg_crypt.MsgCrypt(settings.WZCARD_ENCRYPT_INFO['token'], settings.WZCARD_ENCRYPT_INFO['encodingAESKey'],
                           settings.WZCARD_ENCRYPT_INFO['id'])
class VirtualProductHasCode(business_model.Model):
	"""
	福利卡券活动关联的卡券码
	"""
	__slots__ = (
		'id',
		'owner_id',
		'virtual_product_id',
		'code',
		'password',
		'start_time',
		'end_time',
		'status',
		'get_time',
		'member_id',
		'oid',
		'order_id',
		'created_at',
		'product'
	)

	def __init__(self, webapp_owner, webapp_user):
		business_model.Model.__init__(self)

		self.context['webapp_owner'] = webapp_owner
		self.context['webapp_user'] = webapp_user
		self.context['other_card'] = promotion_models.VirtualProductHasCode()
		# 初始化数据应该为db model默认值，不应为none
		self._init_slot_from_model(self.context['other_card'])


	
	
	# @property
	# def product(self):
	# 	#TODO 优化
	# 	virtual_product = promotion_models.VirtualProduct.select().dj_where(id=self.virtual_product_id).first()
	# 	print "ttttt>>>>>>>>>>>",virtual_product.product
	# 	#virtual_product.product
	# 	model_product = mall_models.Product.select().dj_where(id=virtual_product.product_id).first() #product_models以为是商品规格...
	# 	#product = business_product(model_product)
	# 	#print "model_product****type>",model_product.type
	# 	a = model_product.to_dict()
	# 	return model_product

	@classmethod
	def __decrypt_password(cls, encrypt_password):
		return crypt.DecryptMsg(encrypt_password)[1]


	@staticmethod
	@param_required(['webapp_owner', 'webapp_user'])
	def get_cards_from_webapp_user(args):
		"""工厂方法，获取member_id对应的VirtualProductHasCode对象集合
		
		"""

		webapp_owner = args['webapp_owner']
		webapp_user = args['webapp_user']
		member_id = webapp_user.member.id
		print "member_id",member_id
		member_has_other_card_models = list(promotion_models.VirtualProductHasCode.select().dj_where(member_id=member_id).order_by(-promotion_models.VirtualProductHasCode.get_time))
		print "member_has_other_card_models",member_has_other_card_models
		cards = []

		for member_has_other_card_model in member_has_other_card_models:
			card = VirtualProductHasCode(webapp_owner, webapp_user)
			card.context['other_card'] = member_has_other_card_model
			print "member_has_other_card_model",member_has_other_card_model.to_dict()
			card._init_slot_from_model(card.context['other_card'])
			card.product = member_has_other_card_model.virtual_product.product
			cards.append(card)
		
		return cards
	@staticmethod
	@param_required(['webapp_owner', 'webapp_user'])
	def handle_from_webapp_user(args):
		"""
		标记虚拟卡是否过期

		"""
		member_has_other_cards = VirtualProductHasCode.get_cards_from_webapp_user(args)

		cards = []
		has_expired_cards = False

		for card in member_has_other_cards:
			card_details_dic = {}
			# 过滤出虚拟商品
			if not card.product.type == 'virtual':
				continue
			card_details_dic['card_id'] = card.code
			card_details_dic['password'] = VirtualProductHasCode.__decrypt_password(card.password)
			card_details_dic['time'] = card.get_time.strftime('%Y-%m-%d')
			card_details_dic['product_id'] = card.product.id
			card_details_dic['name'] = card.product.name
			card_details_dic['status'] = card.status
			card_details_dic['is_expired'] = False
			validate_time_to = card.end_time.strftime('%Y-%m-%d %H:%M:%S')
			card_details_dic['validate_time_from'] = card.start_time.strftime('%Y-%m-%d %H:%M:%S')
			card_details_dic['validate_time_to'] = validate_time_to
			now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			if now > validate_time_to:
				card_details_dic['is_expired'] = True
				has_expired_cards = True

			cards.append(card_details_dic)
		return cards, has_expired_cards


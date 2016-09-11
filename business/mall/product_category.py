# -*- coding: utf-8 -*-
"""@package business.mall.product_category
会员
"""

import re
import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from eaglet.decorator import param_required
#from wapi import wapi_utils

from db.mall import models as mall_models

#import resource
import settings
from eaglet.core import watchdog
from eaglet.core.cache import utils as cache_util
from util import emojicons_util

from business import model as business_model
from business.decorator import cached_context_property

class ProductCategory(business_model.Model):
    """
    会员
    """
    __slots__ = (
        'id',
       # 'owner_id',
        'name',
        #'webapp_user',
        # 'pic_url',
        # 'product_count',
        # 'display_index',
        # 'created_at',
    )

    @staticmethod
    def from_models(query):
        pass

    @staticmethod
    @param_required(['webapp_owner', 'model'])
    def from_model(args):
        """
        工厂对象，根据ProductCategory model获取ProductCategory业务对象

        @param[in] webapp_owner
        @param[in] model: product_category model

        @return ProductCategory业务对象
        """
        webapp_owner = args['webapp_owner']
        model = args['model']

        product_category = ProductCategory(webapp_owner, model)
        product_category._init_slot_from_model(model)
        product_category.created_at = model.strftime('%Y-%m-%d %H:%M:%S')
        return product_category
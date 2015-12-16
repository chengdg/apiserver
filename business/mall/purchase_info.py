# -*- coding: utf-8 -*-
"""@package business.mall.purchase_info
购买信息

"""

import json
from bs4 import BeautifulSoup
import math
import itertools

from wapi.decorators import param_required
from wapi import wapi_utils
from core.cache import utils as cache_util
from db.mall import models as mall_models
#import resource
from core.watchdog.utils import watchdog_alert
from business import model as business_model 
import settings
import logging


class PurchaseInfo(business_model.Model):
    """
    购买信息
    """
    __slots__ = (
        'product_ids',
        'promotion_ids',
        'product_counts',
        'product_model_names',

        'ship_info',
        'used_pay_interface_type',
        'customer_message',
        'order_type',
        'group2integralinfo',
        'order_integral_info',

        'is_purchase_from_shopping_cart',
        'coupon_id',
        'wzcard_info', # 微众卡信息
    )

    @staticmethod
    @param_required(['request_args'])
    def parse(args):
        """
        解析http请求的参数，创建PurchaseInfo对象

        @return PurchaseInfo对象
        """
        purchase_info = PurchaseInfo(args['request_args'])

        return purchase_info

    def __init__(self, request_args):
        business_model.Model.__init__(self)

        self.__parse(request_args)

    def __str__(self):
        return str(self.to_dict())

    def __parse(self, request_args):
        """解析request参数
        """
        result = self.__get_product_param(request_args)
        self.product_ids = result['product_ids']
        self.promotion_ids = result['promotion_ids']
        self.product_counts = result['product_counts']
        self.product_model_names = result['product_model_names']

        self.__parse_ship_info(request_args)
        self.__parse_pay_interface(request_args)
        self.__parse_custom_message(request_args)
        self.__parse_coupon_id(request_args)
        # 解析微众卡信息
        self.__parse_wzcard_info(request_args)

        self.order_type = request_args.get('order_type', mall_models.PRODUCT_DEFAULT_TYPE)
        self.is_purchase_from_shopping_cart = (request_args.get('is_order_from_shopping_cart', 'false') == 'true')

        self.__parse_integral_info(request_args) 

    def __parse_ship_info(self, request_args):
        """
        解析收货人信息
        """
        if 'ship_name' in request_args:
            self.ship_info = {
                "name": request_args['ship_name'],
                "tel": request_args['ship_tel'],
                "area": request_args['area'],
                "address": request_args['ship_address']
            }
        else:
            self.ship_info = None

    def __parse_wzcard_info(self, request_args):
        """
        解析微众卡信息

        @return 微众卡信息的list        
        """
        card_names = request_args.get('card_name', '').split(',')
        card_passwords = request_args.get('card_pass', '').split(',')
        wzcard_info = []
        if len(card_names) == len(card_passwords):
            # 微众卡卡号和密码数量应该相等
            for i in range(0, len(card_names)):
                if len(card_names[i])>0:
                    wzcard_info.append({
                            "card_name": card_names[i],
                            "card_pass": card_passwords[i],
                        })
        self.wzcard_info = wzcard_info
        logging.info("ProductInfo.wzcard_info: {}".format(self.wzcard_info))

    def __parse_pay_interface(self, request_args):
        """
        解析支付方式
        """
        self.used_pay_interface_type = request_args.get('xa-choseInterfaces', '-1')

    def __parse_custom_message(self, request_args):
        """
        解析用户留言
        """
        self.customer_message = request_args.get('message', '')

    def __parse_coupon_id(self, request_args):
        """
        解析用户留言
        """
        self.coupon_id = request_args.get('coupon_id', '')

    def __get_product_param(self, args):
        """
        获取订单商品id，数量，规格
        供_get_products调用
        """
        if 'redirect_url_query_string' in args:
            query_string = self.__get_query_string_dict_to_str(args['redirect_url_query_string'])
        else:
            query_string = args

        # jz 2015-11-26
        # if 'product_ids' in query_string:
        product_ids = query_string.get('product_ids', None)
        if product_ids:
            product_ids = product_ids.split('_')
        promotion_ids = query_string.get('promotion_ids', None)
        if promotion_ids:
            promotion_ids = promotion_ids.split('_')
        else:
            promotion_ids = [0] * len(product_ids)
        product_counts = query_string.get('product_counts', None)
        if product_counts:
            product_counts = product_counts.split('_')
        product_model_names = query_string.get('product_model_names', None)
        if product_model_names:
            if '$' in product_model_names:
                product_model_names = product_model_names.split('$')
            else:
                product_model_names = product_model_names.split('%24')
        product_promotion_ids = query_string.get('product_promotion_ids', None)
        if product_promotion_ids:
            product_promotion_ids = product_promotion_ids.split('_')
        product_integral_counts = query_string.get('product_integral_counts', None)
        if product_integral_counts:
            product_integral_counts = product_integral_counts.split('_')
        # jz 2015-11-26
        # else:
        #     product_ids = [query_string.get('product_id', None)]
        #     promotion_ids = [query_string.get('promotion_id', None)]
        #     product_counts = [query_string.get('product_count', None)]
        #     product_model_names = [query_string.get('product_model_name', 'standard')]
        #     product_promotion_ids = [query_string.get('product_promotion_id', None)]
        #     product_integral_counts = [query_string.get('product_integral_count', None)]

        return {
            "product_ids": product_ids,
            "promotion_ids": promotion_ids,
            "product_counts": product_counts,
            "product_model_names": product_model_names
        }

    def __get_query_string_dict_to_str(self, str):
        data = dict()
        for item in str.split('&'):
            values = item.split('=')
            data[values[0]] = values[1]
        return data

    def is_purchase_single_product(self):
        """是否购买单个商品

        @return True: 购买单个商品; False: 不是购买单个商品
        """
        if not self.product_ids:
            return False

        if len(self.product_ids) == 1:
            return True
        else:
            return False

    def __parse_integral_info(self, request_args):
        #解析整单积分信息
        order_integral_info = request_args.get('orderIntegralInfo', None)
        if order_integral_info:
            self.order_integral_info = json.loads(order_integral_info)
        else:
            self.order_integral_info = None

        #商品积分应用信息
        group2integralinfo = request_args.get('group2integralinfo', None)
        if group2integralinfo:
            self.group2integralinfo = json.loads(group2integralinfo)
        else:
            self.group2integralinfo = None
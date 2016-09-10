# -*- coding: utf-8 -*-

__author__ = 'bert'

import logging

from util.command import BaseCommand

from eaglet.core.cache import utils as cache_util
from bson import json_util
import json

from commands.service.cache_mall_product_list_service import cache_product_list_service

class Command(BaseCommand):
    help = "python manage.py test_cache_product_list woid category"
    args = ''
    
    def handle(self, woid, category_id, **options):
        cache_product_list_service({
            "woid":woid,
            "category_id":category_id
            })

        result = cache_util.get("w_%s_c_%s" % (woid, category_id))

        logging.info(result)
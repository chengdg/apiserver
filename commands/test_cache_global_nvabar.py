# -*- coding: utf-8 -*-

__author__ = 'bert'

import logging

from util.command import BaseCommand
from eaglet.core.zipkin import zipkin_client

#from eaglet.core.cache import utils as cache_util
from bson import json_util
import json
import settings

zipkin_client.zipkinClient = zipkin_client.ZipkinClient(settings.SERVICE_NAME, 1, 1, 1)

from commands.service.cache_global_navbar_service import cache_global_navbar_service

class Command(BaseCommand):
    help = "python manage.py test_cache_global_nvabar woid "
    args = ''
    
    def handle(self, woid, **options):
        cache_global_navbar_service({
            "woid":woid
            })

        #result = cache_util.get("w_%s_c_%s" % (woid, category_id))

        # logging.info(result)
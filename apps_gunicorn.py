# -*- coding: utf-8 -*-

import json
#import logging
#import uuid
from wsgiref import simple_server

import falcon
#import requests

from core import api_resource
from core.exceptionutil import unicode_full_stack

import wapi.urls
import wapi as wapi_resource
from apps import FalconResource, ThingsResource

falcon_app = falcon.API()

# 注册到Falcon
falcon_app.add_route('/wapi/{app}/{resource}/', FalconResource())

things = ThingsResource()
falcon_app.add_route('/things', things)

# -*- coding: utf-8 -*-

import os
#import sys
#import upyun
#import time

#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weapp.settings")

import wapi.urls
import wapi as resource

product = resource.get('mall', 'product', {
	"id": 9
})
print '=====> product <====='
print product

promotions = resource.get('mall', 'promotions', {})
print '\n=====> promotion <====='
print promotions

print '\n=====> exception <====='
product = resource.get('mall', 'product', {
	
})

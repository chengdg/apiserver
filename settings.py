# -*- coding: utf-8 -*-

import os

DEBUG = True
PROJECT_HOME = os.path.dirname(os.path.abspath(__file__))

MODE = 'develop'

DATABASES = {
    'default': {
        'ENGINE': 'mysql',
        'NAME': 'weapp',
        'USER': 'weapp',                      # Not used with sqlite3.
        'PASSWORD': 'weizoom',                  # Not used with sqlite3.
        'HOST': 'db.weapp.com',
        'PORT': '',
        'CONN_MAX_AGE': 100
    }
}


MIDDLEWARES = [
    'middleware.core_middleware.ApiAuthMiddleware',
    'middleware.debug_middleware.SqlMonitorMiddleware',
	'middleware.debug_middleware.RedisMiddleware'
]

# settings for WAPI Logger
if MODE == 'develop':
    WAPI_LOGGER_ENABLED = True
    WAPI_LOGGER_SERVER_HOST = 'mongo.weapp.com'
    WAPI_LOGGER_SERVER_PORT = 27017
    WAPI_LOGGER_DB = 'wapi'
    IMAGE_HOST = 'http://dev.weapp.com'
else:
    # 真实环境暂时关闭
    #WAPI_LOGGER_ENABLED = False
    WAPI_LOGGER_ENABLED = True
    WAPI_LOGGER_SERVER_HOST = 'mongo.weapp.com'
    WAPI_LOGGER_SERVER_PORT = 27017
    WAPI_LOGGER_DB = 'wapi'
    IMAGE_HOST = 'http://dev.weapp.com'


#缓存相关配置
REDIS_HOST = 'redis.weapp.com'
REDIS_PORT = 6379
REDIS_CACHES_DB = 1

#BDD相关配置
WEAPP_DIR = '../weapp'
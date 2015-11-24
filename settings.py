# -*- coding: utf-8 -*-

import os

DEBUG = True
PROJECT_HOME = os.path.dirname(os.path.abspath(__file__))

MODE = 'develop'

DATABASES = {
    'default': {
        'ENGINE': 'mysql+retry',
        'NAME': 'weapp',
        'USER': 'weapp',                      # Not used with sqlite3.
        'PASSWORD': 'weizoom',                  # Not used with sqlite3.
        'HOST': 'db.weapp.com',
        'PORT': '',
        'CONN_MAX_AGE': 100
    },
    'watchdog': {
        'ENGINE': 'mysql+retry',
        'NAME': 'weapp',
        'USER': 'weapp',                      # Not used with sqlite3.
        'PASSWORD': 'weizoom',                  # Not used with sqlite3.
        'HOST': 'db.operation.com',
        'PORT': '',
        'CONN_MAX_AGE': 100
    }
}


MIDDLEWARES = [
    'middleware.core_middleware.ApiAuthMiddleware',
    
    'middleware.debug_middleware.SqlMonitorMiddleware',
    'middleware.debug_middleware.RedisMiddleware',

    #账号信息中间件
    'middleware.account_middleware.WebAppOwnerMiddleware',
	'middleware.account_middleware.AccountsMiddleware'
]
#sevice celery 相关
EVENT_DISPATCHER = 'redis'

# settings for WAPI Logger
if MODE == 'develop':
    WAPI_LOGGER_ENABLED = True
    WAPI_LOGGER_SERVER_HOST = 'mongo.weapp.com'
    WAPI_LOGGER_SERVER_PORT = 27017
    WAPI_LOGGER_DB = 'wapi'
    IMAGE_HOST = 'http://dev.weapp.com'
    PAY_HOST = 'api.weapp.com'
    #sevice celery 相关
    EVENT_DISPATCHER = 'local'
    ENABLE_SQL_LOG = False
else:
    # 真实环境暂时关闭
    #WAPI_LOGGER_ENABLED = False
    WAPI_LOGGER_ENABLED = True
    WAPI_LOGGER_SERVER_HOST = 'mongo.weapp.com'
    WAPI_LOGGER_SERVER_PORT = 27017
    WAPI_LOGGER_DB = 'wapi'
    IMAGE_HOST = 'http://dev.weapp.com'
    PAY_HOST = 'api.weapp.com'
    ENABLE_SQL_LOG = False


#缓存相关配置
REDIS_HOST = 'redis.weapp.com'
REDIS_PORT = 6379
REDIS_CACHES_DB = 2

#BDD相关配置
WEAPP_DIR = '../weapp'
WEAPP_BDD_SERVER_HOST = '127.0.0.1'
WEAPP_BDD_SERVER_PORT = 8170
ENABLE_BDD_DUMP_RESPONSE = True

#watchdog相关
WATCH_DOG_DEVICE = 'mysql'
WATCH_DOG_LEVEL = 200
IS_UNDER_BDD = False
# 是否开启TaskQueue(基于Celery)
TASKQUEUE_ENABLED = True


INSTALLED_TASKS = [
    # Celery for Falcon
    'resource.member.tasks',
    'core.watchdog.tasks',
    'services.example_service.tasks.example_log_service'
    ]

#redis celery相关
REDIS_SERVICE_DB = 2
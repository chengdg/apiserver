# -*- coding: utf-8 -*-
#coding:utf8
from __future__ import absolute_import

import os
import sys
import logging

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_DIR)
from celery import Celery
from celery.utils.log import get_logger
import settings

logging.info("init celery")
app = Celery('apiserver')
logging.info("loaded `celeryconfig`")
app.config_from_object('core.celery.celeryconfig')
app.autodiscover_tasks(lambda: settings.INSTALLED_TASKS)

celery_app  = app
task = celery_task = app.task

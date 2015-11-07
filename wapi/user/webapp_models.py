#coding: utf8

import datetime

from db import models
from models import User


class WebApp(models.Model):
	"""
	webapp
	"""
	owner = models.ForeignKey(User)
	appid = models.CharField(max_length=16)
	name = models.CharField(max_length=100, default='')

	class Meta(object):
		db_table = 'webapp'
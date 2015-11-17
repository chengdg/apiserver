# -*- coding: utf-8 -*-

__author__ = 'bert'

from apiserver.celery import task

@task
def add(x):
	print '>>>>>>>>>>>>>>>tasks', x
	return x
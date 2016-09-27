# -*- coding: utf-8 -*-

__author__ = 'bert'

from bdem import msgutil


def send_mns_message(topic_name, message_name, data):
	print ">>>>>>>>>>>>>.11111,",topic_name,message_name,data
	msgutil.send_message(topic_name, message_name, data)
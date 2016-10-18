# -*- coding: utf-8 -*-

__author__ = 'bert'

from bdem import msgutil
from eaglet.core import watchdog

def send_mns_message(topic_name, message_name, data):
	msgutil.send_message(topic_name, message_name, data)

	message = u"send_mns_message, topic_name:{}, message_name:{}, data:{}".format(topic_name, message_name, data)
	watchdog.info(message)
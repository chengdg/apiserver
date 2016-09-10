# -*- coding: utf-8 -*-
"""
基于MNS的创建service runner

启动之后，不断轮询队列

@author bert
"""

from eaglet.utils.command import BaseCommand

import json

import settings

from eaglet.core.exceptionutil import unicode_full_stack
from eaglet.core import watchdog
import logging

from mns.account import Account
from mns.queue import *
from mns.topic import *
from mns.subscription import *

import time
import service  # load all services
import service_register




WAIT_SECONDS = 10
SLEEP_SECONDS = 10

class Command(BaseCommand):
	help = "python manage.py customer_create_service"
	args = ''

	# topic-queue模型中的queue

	def handle(self, *args, **options):
		global _SERVICE_LIST

		# 准备访问MNS
		self.mns_account = Account(\
			settings.MNS_ENDPOINT, \
			settings.MNS_ACCESS_KEY_ID, \
			settings.MNS_ACCESS_KEY_SECRET, \
			settings.MNS_SECURITY_TOKEN)

		queue = self.mns_account.get_queue(settings.SUBSCRIBE_QUEUE_NAME)
		watchdog.info(server_name=settings.SERVICE_NAME,'queue: {}'.format(queue.get_attributes().queue_name))

		# TODO: 改成LongPoll更好
		while True:
			#读取消息
			try:
				recv_msg = queue.receive_message(WAIT_SECONDS)
				watchdog.info(server_name=settings.SERVICE_NAME,"Receive Message Succeed! ReceiptHandle:%s MessageBody:%s MessageID:%s" % (recv_msg.receipt_handle, recv_msg.message_body, recv_msg.message_id))

				# 处理消息(consume)
				data = json.loads(recv_msg.message_body)
				function_name = data['function']
				func = service_register.SERVICE_LIST.get(function_name)
				if func:
					try:
						response = func(data['args'], recv_msg)
						watchdog.info(server_name=settings.SERVICE_NAME,"service response: {}".format(response))
					except:
						watchdog.info(server_name=settings.SERVICE_NAME,u"Service Exception: {}".format(unicode_full_stack()))
				else:
					watchdog.info(server_name=settings.SERVICE_NAME,u"Error: no such service found : {}".format(function_name))

			except MNSExceptionBase as e:
				if e.type == "QueueNotExist":
					watchdog.debug(server_name=settings.SERVICE_NAME, "Queue not exist, please create queue before receive message.")
					break
				elif e.type == "MessageNotExist":
					watchdog.debug("Queue is empty! Waiting...",server_name=settings.SERVICE_NAME)
				else:
					watchdog.debug("Receive Message Fail! Exception:%s\n" % e,server_name=settings.SERVICE_NAME)
				time.sleep(SLEEP_SECONDS)
				continue
			except Exception as e:
				print u"Exception: {}".format(unicode_full_stack())

			#删除消息
			try:
				queue.delete_message(recv_msg.receipt_handle)
				logging.debug("Delete Message Succeed!  ReceiptHandle:%s" % recv_msg.receipt_handle)
			except MNSException,e:
				logging.debug("Delete Message Fail! Exception:%s\n" % e)
		return

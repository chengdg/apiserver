# coding: utf8
"""
测试批量发任务消息

执行：
	
	python test_multi_tasks.py
	
"""
#import os
#import sys
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weapp.settings')
#WEAPP_DIR = os.path.abspath(os.path.join(os.getcwd(), '.'))
#print("WEAPP_DIR: %s" % WEAPP_DIR)
#sys.path.insert(0, WEAPP_DIR)
#for path in sys.path:	print path

import time

from weapp import settings

from watchdog.tasks import send_watchdog

MAX_TRY = 500
result_map = dict()
state_map = dict()

def to_key(index):
	return "name_%d" % index


#from celery import Celery
#app = Celery('weapp')
#app.config_from_object('django.conf:settings')


def test_multi_tasks():
	from time import clock
	start = clock()
	for i in range(0, MAX_TRY):
		r = send_watchdog.delay(200, "message: %s" % to_key(i))
		result_map[i] = r
	end = clock()
	print("started %d tasks, consumed: %.3f ms" % (MAX_TRY, (end-start)))

	checked = 0
	for j in range(0, 100):
		for i in range(0, MAX_TRY):
			r = result_map[i]
			if not state_map.has_key(i) and r.state == 'SUCCESS':
				try:
					state_map[i] = r.get(timeout=1)
					print("%d is OK" % i)
					checked+=1
				except:
					print("Timeout exception.")
		print("round #%d checking finished: checked=%d" % (j+1, checked))
		if checked>=MAX_TRY:
			break
		print("sleep for a while")
		time.sleep(10) # 10s

	verified = 0
	for k,v in state_map.items():
		#print("%d\t%s" % (k,v))
		#if to_key(k) == v:
		if v == 'OK':
			verified+=1
		else:
			print("incorrect result: k=%d, v=%s" % (k, v))

	print("started %d tasks, consumed: %.3f s, %.3f ms/call" % (MAX_TRY, (end-start), (end-start)*1000.0/MAX_TRY))
	print("sent: %d, received: %d, verified results: %d" % (MAX_TRY, checked, verified))

if __name__=="__main__":
	test_multi_tasks()

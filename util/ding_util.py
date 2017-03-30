# -*- coding: utf-8 -*-
import json, requests
from eaglet.core import watchdog

DEFAULT_DING_TOKEN = u'a4e49e51809a3cff074d4f30247a03cd9485e5fb4cc1df157f0edecc0908069d'  #测试群的token

def send_message_to_ding(msg, token=DEFAULT_DING_TOKEN, at_mobiles=[], is_at_all=False):
	"""
	发送钉钉报警信息
	"""
	webhook = u'https://oapi.dingtalk.com/robot/send?access_token=%s' % token
	text = {
			"msgtype": "text", 
				"text": {
				"content": msg
			}, 
			"at": {
				"atMobiles": [], 
				"isAtAll": 'false'
			}
		}

	if is_at_all:
		text["at"]["isAtAll"] = "true"
	elif len(at_mobiles) > 0:
		text["at"]["atMobiles"] = at_mobiles

	watchdog.info('send msg: %s' % text)
	response = requests.post(webhook, json=text)

	result = json.loads(response.text)
	if result['errmsg'] == u'ok':
		return True

	return False
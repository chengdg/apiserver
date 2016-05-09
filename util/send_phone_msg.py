# -*- coding: utf-8 -*-

__author__ = 'bert'

import sys
import random
import string
import urllib
from BeautifulSoup import BeautifulSoup

from core.exceptionutil import unicode_full_stack
from eaglet.core import watchdog

URL = "http://www.mxtong.net.cn/GateWay/Services.asmx/DirectSend?%s"
USER_ID = 963921
ACCOUNT = "admin"
PASSWORD = "4MSCFX" 
SUCESS = 'Sucess'
#===============================================================================
# send_phone_captcha : 使用麦讯短信平台发送短信 phones = 1;2;3;2;
#===============================================================================
def send_phone_captcha(phones, content, send_time='', sent_type=1, post_fix_number='', account=ACCOUNT, password=PASSWORD, user_id=USER_ID):
	params = urllib.urlencode({
		'UserID': user_id, 
		'Account': account, 
		'Password': password, 
		'Phones': phones, 
		'Content': content.encode("utf-8"), 
		'SendTime':send_time,
		'SendType': sent_type, 
		'PostFixNumber': post_fix_number
		})

	try:
		response = urllib.urlopen(URL % params)
		soup = BeautifulSoup(response.read())
		if soup.retcode.text == SUCESS:
			return True
		else:
			return False
	except:
		notify_msg = u"发送手机验证码异常:cause:\n{}".format(unicode_full_stack())
		watchdog.alert(notify_msg)
		return False




def send_captcha(phone_number, company_name=u'微众传媒'):
	"""
		send_phone_msg: 发送手机验证码
	"""
	MSG_CONTENT = u"您的验证码为[%s]，请不要泄露给任何人【%s】"
	captcha = ''.join(random.sample(string.digits, 4))
	content = MSG_CONTENT % (captcha, company_name)
	#result = True
	result = send_phone_captcha(phone_number, content)
	return result,captcha
# -*- coding: utf-8 -*-
import json, requests

from eaglet.core import watchdog
from util import ding_util
from util import jinge_rsa_util
import settings

JINGE_HOST = settings.JINGE_HOST  #锦歌饭卡的第三方支付公司host
DING_TOKEN = '43b4b5204686a4a09fbdec8acedcd90db0d1f12851a3c6a3935b6c7d7c08bbf2'  #支付报警群
AT_MOBILES = ['13718183044']

def get_card_info_by_phone(phone_number):
	"""
	根据手机号获取用户的饭卡卡号和token
	"""
	url = JINGE_HOST + 'checkPhone.json'
	params = {'phone': phone_number}
	resp = requests.post(url, data=params)

	if resp.status_code == 200:
		try:
			json_data = json.loads(resp.text)
			if json_data['ret'] == 1:
				watchdog.info('get_card_info_by_phone success requests: %s, params: %s, results: %s' % (url, params, json_data))
				return {
					'card_number': json_data['cardNo'],
					'token': json_data['token'],
					'name': json_data['vipName'],  #员工姓名
					'company': json_data['merName'],  #公司名称
					'mer_id': json_data['merId'],  #商户号
					'term_id': json_data['termId']  #终端号
				}, ''
			else:
				return None, json_data['tip']
				watchdog.alert('get_card_info_by_phone fail requests: %s, params: %s, resp: %s' % (url, params, resp.content))
		except Exception, e:
			watchdog.alert('get_card_info_by_phone fail requests: %s, params: %s, resp: %s, Exception: %s' % (url, params, resp.content, e))
	else:
		watchdog.alert('get_card_info_by_phone fail requests: %s, params: %s, resp: %s' % (url, params, resp.content))
	
	return None, None


def set_password(card_number, token, password):
	"""
	首次设置支付密码
	"""
	url = JINGE_HOST + 'setPass.json'
	try:
		card_number = card_number.encode('utf-8')
		token = token.encode('utf-8')
	except:
		pass
	params = {
		'cardNo': card_number,
		'token': token,
		'newPass': password
	}
	resp = requests.post(url, data=params)

	if resp.status_code == 200:
		try:
			json_data = json.loads(resp.text)
			if json_data['ret'] == 1:
				watchdog.info('set password success requests: %s, params: %s, results: %s' % (url, params, json_data))
				return True
			else:
				watchdog.alert('set password fail requests: %s, params: %s, resp: %s' % (url, params, resp.content))
		except Exception, e:
			watchdog.alert('set password fail requests: %s, params: %s, resp: %s, Exception: %s' % (url, params, resp.content, e))
	else:
		watchdog.alert('set password fail requests: %s, params: %s, resp: %s' % (url, params, resp.content))
	
	return False


def get_balance(card_number, token):
	"""
	查询余额
	"""
	url = JINGE_HOST + 'qurBalance.json'
	params = {
		'cardNo': card_number,
		'token': token
	}
	resp = requests.post(url, data=params)

	if resp.status_code == 200:
		try:
			json_data = json.loads(resp.text)
			if json_data['ret'] == 1:
				watchdog.info('get balance success requests: %s, params: %s, results: %s' % (url, params, json_data))
				return json_data['balance']
			else:
				watchdog.alert('get balance fail requests: %s, params: %s, resp: %s' % (url, params, resp.content))
		except Exception, e:
			watchdog.alert('get balance fail requests: %s, params: %s, resp: %s, Exception: %s' % (url, params, resp.content, e))
	else:
		watchdog.alert('get balance fail requests: %s, params: %s, resp: %s' % (url, params, resp.content))
	
	return None


def refund(card_number, card_password, token, trade_id, order_id, price):
	"""
	退款
	"""
	url = JINGE_HOST + 'getRefund.json'
	try:
		card_number = card_number.encode('utf-8')
		token = token.encode('utf-8')
		card_password = card_password.encode('utf-8')
		trade_id = trade_id.encode('utf-8')
	except:
		pass
	params = {
		'cardNo': card_number,
		'password': card_password,
		'token': token,
		'tradeId': trade_id
	}
	resp = requests.post(url, data=params)

	if resp.status_code == 200:
		try:
			json_data = json.loads(resp.text)
			if json_data['ret'] == 1:
				watchdog.info('jinge_card refund success requests: %s, params: %s, results: %s' % (url, params, json_data))
				trade_amount = json_data['tradeAmount']
				refund_trade_id = json_data['tradeId']
				if trade_amount != price:
					#如果退款的金额跟消费的金额不一致就往钉钉群里发报警消息
					msg = u'锦歌饭卡退款金额与消费金额不一致,\n请求退款金额: {}\n实际退款金额: {}\norder_id: {}\ncard_number: {}\ntrade_id: {}\nrefund_trade_id: {}'.format(
						price,
						trade_amount,
						order_id,
						card_number,
						trade_id,
						refund_trade_id
					)
					ding_util.send_message_to_ding(msg, token=DING_TOKEN, at_mobiles=AT_MOBILES)
				return True, refund_trade_id, trade_amount
			else:
				watchdog.alert('jinge_card refund fail requests: %s, params: %s, resp: %s' % (url, params, resp.content))
		except Exception, e:
			watchdog.alert('jinge_card refund fail requests: %s, params: %s, resp: %s, Exception: %s' % (url, params, resp.content, e))
	else:
		watchdog.alert('jinge_card refund fail requests: %s, params: %s, resp: %s' % (url, params, resp.content))

	msg = u'锦歌饭卡退款失败\n消费金额: {}\norder_id: {}\ncard_number: {}'.format(price, order_id, card_number)
	ding_util.send_message_to_ding(msg, token=DING_TOKEN, at_mobiles=AT_MOBILES)
	
	return False, None, None


def pay(card_number, card_password, token, money, mer_id, term_id, trade_time):
	"""
	支付
	"""
	url = JINGE_HOST + 'cardPay.json'
	params = {
		'cardNo': card_number,
		'token': token,
		'merId': mer_id,  #商户号
		'termId': term_id,  #终端号
		'money': money,
		'password': card_password,
		'tradeTime': trade_time,  #交易时间
	}
	resp = requests.post(url, data=params)
	
	if resp.status_code == 200:
		try:
			json_data = json.loads(resp.text)
			if json_data['ret'] == 1:
				watchdog.info('jinge_card pay success requests: %s, params: %s, results: %s' % (url, params, json_data))
				trade_id = json_data['tradeId']
				return True, trade_id
			else:
				watchdog.alert('jinge_card pay requests: %s, params: %s, resp: %s' % (url, params, resp.content))
		except Exception, e:
			watchdog.alert('jinge_card pay fail requests: %s, params: %s, resp: %s, Exception: %s' % (url, params, resp.content, e))
	else:
		watchdog.alert('jinge_card pay requests: %s, params: %s, resp: %s' % (url, params, resp.content))
	
	return False, None

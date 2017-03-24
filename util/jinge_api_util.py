# -*- coding: utf-8 -*-
import json, requests

from eaglet.core import watchdog

JINGE_HOST = 'http://101.200.142.53:8088/wxPay/'  #锦歌饭卡的第三方支付公司host

def get_card_info_by_phone(phone_number):
	"""
	根据手机号获取用户的饭卡卡号和token
	"""
	url = JINGE_HOST + 'checkPhone.json'
	params = {'phone': phone_number}
	resp = requests.post(url, data=params)

	if resp.status_code == 200:
		json_data = json.loads(resp.text)
		watchdog.info('success requests: %s, params: %s, results: %s' % (url, params, json_data))

		if json_data['ret'] == 1:
			return {
				'card_number': json_data['cardNo'],
				'token': json_data['token']
			}
	else:
		watchdog.alert('fail requests: %s, params: %s, resp: %s' % (url, params, resp.text))
	
	return None


def set_password(card_number, token, password):
	"""
	首次设置支付密码
	"""
	url = JINGE_HOST + 'setPass.json'
	params = {
		'cardNo': card_number,
		'token': token,
		'newPass': password
	}
	resp = requests.post(url, data=params)

	if resp.status_code == 200:
		json_data = json.loads(resp.text)
		watchdog.info('success requests: %s, params: %s, results: %s' % (url, params, json_data))

		if json_data['ret'] == 1:
			return True
	else:
		watchdog.alert('fail requests: %s, params: %s, resp: %s' % (url, params, resp.text))
	
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
		json_data = json.loads(resp.text)
		watchdog.info('success requests: %s, params: %s, results: %s' % (url, params, json_data))

		if json_data['ret'] == 1:
			return json_data['balance']
	else:
		watchdog.alert('fail requests: %s, params: %s, resp: %s' % (url, params, resp.text))
	
	return None


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
		json_data = json.loads(resp.text)
		watchdog.info('success requests: %s, params: %s, results: %s' % (url, params, json_data))

		if json_data['ret'] == 1:
			return json_data['balance']
	else:
		watchdog.alert('fail requests: %s, params: %s, resp: %s' % (url, params, resp.text))
	
	return None


def refund():
	"""
	退款
	"""
	return True


def pay(card_number, card_password, token, money, trade_time):
	"""
	支付
	"""
	# return is_success, reason, trade_id
	return True, '', '1111111'
# -*- coding: utf-8 -*-

from utils import msg_crypt
import settings

crypt = msg_crypt.MsgCrypt(settings.CTYPT_INFO['token'], settings.CTYPT_INFO['encodingAESKey'], settings.CTYPT_INFO['id'])
def encrypt_access_token(user_id, openid='notopenid'):
	if not user_id:
		raise 'error user_id'

	# crypt = msg_crypt.MsgCrypt(settings.CTYPT_INFO['token'], settings.CTYPT_INFO['encodingAESKey'], settings.CTYPT_INFO['id'])
	access_token_str = str(user_id) + '_weizoom_' + openid

	encrypt_msg = crypt.EncryptMsg(access_token_str)
	x = crypt.DecryptMsg(encrypt_msg)
	print '____________________xx',x
	return encrypt_msg


def decrypt_access_token(msg):
	result,access_token = crypt.DecryptMsg(msg)
	if not result:
		raise 'error access_token'
	return access_token

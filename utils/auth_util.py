# -*- coding: utf-8 -*-
"""@package utils.auth_utils
	access_token 加密解密工具
"""

from utils import msg_crypt
import settings

crypt = msg_crypt.MsgCrypt(settings.CTYPT_INFO['token'], settings.CTYPT_INFO['encodingAESKey'], settings.CTYPT_INFO['id'])

def encrypt_access_token(webapp_owner_id, openid='notopenid'):
	"""
	使用msg_crypt加密包对由 user和openid组成的webapp_owner_id_weizoom_openid(eg：12_weizoom_xxxxxxxxxxx)字符串进行加密
	
	@param webapp_owner_id
	@param openid
	"""
	if not webapp_owner_id:
		raise ValueError('error webapp_owner_id')
	access_token_str = str(webapp_owner_id) + '_weizoom_' + openid
	encrypt_msg = crypt.EncryptMsg(access_token_str)
	return encrypt_msg


def decrypt_access_token(msg):
	"""
	使用msg_crypt加解密包对msg解密
	
	@param msg 待解密字符串
	"""
	result,access_token = crypt.DecryptMsg(msg)
	if not result:
		raise ValueError('error access_token')
	return access_token

# -*- coding: utf-8 -*-
"""@package utils.auth_utils
	access_token 加密揭秘工具
"""

from utils import msg_crypt
import settings

crypt = msg_crypt.MsgCrypt(settings.CTYPT_INFO['token'], settings.CTYPT_INFO['encodingAESKey'], settings.CTYPT_INFO['id'])

def encrypt_access_token(user_id, openid='notopenid'):
	"""
	使用msg_crypt加密包对由 user和openid组成的user_id_weizoom_openid(eg：12_weizoom_xxxxxxxxxxx)字符串进行加密
	
	@param user_id
	@param openid
	"""
	if not user_id:
		raise 'error user_id'
	access_token_str = str(user_id) + '_weizoom_' + openid
	encrypt_msg = crypt.EncryptMsg(access_token_str)
	x = crypt.DecryptMsg(encrypt_msg)
	return encrypt_msg


def decrypt_access_token(msg):
	"""
	使用msg_crypt加解密包对msg解密
	
	@param msg 待解密字符串
	"""
	
	result,access_token = crypt.DecryptMsg(msg)
	if not result:
		raise 'error access_token'
	return access_token

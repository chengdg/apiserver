# -*- coding: utf-8 -*-
"""@package utils.auth_utils
	access_token 加密解密工具
"""
import urllib
from utils import msg_crypt
import settings

crypt = msg_crypt.MsgCrypt(settings.CTYPT_INFO['token'], settings.CTYPT_INFO['encodingAESKey'], settings.CTYPT_INFO['id'])

def encrypt_access_token(woid, openid='notopenid'):
	"""
	使用msg_crypt加密包对由woid和openid组成的woid_weizoom_openid(eg：12_weizoom_xxxxxxxxxxx)字符串进行加密
	
	@param woid
	@param openid
	"""
	if not woid:
		raise ValueError('error woid')
	access_token_str = str(woid) + '_weizoom_' + openid
	encrypt_msg = crypt.EncryptMsg(access_token_str)
	encrypt_msg = urllib.quote(encrypt_msg)
	return encrypt_msg


def decrypt_access_token(msg):
	"""
	使用msg_crypt加解密包对msg解密
	
	@param msg 待解密字符串
	"""
	msg = urllib.unquote(msg)
	result,access_token = crypt.DecryptMsg(msg)
	if not result:
		raise ValueError('error access_token')
	return access_token

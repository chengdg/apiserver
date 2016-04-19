#!/usr/bin/env python
#-*- encoding:utf-8 -*-

""" 对公众平台发送给公众账号的消息加解密示例代码.
@copyright: Copyright (c) 1998-2014 Tencent Inc.

"""
# ------------------------------------------------------------------------

import base64
import string
import random
import hashlib
import time
import struct
from Crypto.Cipher import AES
import xml.etree.cElementTree as ET
import sys
import socket

reload(sys)
sys.setdefaultencoding('utf-8')

"""
关于Crypto.Cipher模块，ImportError: No module named 'Crypto'解决方案
请到官方网站 https://www.dlitz.net/software/pycrypto/ 下载pycrypto。
下载后，按照README中的“Installation”小节的提示进行pycrypto安装。
"""
class FormatException(Exception):
	pass

def throw_exception(message, exception_class=FormatException):
	"""my define raise exception function"""
	raise exception_class(message)

class PKCS7Encoder():
	"""提供基于PKCS7算法的加解密接口"""

	block_size = 32
	def encode(self, text):
		""" 对需要加密的明文进行填充补位
		@param text: 需要进行填充补位操作的明文
		@return: 补齐明文字符串
		"""
		text_length = len(text)
		# 计算需要填充的位数
		amount_to_pad = self.block_size - (text_length % self.block_size)
		if amount_to_pad == 0:
			amount_to_pad = self.block_size
		# 获得补位所用的字符
		pad = chr(amount_to_pad)
		return text + pad * amount_to_pad

	def decode(self, decrypted):
		"""删除解密后明文的补位字符
		@param decrypted: 解密后的明文
		@return: 删除补位字符后的明文
		"""
		pad = ord(decrypted[-1])
		if pad<1 or pad >32:
			pad = 0
		return decrypted[:-pad]

class Prpcrypt(object):

	def __init__(self, key):
		self.key = key
		# 设置加解密模式为AES的CBC模式
		self.mode = AES.MODE_CBC

	def encrypt(self, text, id):
		"""对明文进行加密
		@param text: 需要加密的明文
		@return: 加密得到的字符串
		"""
		# 16位随机字符串添加到明文开头
		text = self.get_random_str() + struct.pack("I",socket.htonl(len(text))) + text + id.encode('utf-8')
		# 使用自定义的填充方式对明文进行补位填充
		pkcs7 = PKCS7Encoder()
		text = pkcs7.encode(text)
		# 加密
		cryptor = AES.new(self.key,self.mode,self.key[:16])
		ciphertext = cryptor.encrypt(text)
		return base64.b64encode(ciphertext)

	def decrypt(self, text, id):
		"""对解密后的明文进行补位删除
		@param text: 密文
		@return: 删除填充补位后的明文
		"""		
		#try:
		cryptor = AES.new(self.key,self.mode,self.key[:16])
		# 使用BASE64对密文进行解码，然后AES-CBC解密
		plain_text  = cryptor.decrypt(base64.b64decode(text))
		pad = ord(plain_text[-1])
		# 去掉补位字符串
		#pkcs7 = PKCS7Encoder()
		#plain_text = pkcs7.encode(plain_text)
		# 去除16位随机字符串
		content = plain_text[16:-pad]
		msg_len = socket.ntohl(struct.unpack("I",content[ : 4])[0])
		mes_content = content[4 : msg_len+4]
		from_id = content[msg_len+4:]

		if from_id != id:
			return False, 'error param'
		return True, mes_content
		# except Exception, e:
		# 	raise e

	def get_random_str(self):
		""" 随机生成16位字符串
		@return: 16位字符串
		"""
		rule = string.letters + string.digits
		str = random.sample(rule, 16)
		return "".join(str)


class MsgCrypt(object):

	def __init__(self, token, AESkey, id):
		try:
			self.key = base64.b64decode(AESkey+"=")
		except:
			throw_exception("[error]: EncodingAESKey unvalid !", FormatException)

		self.token = token
		self.id = id

	def EncryptMsg(self, text):
		pc = Prpcrypt(self.key)
		encrypt = pc.encrypt(text, self.id)
		return encrypt

	def DecryptMsg(self, encrypt):
		pc = Prpcrypt(self.key)
		ret,content = pc.decrypt(encrypt,self.id)
		return ret, content



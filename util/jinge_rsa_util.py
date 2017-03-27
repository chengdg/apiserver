# -*- coding: utf-8 -*-
from Crypto import Random
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA
import base64

"""
pem文件生成方式见RSAJavaKeyFileGenerator.java
"""
def encrypt(text):
	try:
		text = text.encode('utf-8')
	except:
		pass
	print text,type(text)
	with open('util/jinge_public_key.pem') as f:
		key = f.read()
		rsakey = RSA.importKey(key)
		cipher = Cipher_pkcs1_v1_5.new(rsakey)
		encrypt_text = base64.b64encode(cipher.encrypt(text))
		return encrypt_text
	return ''

def decrypt(text):
	try:
		text = text.encode('utf-8')
	except:
		pass
	random_generator = Random.new().read
	with open('util/jinge_private_key.pem') as f:
		key = f.read()
		rsakey = RSA.importKey(key)
		cipher = Cipher_pkcs1_v1_5.new(rsakey)
		decrypt_text = cipher.decrypt(base64.b64decode(text), random_generator)
		return decrypt_text
	return ''
# -*- coding: utf-8 -*-

import re


def filter_invalid_str(text,to_str=u'_'):
	"""
	MySQL utf字符集能存储3个自己的字符,过滤掉4字节字符
	@param text
	@param to_str 过滤成的字符
	@return 4字节字符过滤为'_'
	"""
	# 版本4：
	try:
		# UCS-4
		highpoints = re.compile(u'[\U00010000-\U0010ffff]')
	except re.error:
		# UCS-2
		highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')

	return highpoints.sub(to_str, text)


	# 版本3：简化版本2所得，然而并没有什么用，UCS-2下好好一个字符，怎么就被识别成了两个了呢？
	# return ''.join(map(lambda x: x if u'\u0000' < x < u'\uFFFF' else '_', text))

	# 版本2：反正也不能用
	# result = ''
	# for i in text:
	#     if u'\u0000' < i < u'\uFFFF':
	#         result += i
	#     else:
	#         result += '_'
	# return result



	# 版本1：莫名的不好用
	# def filter_invalid_str(text):
	#
	#         return re.sub(r'[^\u0000-\uFFFD]+', '_', text)



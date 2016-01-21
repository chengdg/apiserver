# -*- coding: utf-8 -*-


def filter_invalid_str(text):
	"""
	MySQL utf字符集能存储3个自己的字符，范围为(\u0000-\uFFFF)
	@param text:
	@return:
	"""
	return ''.join(map(lambda x: x if u'\u0000' < x < u'\uFFFF' else '_', text))

	# result = ''
    # for i in text:
    #     if u'\u0000' < i < u'\uFFFF':
    #         result += i
    #     else:
    #         result += '_'
    # return result

# def filter_invalid_str(text):
#
#         return re.sub(r'[^\u0000-\uFFFD]+', '_', text)
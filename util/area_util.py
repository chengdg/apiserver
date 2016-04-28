# -*- coding: utf-8 -*-

ID2PROVINCE = {
	1: u'北京',
	2: u'天津',
	3: u'河北',
	4: u'山西',
	5: u'内蒙古',
	6: u'辽宁',
	7: u'吉林',
	8: u'黑龙江',
	9: u'上海',
	10: u'江苏',
	11: u'浙江',
	12: u'安徽',
	13: u'福建',
	14: u'江西',
	15: u'山东',
	16: u'河南',
	17: u'湖北',
	18: u'湖南',
	19: u'广东',
	20: u'广西',
	21: u'海南',
	22: u'重庆',
	23: u'四川',
	24: u'贵州',
	25: u'云南',
	26: u'西藏',
	27: u'陕西',
	28: u'甘肃',
	29: u'青海',
	30: u'宁夏',
	31: u'新疆',
	32: u'香港',
	33: u'澳门',
	34: u'台湾'
}

def get_province_by_id(id):
	return ID2PROVINCE.get(int(id), '')

def get_provinces_by_ids(ids):
	provinces = []
	for id in ids:
		if id:
			provinces.append(ID2PROVINCE.get(int(id), ''))

	return provinces
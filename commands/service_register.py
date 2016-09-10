#coding: utf8

import logging

SERVICE_LIST = {
}


def register(function_name):
	#global _SERVICE_LIST
	def wrapper(function):
		SERVICE_LIST[function_name] = function
		logging.info("registered service: {} => {}".format(function_name, function))
		return function
	return wrapper

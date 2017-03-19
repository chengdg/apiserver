# coding:utf8
# bdd server相关的step

import sys
import json
import os

INITIAL_PORT = 18001

PORT_FILE_PATH = None
def read_service_to_port_info():
	"""
	获得../__bdd_port文件中存储的<service, port>对
	"""
	cur_path = os.path.abspath('.')
	if not 'microservice' in cur_path:
		print '[ERROR] You must run this in dir like ".../microservice/${service}", but now the dir is %s' % cur_path
		sys.exit(1)

	items = cur_path.split('/microservice/')
	global PORT_FILE_PATH
	PORT_FILE_PATH = '%s/microservice/__bdd_port' % items[0]

	service2port = {}
	if os.path.exists(PORT_FILE_PATH):
		with open(PORT_FILE_PATH, 'rb') as f:
			service2port = json.loads(f.read())

	return service2port

def get_current_service_name():
	"""
	获得当前service的name
	"""
	with open('./service.json', 'rb') as f:
		service_info = json.loads(f.read())
	service_name = service_info['name']

	return service_name


def get_port_for_service(service_name):
	"""
	获得指定service的bdd server端口
	"""
	service2port = read_service_to_port_info()
	return service2port.get(service_name, None)


def determin_service_port(service2port, service_name):
	"""
	确定service的bdd server端口
	"""
	port = INITIAL_PORT # default port
	if service_name in service2port:
		port = service2port[service_name]
	else:
		if len(service2port) == 0:
			port = INITIAL_PORT
		else:
			used_ports = [int(port) for port in service2port.values()]
			used_ports.sort()
			port = used_ports[-1]+1

	# write back port info
	service2port[service_name] = port
	with open(PORT_FILE_PATH, 'wb') as f:
		f.write(json.dumps(service2port))
		f.flush()

	return port


def get_my_port():
	"""
	获得当前service的bdd server端口
	"""
	service2port = read_service_to_port_info()
	service_name = get_current_service_name()

	return determin_service_port(service2port, service_name)

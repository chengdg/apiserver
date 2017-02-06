# -*- coding: utf-8 -*-

import os
import json

from util.command import BaseCommand


class Command(BaseCommand):
	help = "rebuild database for service"
	args = ''
	
	def handle(self, **options):
		if os.name == 'nt':
			#在windows开发环境，模拟容器的环境变量
			os.environ['_IS_SERVICE_IN_CONTAINER'] = '1'
			os.environ['_SERVICE_MODE'] = 'develop'

		import servicecli
		servicecli.rebuild_service_in_container()
# -*- coding: utf-8 -*-

import os
import json

from util.command import BaseCommand


class Command(BaseCommand):
	help = "inspect service: 1. rebuild db, 2. init db"
	args = ''
	
	def handle(self, **options):
		if os.environ.get('_IS_SERVICE_IN_CONTAINER', '0') != '1':
			print '[error]: inspect service must invoked in container'
			import sys
			sys.exit(1)

		import servicecli
		servicecli.inspect_service_in_container()
# -*- coding: utf-8 -*-

"""批量进行文件内容替换的工具，在重构时，如果一个module的路径有所变化，该命令可以用来批量修改py文件中的import
"""

__author__ = 'robert'

import datetime
import array
import os

from utils.command import BaseCommand

from core.cache import utils as cache_util
from bson import json_util
import json

class Command(BaseCommand):
	help = "python manage.py batch_replace [src] [dest]"
	args = ''
	
	def handle(self, src, dest, **options):
		for root, dirs, files in os.walk('.'):
			for f in files:
				if not f.endswith('.py'):
					continue

				file_path = os.path.join(root, f)
				new_content = None
				with open(file_path, 'rb') as src_file:
					content = src_file.read().decode('utf-8')
					if src in content:
						new_content = content.replace(src, dest)

				if new_content:
					with open(file_path, 'wb') as dst_file:
						print >> dst_file, new_content.encode('utf-8')
						print 'process ', file_path


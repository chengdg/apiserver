# -*- coding: utf-8 -*-
"""@package wapi.mall.a_image
上传图片

"""
from core import api_resource
from wapi.decorators import param_required
import logging

from utils import upload_img

class AImage(api_resource.ApiResource):
	"""
	上传图片

	"""
	app = 'mall'
	resource = 'image'


	@param_required(['file'])
	def put(args):
		webapp_owner = args['webapp_owner']
		file_data = args['file']
		image_path = upload_img.save_base64_img_file_local_for_webapp(webapp_owner.id, file_data)
		if image_path:
			return {"image_path": image_path}
		else:
			return 500

		

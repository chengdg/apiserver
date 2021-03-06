# -*- coding: utf-8 -*-
"""@package apimall.a_image
上传图片

"""
from eaglet.core import api_resource
from eaglet.decorator import param_required
import logging

from util import upload_img

class AImage(api_resource.ApiResource):
	"""
	上传图片

	"""
	app = 'mall'
	resource = 'image'


	@param_required(['file'])
	def put(args):
		"""
		@param file
		@return {"image_path": image_path}
		"""
		webapp_owner = args['webapp_owner']
		file_data = args['file']
		image_path = upload_img.save_base64_img_file_local_for_webapp(webapp_owner.id, file_data)
		if image_path:
			return {"image_path": image_path}
		else:
			return 500

		

# -*- coding: utf-8 -*-
"""@package wapi.mall.a_coupon_qrcode
优惠券二维码接口

@see Webapp中的`mall/promotion/coupon.py`

"""
import os

from core import api_resource
from wapi.decorators import param_required

#from excel_response import ExcelResponse

#from core import resource
#from mall import export
#from mall.models import *
#from modules.member.models import WebAppUser
#from modules.member.module_api import get_member_by_id_list
#from core import paginator
#from models import *
#from core.jsonresponse import create_response, JsonResponse
#from core import search_util
#from mall.promotion.utils import create_coupons

COUNT_PER_PAGE = 20
PROMOTION_TYPE_COUPON = 4
FIRST_NAV_NAME = export.MALL_PROMOTION_AND_APPS_FIRST_NAV


class ACouponQrcode(api_resource.Resource):
	"""
	优惠券二维码
	"""

	app = "mall2"
	resource = "coupon_qrcode"

	@param_required
	def get(args):

		"""
		下载优惠券二维码
		"""
		coupon_id = args.GET["id"]
		dir_path = os.path.join(settings.UPLOAD_DIR, '../coupon_qrcode/')
		filename = dir_path + coupon_id + '.png'
		try:
			response = HttpResponse(open(filename, "rb").read(), mimetype='application/x-msdownload')
			response['Content-Disposition'] = 'attachment; filename="qrcode.png"'
		except:
			response = HttpResponse('')
		return response
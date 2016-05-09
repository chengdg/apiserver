# -*- coding: utf-8 -*-

from eaglet.core.service.celery import task

from eaglet.core.wxapi import get_weixin_api
from db.account import weixin_models as weixin_user_models


@task(bind=True)
def send_template_message(self, mpuser_access_token_dict, message):
    mpuser_access_token = weixin_user_models.WeixinMpUserAccessToken.from_dict(mpuser_access_token_dict)
    weixin_api = get_weixin_api(mpuser_access_token)
    weixin_api.send_template_message(message, True)

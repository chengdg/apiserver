# -*- coding: utf-8 -*-
"""
@package business.news
图文业务模型
"""

from business import model as business_model
from db.news import models as news_models
from wapi.decorators import param_required
import logging
from core.decorator import deprecated

class NewsPage(business_model.Model):
    """
    图文业务模型
    """

    __slots__ = (
        'id',
        'title',
        'text',
        'is_show_cover_pic',
        'pic_url',
        'created_at'
    )

    def __init__(self, model):
        business_model.Model.__init__(self)

        if model:
            self._init_slot_from_model(model)
            model.created_at = model.created_at.strftime('%Y-%m-%d')

    @staticmethod
    @param_required(['news_id'])
    def from_id(args):
        """
        获取图文对象

        @return 如果不存在，返回None
        """
        try:
            model = news_models.News.get(id=args['news_id'])
            news_page = NewsPage(model).to_dict()
            return news_page
        except Exception as e:
            logging.error("Exception: " + str(e))
        return None
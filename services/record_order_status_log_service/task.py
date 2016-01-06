# -*- coding: utf-8 -*-
from celery import task

from db.mall import models as mall_models


@task
def record_order_status_log(order_id, operator, from_status, to_status):
    """
    创建订单状态日志
    """

    order_status_log = mall_models.OrderStatusLog.create(
            order_id=order_id,
            from_status=from_status,
            to_status=to_status,
            operator=operator
    )
    return order_status_log

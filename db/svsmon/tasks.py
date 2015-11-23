#coding:utf8
from __future__ import absolute_import

from core.exceptionutil import full_stack
from db.svsmon.models import Svsmon,  TASK_ACCEPTED, TASK_REVOKED, TASK_ERROR, TASK_SUCCESS, TASK_TIMEOUT, TASK_RETRY, TASK_FAILURE, TASK_UNKNOWN
from weapp.celery import task
import settings

@task(bind=True)
def svslog(self, t, pid, task_id, status, message):
    obj=Svsmon.create(task=t, pid=pid, task_id=task_id, status = status, message=(message  and dumps(message) or ''))
    #obj.save(using=settings.WATCHDOG_DB)

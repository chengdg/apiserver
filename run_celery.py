#!/usr/bin/python
# coding: utf-8
# EASY-INSTALL-ENTRY-SCRIPT: 'celery==3.1.17','console_scripts','celery'
# 
'''
import sys;
from weapp.celery import app;
from celery.execute import send_task
send_task('example.tasks.example_task',args=['give me a break: AAAAA'])

'''
# 
# rss = tuple([ send_task('example.tasks.example_task',args=['give me a break: %s'%i]) for i in xrange(100000) ])

import os,sys,re,signal,logging

from logging.handlers import TimedRotatingFileHandler
from celery.signals import setup_logging,  after_setup_logger
from celery.worker.job import logger
import settings
from core.service.celery import app as weapp_celery
from core.service.celery import celery_logger
from celery.utils.log import ensure_process_aware_logger
from celery import task
from json import dumps,loads
import logging

# jz 2015-11-24
from db.svsmon.models import Svsmon,  TASK_ACCEPTED, TASK_REVOKED, TASK_ERROR, TASK_SUCCESS, TASK_TIMEOUT, TASK_RETRY, TASK_FAILURE, TASK_UNKNOWN
#from django.core.mail import send_mail

ensure_process_aware_logger()

WEAPP_CELERY_DIR = os.path.dirname(os.path.realpath(__file__) or os.path.realpath(sys.argv[0]))
WEAPP_CELERY_LOG_DIR = os.path.realpath(os.path.join(WEAPP_CELERY_DIR,'../log/celery/') )
PIDFILE = os.path.join(WEAPP_CELERY_LOG_DIR, 'celery-%i.pid')
LOGFILE = os.path.join(WEAPP_CELERY_LOG_DIR, 'celery-%i.log')

SERVICE_BLACKLIST = {
  
}

CELERY_BUILTINS = {
        'celery.backend_cleanup':True,
        'celery.chain':True,
        'celery.chord':True,
        'celery.chord_unlock':True,
        'celery.chunks':True,
        'celery.group':True,
        'celery.map':True,
        'celery.starmap':True,
        }

# for k,v in CELERY_BUILTINS.iteritems():
#     if not SERVICE_BLACKLIST.has_key(k):
#         SERVICE_BLACKLIST[k] = v

logging.info("in run_celery.py")

# jz 2015-11-24
# def svslog(t, pid, task_id, status, message):
#     obj=Svsmon.create(task=t, pid=pid, task_id=task_id, status = status, message=(message  and dumps(message) or ''))
    #obj.save(using=settings.WATCHDOG_DB)

class CeleryTaskMonitor(logging.Filter):
    pairs = {}
    tasks  = {}
    loggers = {}

    def __init__(self, app,  logdir, sys_handler=None, name='celery.worker.job',  level=logging.DEBUG):
        logging.Filter.__init__(self,name)
        self.logdir = os.path.realpath(logdir)
        assert os.path.isdir(self.logdir)
        self.app = app
        self.level = level
        self.loggers = {}
        self.mainpid = pid = os.getpid()
        fmt = '[%(asctime)s][%(levelname)s][%(process)s] %(message)s'
        sys_handler and sys_handler.setFormatter(logging.Formatter(fmt))
        self.handlers = sys_handler and [sys_handler] or []
        if not self.loggers:
            for task in  self.app.tasks:
                if task in CELERY_BUILTINS:
                    continue
                log_file = '%s/%s.log' %(self.logdir, task)
                handler = TimedRotatingFileHandler(log_file, 'D', 30, 0)
                handler.suffix = "%Y%m%d_%H%M.log"
                handler.setFormatter(logging.Formatter(fmt))
                hlogger = celery_logger(task)
                hlogger.handlers = []
                hlogger.addHandler(handler)
                hlogger.setLevel(self.level)
                hlogger.propagate = False
                self.loggers[task] = hlogger

            log = celery_logger(name)
            log.propagate = False
            log.setLevel(level)
            log.addFilter(self)

            celery_log = celery_logger('celery')
            celery_log.handlers = self.handlers
            celery_log.propagate = False
            celery_log.setLevel(logging.WARNING)

            celery_task_log = celery_logger('celery.task')
            celery_task_log.handlers = self.handlers
            celery_task_log.propagate = False
            celery_task_log.setLevel(logging.WARNING)

            consumer_log = celery_logger('celery.worker.consumer')
            consumer_log.handlers = self.handlers
            consumer_log.propagate = False
            consumer_log.setLevel(level)
            #consumer_log.addFilter(self)

            strategy_log = celery_logger('celery.worker.strategy')
            strategy_log.setLevel(logging.WARNING)
            strategy_log.handlers = self.handlers

            redirected_log = celery_logger('celery.redirected')
            redirected_log.handlers =self.handlers
            redirected_log.propagate = False
            redirected_log.setLevel(level)
            
    def filter(self, r):
        if r.module== 'consumer' :
            if r.funcName == 'on_unknown_task':
                # try:
                #     r.msg = u'\n收到未注册Task:\n [ %s ]:\n    1. 请确认该Task已经添加到 settings.py:INSTALLED_TASKS;\n    2. Celery重启完毕以加载该Task；\n  参数和异常信息:\n    %s'
                #     r.args = (r.args[0].args[0], r.args[1].split('Traceback')[0])
                #     s = r.args[1] 
                #     s = s[s.find('{'): 1+s.rfind('}')]
                #     ctx = None
                #     try:
                #         ctx = eval(s)
                #     except:
                #         pass
                #     if ctx:
                #         if ctx['task'] in SERVICE_BLACKLIST:
                #             return False
                #         # jz 2015-11-24
                #         # svslog(ctx['task'], r.process, ctx['id'], status=TASK_UNKNOWN, message=s)
                #     subject = u'测试邮件：　服务异常: Celery收到未注册Task: %s' % ctx['task']
                #     message = u'1. 请确认该Task已经添加到 settings.py:INSTALLED_TASKS;\n2. Celery重启完毕以加载该Task；\n3. 参数和异常信息:\n4. %s' % r.args[1]
                #     logging.info("Email Message: "+message)
                #     #send_mail(subject,
                #               # message, 
                #               # 'heyijun@weizoom.com',
                #               # ['heyijun@weizoom.com'], fail_silently=False)
                # except:
                #     pass
                return True
            return False
        else:
            if r.levelno == logging.ERROR and r.funcName:
                r.funcName = 'on_error'
            return getattr(self, r.funcName, 'on_failure')(r)

    def revoked(self, r):
        task, tid = r.args
        self.on_reallog(r, tid, TASK_REVOKED)

    def on_error(self, r):
        tid, r.task = r.args.get('id'), r.args.get('name')
        self.on_reallog(r, tid, TASK_ERROR)

    def on_accepted(self, r):
        r.levelno = logging.INFO
        r.levelname = 'INFO'
        r.msg = 'Task [%s] accepted in pid:%r'
        task, tid, pid = r.args
        r.args = (tid, pid)
        r.process = pid
        self.pairs[tid] = (pid, task)
        if r.task in SERVICE_BLACKLIST:
            return False
        # jz 2015-11-24
        # svslog(task, tid, pid, status = TASK_ACCEPTED)
        if self.loggers.has_key(task):
            real_logger = self.loggers[task]
            real_logger.handle(r)
            return False

    def on_success(self, r):
        tid = r.args.get('id')
        r.msg = 'Task [%(id)s] succeeded in %(runtime)ss: %(return_value)s'
        self.on_reallog(r, tid, TASK_SUCCESS)

    def on_timeout(self, r):
        timeout, task, tid = r.args
        self.on_reallog(r, tid, TASK_TIMEOUT)

    def on_retry(self, r):
        tid, name, exc = r.args
        self.on_reallog(r, tid, TASK_RETRY)

    def on_failure(self, r):
        tid = r.args['id']
        self.on_reallog(r, tid, TASK_FAILURE)

    def on_reallog(self, r, tid, status):
        if CeleryTaskMonitor.pairs.has_key(tid):
            r.process, r.task = self.pairs.pop(tid)
            if r.task in SERVICE_BLACKLIST:
                return False
            # jz 2015-11-24
            # svslog(r.task, r.process, tid, status, message=(hasattr(r, 'args') and r.args) and dumps(r.args) or None)
            if self.loggers.has_key(r.task):
                real_logger = self.loggers[r.task]
                real_logger.handle(r)
                return False
        return True

@after_setup_logger.connect
def hijack_celery_log(signal, sender, logger, loglevel, logfile, format, colorize,  *args):
    return CeleryTaskMonitor(weapp_celery, WEAPP_CELERY_LOG_DIR, sys_handler=logger.handlers[0])

def getcmd():
    from time import sleep
    CMD_DICT = {
               'start'   :'celery worker -E -A core.service  --pidfile=%s  --logfile=%s -l warning' %( PIDFILE, LOGFILE),
               'show'    :'celery multi show     worker -A core.service  --pidfile=%s  --logfile=%s ' %(PIDFILE, LOGFILE),
               'stopwait':'celery multi stopwait --pidfile=%s',
               'stop'    :'celery multi stop     --pidfile=%s',
               'kill'    :'celery multi kill     --pidfile=%s',
               'names'   :'celery multi names    --pidfile=%s',
               }
    fname = os.path.basename(os.path.realpath(__file__))
    print("fname: {}".format(fname))
    i = (lambda x:(x and x[0] or 0)) ([i for i in xrange(len(sys.argv)) if sys.argv[i].endswith(fname)])
    argv = sys.argv[i:]
    cmd = len(argv) < 2 and 'start' or argv[1]
    cmdline = CMD_DICT.get(cmd)
    #_list = os.listdir(WEAPP_CELERY_LOG_DIR)
    #print("list: {}".format(_list))
    all_files = os.listdir(WEAPP_CELERY_LOG_DIR)
    pidfiles = [ f  for f in all_files if f.startswith('celery-') and f.endswith('.pid') ]
    pidfiles = [ (file(os.path.join(WEAPP_CELERY_LOG_DIR, f)).read().strip(), os.path.join(WEAPP_CELERY_LOG_DIR, f)) for f in pidfiles ]
    pids = [(int(pid),f) for (pid,f) in pidfiles if pid.isdigit()]
    if cmd == 'down':
        for pid,f in pids:
            try:
                os.kill(pid, signal.SIGQUIT)
            except:
                pass
    if cmd == 'stop':
        for pid,f in pids:
            try:
                os.kill(pid, signal.SIGTERM)
            except:
                pass
    if cmd == 'restart':
        for pid,f in pids:
            try:
                os.kill(pid, signal.SIGHUP)
                sleep(5)
            except:
                raise     
    if cmd == 'start':
        running  = False
        pidfpath = ''     
        for pid,fpath in pids:
            try:
                os.kill(pid, signal.SIG_IGN)
                running = True
                pidfpath = fpath
                break
            except OSError:
                errtype, errinst, traceback = sys.exc_info()
                if hasattr(errinst,'args') and errinst.args == (3, 'No such process'):
                    os.remove(fpath)
            except:
                pass
        if running:
            print 'PIDFILE(%s)存在：， 请确认是否Celery已停止运行（ps aux | grep celery）' % pidfpath
            return None
        print cmdline
        return cmdline

    
if __name__ == '__main__':
    cmdline = getcmd()
    if cmdline:
        sys.argv = cmdline.split()
        from celery import __main__ as main
        entry = getattr(main, 'main')
        sys.exit(entry())

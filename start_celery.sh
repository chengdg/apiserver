#!/bin/bash
#celery -A weapp worker -l info
rm -f celery.pid
nohup python run_celery.py   &
#celery -A core.service worker -l info --pidfile="celery.pid"

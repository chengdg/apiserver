#!/bin/bash
#celery -A weapp worker -l info
rm -f celery.pid
nohup python run_celery.py   &

#!/bin/bash

function old_way() {
echo kill `cat ../celery.pid` 
kill `cat ../celery.pid` 

echo sleep 5s
sleep 5

echo start celery
nohup celery -A core.service worker -l info --pidfile=../celery.pid &> ../celery.log &
celery multi restart worker -A core.service --pidfile="celery-%N-%i.pid" --logfile="celery-%N-%i.log" -l info
}
python run_celery.py stop
echo sleep 5s
sleep 5
nohup python run_celery.py start &

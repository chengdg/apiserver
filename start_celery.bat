celery -A apiserver worker -l info --pidfile="celery.pid"
REM celery worker -A apiserver --pidfile="celery-%N-%i.pid" --logfile="celery-%N-%i.log" -l info
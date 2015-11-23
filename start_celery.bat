celery -A core.celery worker -l info --pidfile="celery.pid"
REM celery core.celery -A apiserver --pidfile="celery-%N-%i.pid" --logfile="celery-%N-%i.log" -l info
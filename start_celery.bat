celery -A core.service worker -l info --pidfile="celery.pid"
REM celery core.service -A apiserver --pidfile="celery-%N-%i.pid" --logfile="celery-%N-%i.log" -l info
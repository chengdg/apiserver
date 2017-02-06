#!/bin/bash
PORT=${1:-8001}

if [ "${_SERVICE_HOST_PORT}" == "" ]; then
	__IGNORE=1 #do nothing
else
	PORT=${_SERVICE_HOST_PORT}
fi

# prepare service
CAN_START_SERVICE=`python <<END
import servicecli
servicecli.prepare_service(${PORT})
END`

if [ "${CAN_START_SERVICE}" == "false" ]; then
	exit 2
fi

if [ "$_PROCESS_COUNT" == "" ]; then
	_PROCESS_COUNT=10
fi
echo "process count: ${_PROCESS_COUNT}"

# start service
if [ "$_USE_WSGI_PROTOCAL" == "1" ]; then
	uwsgi --processes ${_PROCESS_COUNT} --socket 0.0.0.0:${PORT} service.ini
else
	python manage.py runserver 0.0.0.0 $PORT
fi

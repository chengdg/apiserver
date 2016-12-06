#!/bin/bash
PORT=${1:-8001}

# prepare service
CAN_START_SERVICE=`python <<END
import servicecli
servicecli.prepare_service(${PORT})
END`

if [ "${CAN_START_SERVICE}" == "false" ]; then
	exit 2
fi

# start service
if [ "$_WEIZOOM_PRODUCTION" == "1" ]; then
	uwsgi service.ini
else
	python manage.py runserver 0.0.0.0 $PORT
fi



#trap cleanup 2
#while true; do
# python manage.py runserver 0.0.0.0 8001
#done

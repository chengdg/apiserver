#!/bin/bash
DIR=`dirname $0`
cd $DIR

cleanup() {
  exit 1	
}

trap cleanup 2

while true; do
 python manage.py runserver 0.0.0.0 8001
done

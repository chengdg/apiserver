#!/bin/bash

# wait for the starting of DB
sleep 10

# remove all existed .pyc
rm -f `find . -name '*.pyc'`

uwsgi --ini apiserver.ini

# loop forever
while true; do sleep 1000; done

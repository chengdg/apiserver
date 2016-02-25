#!/bin/bash

sleep 10

uwsgi --ini apiserver.ini

# loop forever
while true; do sleep 1000; done

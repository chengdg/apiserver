#!/bin/bash

uwsgi --ini apiserver.ini

# loop forever
while true; do sleep 1000; done

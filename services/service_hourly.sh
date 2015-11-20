#!/bin/bash
export PATH=/usr/local/bin:$PATH
# 每小时调用的service

DATE="`date +%Y%m%d`"
TIME="`date +%Y%m%d%H%M%S`"
ROOT_DIR="/weapp/web/weapp"
#ROOT_DIR="`pwd`"
LOG_DIR="$ROOT_DIR/../log/services/$DATE"
mkdir -p $LOG_DIR

LOG="$LOG_DIR/hourly_$TIME.log"
echo "called time: $TIME" > $LOG
echo "LOG_DIR=$LOG_DIR"

echo "ROOT_DIR=$ROOT_DIR"
cd $ROOT_DIR
echo "========================================================" >> $LOG

# add more services here

echo "========================================================" >> $LOG
echo "done!" >> $LOG
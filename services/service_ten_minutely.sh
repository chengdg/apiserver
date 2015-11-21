#!/bin/bash
export PATH=/usr/local/bin:$PATH
# to be called ten minutely
DATE="`date +%Y%m%d`"
TIME="`date +%Y%m%d%H%M%S`"
ROOT_DIR="/weapp/web/weapp"
#ROOT_DIR="`pwd`"
LOG_DIR="$ROOT_DIR/../log/services/$DATE"
mkdir -p $LOG_DIR

LOG="$LOG_DIR/ten_minute_$TIME.log"
echo "called time: $TIME" > $LOG
echo "LOG_DIR=$LOG_DIR"

echo "ROOT_DIR=$ROOT_DIR"
cd $ROOT_DIR
echo "========================================================" >> $LOG

# add more services here

# echo ">> calling 'services.update_component_mp_token_service.tasks.update_component_mp_info'" >> $LOG
# echo "--------------------------------------------------------" >> $LOG
# python services/send_task.py "services.update_component_mp_token_service.tasks.update_component_mp_info" {} "{\"id\": 0}" >> $LOG 2>&1

echo ">> calling 'services.analysis_message_service.tasks.analysis_message'" >> $LOG
echo "--------------------------------------------------------" >> $LOG
python services/send_task.py "services.analysis_message_service.tasks.analysis_message" {} "{}" >> $LOG 2>&1

#add by duhao 20150521
echo ">> calling 'services.count_keyword.tasks.count_keyword'" >> $LOG
echo "--------------------------------------------------------" >> $LOG
python services/send_task.py "services.count_keyword_service.tasks.count_keyword" {} "{}" >> $LOG 2>&1
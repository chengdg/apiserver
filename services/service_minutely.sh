#!/bin/bash
export PATH=/usr/local/bin:$PATH
# to be called minutely
DATE="`date +%Y%m%d`"
TIME="`date +%Y%m%d%H%M%S`"
ROOT_DIR="/weapp/web/weapp"
#ROOT_DIR="`pwd`"
LOG_DIR="$ROOT_DIR/../log/services/$DATE"
mkdir -p $LOG_DIR

LOG="$LOG_DIR/minute_$TIME.log"
echo "called time: $TIME" > $LOG
echo "LOG_DIR=$LOG_DIR"

echo "ROOT_DIR=$ROOT_DIR"
cd $ROOT_DIR
echo "========================================================" >> $LOG

# add more services here

echo ">> calling 'services.start_promotion_service.tasks.start_promotion'" >> $LOG
echo "--------------------------------------------------------" >> $LOG
python services/send_task.py "services.start_promotion_service.tasks.start_promotion" {} "{\"id\": 0}" >> $LOG 2>&1

echo ">> calling 'services.finish_promotion_service.tasks.finish_promotion'" >> $LOG
echo "--------------------------------------------------------" >> $LOG
python services/send_task.py "services.finish_promotion_service.tasks.finish_promotion" {} "{\"id\": 0}" >> $LOG 2>&1

echo ">> calling 'services.update_mp_token_service.tasks.update_mp_token'" >> $LOG
echo "--------------------------------------------------------" >> $LOG
python services/send_task.py "services.update_mp_token_service.tasks.update_mp_token" {} "{\"id\": 0}" >> $LOG 2>&1

echo ">> calling 'cancell_not_pay_order'" >> $LOG
echo "--------------------------------------------------------" >> $LOG
python manage.py cancell_not_pay_order >> $LOG 2>&1

echo "========================================================" >> $LOG
echo "done!" >> $LOG
# coding: utf-8
import os
import datetime

branch_name = os.popen('git symbolic-ref --short HEAD').read().strip()
now = datetime.datetime.now()
backup_name = '__bak_'+branch_name+'_' + now.strftime("%Y-%m-%d_%H-%M")
os.system('git branch ' + backup_name)

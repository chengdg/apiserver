# -*- coding: utf-8 -*-
"""
增加用户名
"""
import subprocess

commit_msg_filepath = '.git/COMMIT_EDITMSG'

try:
    username = subprocess.check_output('git config --local user.name').strip()
except:
    try:
        username = subprocess.check_output('git config --system user.name').strip()
    except:
        try:
            username = subprocess.check_output('git config --global user.name').strip()
        except:
            username = None

with open(commit_msg_filepath, 'r') as f:
    raw_msg = f.read()

with open(commit_msg_filepath, 'w') as f:
    f.write("[%s]%s" % (username, raw_msg))

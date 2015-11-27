# -*- coding: utf-8 -*-
"""
增加当前本地分支名，如果当前不在一个分支上，则不增加
"""
import os

commit_msg_filepath = '.git/COMMIT_EDITMSG'
# 注意：当不在一个分支上时，取不到分支名
branch_name = os.popen('git symbolic-ref --short HEAD').read().strip()
if branch_name:
    with open(commit_msg_filepath, 'r') as f:
        raw_msg = f.read()

    with open(commit_msg_filepath, 'w') as f:
        f.write("[%s]%s" % (branch_name, raw_msg))

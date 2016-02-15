# -*- coding: utf-8 -*-
"""
增加当前本地分支名，如果当前不在一个分支上，则不增加
"""
import os


def git_shell(git_command):
    try:
        return os.popen(git_command).read().strip()
    except:
        return None

commit_msg_file_path = '.git/COMMIT_EDITMSG'
# 注意：当不在一个分支上时，取不到分支名
branch_name = git_shell('git symbolic-ref --short HEAD')
if branch_name:
    with open(commit_msg_file_path, 'r+') as f:
        raw_msg = f.read()
        f.seek(0)
        f.write("[%s]%s" % (branch_name, raw_msg))






# -*- coding: utf-8 -*-
"""
增加用户名
"""
import os


def git_shell(git_command):
    try:
        return os.popen(git_command).read().strip()
    except:
        return None

commit_msg_file_path = '.git/COMMIT_EDITMSG'

username = git_shell('git config --local user.name')
if not username:
    username = git_shell('git config --system user.name')
if not username:
    username = git_shell('git config --global user.name')


with open(commit_msg_file_path, 'r+') as f:
    raw_msg = f.read()
    f.seek(0)
    f.write("[%s]%s" % (username, raw_msg))

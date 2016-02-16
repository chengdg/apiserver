# -*- coding: utf-8 -*-
import os

commit_msg_filepath = '.git/COMMIT_EDITMSG'

branch_name = os.popen('git symbolic-ref --short HEAD').read().strip()

if branch_name == 'master':
    print('Commit failed! DO not commit on master!')
    exit(1)

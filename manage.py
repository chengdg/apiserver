#!/usr/bin/env python

# DO NOT delete following lines
# from gevent import monkey
# monkey.patch_all(
#     socket=True,
#     dns=True,
#     time=True,
#     select=True,
#     thread=True,
#     os=True,
#     ssl=True,
#     httplib=False,
#     aggressive=True
# )

# import os
import sys
# import time
# from django.conf import settings

# patch django autoreload
# from django.utils import autoreload


# def my_reloader_thread():
#     autoreload.ensure_echo_on()
#     while autoreload.RUN_RELOADER:
#         if autoreload.code_changed():
#             if settings.IS_UNDER_CODE_GENERATION:
#                 count = 1
#                 while True:
#                     print 'waiting settings.IS_UNDER_CODE_GENERATION change to FALSE..........'
#                     if not settings.IS_UNDER_CODE_GENERATION:
#                         break
#                     if count >= 5:
#                         break
#                     count += 1
#                     time.sleep(1)
#             os._exit(3)
#         time.sleep(1)

# autoreload.reloader_thread = my_reloader_thread

# if __name__ == "__main__":
#     command = sys.argv[1]
#     target_py = '%s.py' % command
#     commands_dir = './commands'
#     found_command = False
#     import os
#     for f in os.listdir(commands_dir):
#         if os.path.isfile(os.path.join(commands_dir, f)):
#             if f == target_py:
#                 found_command = True
#                 module_name = 'commands.%s' % command
#                 module = __import__(module_name, {}, {}, ['*',])
#                 instance = getattr(module, 'Command')()
#                 try:
#                     instance.handle(*sys.argv[2:])
#                 except TypeError, e:
#                     print '[ERROR]: wrong command arguments, usages:'
#                     print instance.help

#     if not found_command:
#         print 'no command named: ', command
import sys,os
from eaglet.command import manage as command_manager

print ">>>>>",sys.path
import settings
if __name__ == '__main__': 
    wapi_path = os.path.join(settings.PROJECT_HOME, '..', 'wapi')
    sys.path.insert(0, wapi_path)
    command = sys.argv[1]
    command_manager.run_command(command)


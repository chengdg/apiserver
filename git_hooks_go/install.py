# -*- coding: utf-8 -*-

from git_hooks_go import copytree2, src_path, hooks_path
import os

try:
    copytree2(src_path, hooks_path)
    print(u'安装成功')
    os.system('pause')
except BaseException as e:
    print(e)
    print(u'安装失败')
    os.system('pause')

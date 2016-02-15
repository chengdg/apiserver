# -*- coding: utf-8 -*-
import json
import subprocess
import re

status = subprocess.check_output('git status -s')

rule = re.compile('([Ww]hen|[Tt]hen|[Gg]iven|[Aa]nd)[\s\S]*?"""([\s\S]*?)"""')
has_error = False
for file_line in status.split('\n'):
    if not file_line.startswith(' ') and not file_line.startswith('?') and not file_line.startswith('D') and len(
            file_line) and file_line.endswith(
            '.feature'):
        file_path = file_line.split()[-1]
        with open(file_path) as f:
            content = f.read()
            result = rule.findall(content)
            for i in result:
                step_content = i[1]
                try:
                    json.loads(step_content)
                except BaseException as e:
                    print('error file:', str(file_line))
                    print('error step:')
                    print(step_content)
                    print('error info:')
                    print(e)
                    print("-----------------------------------")
                    has_error = True

if has_error:
    exit(1)

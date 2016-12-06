#!/bin/bash

python <<END
import servicecli
args = '$*'.split(' ')
if (len(args) == 1) and (len(args[0]) == 0):
	args = ['build_image.sh']
else:
	args.insert(0, 'build_image.sh')
servicecli.build_image(*args)
END
#!/bin/bash
doxygen Doxyfile
sed -i -e "s/charset=iso-8859-1/charset=utf-8/g" doc/html/*.html

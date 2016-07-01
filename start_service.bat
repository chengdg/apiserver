@echo off
set a=%cd: =:%
set a=%a:\= %
for %%j in (%a%) do (set a=%%j)
set a=%a::= %
title %a%

pip2 install git+https://git2.weizzz.com:84/microservice/eaglet.git

python manage.py runserver 0.0.0.0 8001

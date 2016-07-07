@echo off
set a=%cd: =:%
set a=%a:\= %
for %%j in (%a%) do (set a=%%j)
set a=%a::= %
title %a%


behave -k --no-capture --no-capture-stderr -t @bdd_server

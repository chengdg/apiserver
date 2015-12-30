#!/bin/bash
for x in 1 2 3 4 5 6 7 8 9; do
 python manage.py runserver 0.0.0.0 8001
done

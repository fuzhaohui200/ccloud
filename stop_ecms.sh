#!/bin/bash
kill `ps -ef | grep "/usr/local/bin/python manage.py"| awk -F' ' '{print $2}' | head -1`


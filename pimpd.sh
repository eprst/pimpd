#!/usr/bin/env sh
cd /home/pi/pimpd/pimpd
/bin/date >> /var/log/pimpd.log
exec /usr/bin/python3 pimpd.py >> /var/log/pimpd.log 2>&1

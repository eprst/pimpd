#!/usr/bin/env sh
cd /home/pi/pimpd
# /bin/date >> /var/log/pimpd.log
# exec /usr/bin/python3 pimpd.py >> /var/log/pimpd.log 2>&1
python3 -m venv env
. env/bin/activate
python3 pimpd/pimpd.py

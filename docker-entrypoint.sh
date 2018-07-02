#!/bin/bash

echo "America/Recife" > /etc/timezone
dpkg-reconfigure -f noninteractive tzdata

cd /var/www/backupy

pip3 install -r requirements.txt

crontab -r
(crontab -l 2>/dev/null; echo "* * * * * python3 /var/www/backupy/executor.py") | crontab -

cron -f

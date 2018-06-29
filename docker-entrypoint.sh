#!/bin/bash

echo "America/Recife" > /etc/timezone
dpkg-reconfigure -f noninteractive tzdata

cd /var/www/backupy

pip3 install -r requirements.txt

(crontab -l 2>/dev/null; echo "50 23 * * * python3 /var/www/backupy/executor.py") | crontab -


#!/bin/bash
/usr/sbin/sshd -D &! 

echo "listen_addresses = '*'" >> /etc/postgresql/9.6/main/postgresql.conf
service postgresql restart

git clone git@gitlab.com:genomika/backupy.git
cd backupy

git checkout $backupy_branch

sh crontab.sh

cron -f

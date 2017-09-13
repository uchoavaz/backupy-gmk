#!/bin/bash
/usr/sbin/sshd -D &! 

echo "listen_addresses = '*'" >> /etc/postgresql/9.6/main/postgresql.conf
service postgresql restart

cd /var/www/backupy
git checkout $backupy_branch

/var/www/backupy/crontab.sh

cron -f

#!/bin/bash
/usr/sbin/sshd -D &! 

echo "listen_addresses = '*'" >> /etc/postgresql/9.6/main/postgresql.conf
service postgresql restart

git checkout $backupy_branch

/www/var/backupy/crontab.sh

cron -f

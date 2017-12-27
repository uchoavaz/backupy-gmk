#!/bin/bash

(crontab -l 2>/dev/null; echo "30 02 * * * python /var/www/backupy/run.py") | crontab -
(crontab -l 2>/dev/null; echo "30 13 * * * python /var/www/backupy/run.py") | crontab -

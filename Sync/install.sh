#!/bin/bash
chmod +x cronjob.py
mkdir /etc/backup_rsync/
cp cronjob.py /etc/backup_rsync/
cp USB.py /etc/backup_rsync/
python /etc/backup_rsync/cronjob.py
echo "setting up cronjob in hourly"
su -c "echo \"@hourly /etc/backup_rsync/cronjob.py\" >> /var/spool/cron/crontabs/root"
echo "done. goodbye."

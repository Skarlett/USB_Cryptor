#!/bin/bash
apt-get -y install python-dev python-pip
python -m pip install notify2

chmod +x cronjob.py
mkdir /etc/backup_rsync/

cp cronjob.py /etc/backup_rsync/
cp USB.py /etc/backup_rsync/

echo "Running First run"
python /etc/backup_rsync/cronjob.py
echo "setting up cronjob in hourly"

su -c "echo \"59 * * * * export DISPLAY=:0.0 && export XAUTHORITY=/home/$USER/.Xauthority && sudo -u $USER /usr/bin/python /etc/backup_rsync/cronjob.py\" >> /var/spool/cron/crontabs/root"

echo "done. goodbye."

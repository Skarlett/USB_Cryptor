## Sync
This script will set up your encrypted usbs to be rsync'ed with. It will also set up a cronjob and automate the task hourly
running `install.sh` will cause each encrypted USB by our software to be formatted for auto sync with your computer

## Inner workings.
This file first identifies our encrypted USBs, finds the mount off of tempSave.tmp, goes in, makes a files called dirs.lst.
This file contains all the directories you wish to sync with the encrypted fs on the usb.

### Forcing sync
Simply run `/etc/backup_rsync/cronjob.py`


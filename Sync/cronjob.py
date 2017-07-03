#!/usr/bin/python
from os import walk, system, path, mkdir, getegid
from subprocess import Popen, PIPE
from USB import USB
from datetime import datetime
from time import time


EXTRA_DIR = '/etc/backup_rsync/'
LOG_FILE = path.join(EXTRA_DIR, 'log.log')


def log(data):
  if not data:
    data = 'None'
  with open(LOG_FILE, 'a') as f:
    f.write('[%s | %s ]: %s ' % (str(time()), str(datetime.now()), str(data)))
  
def sys(cmd):
  return Popen(cmd, shell=True, stdout=PIPE).stdout.read()

def notify(message):
  sys('notify-send Backup_Dev "%s"' % message)


def get_backup_dev():
  USB_DEVS = [USB(usb) for usb in set(
    [x for x in sys("for devlink in /dev/disk/by-id/usb*; do readlink -f ${devlink}; done").split('\n') if len(x) > 0])
              if USB(usb).data]
  
  if len(USB_DEVS) > 0:
    log('Usbs found '+str(USB_DEVS))
    
    for usb in USB_DEVS:
      for _, _, files in walk(usb.data.target):
        if 'backup_dev.rip' in files:
          yield usb
  else:
    raise OSError('No backup Dev found')

def main():
  
  log('Starting backup')
  
  notify('Backup started.')
  try:
    try:
      assert getegid() == 0
    except AssertionError:
      raise AssertionError('Needs to run at root level')
    
    for dev in get_backup_dev():
      if path.isfile(path.join(dev.data.target, 'tempSave.tmp')):
        with open(path.join(dev.data.target, 'tempSave.tmp')) as f:
          backupTo = f.read().strip('\n ')
      else:
        notify('FATAL: no mounted encrypted fs')
        log('FATAL: no mounted encrypted fs')
        exit()
    
      if not path.isfile(path.join(backupTo, 'dirs.lst')):
        system('echo "# This file is a configuration of which directories you\'d like to backup.\n'
               '# This specific configuration is specific for (as for the moment of this install) \n'
               '# %s " > %s' % (dev.data.source, path.join(backupTo, 'dirs.lst')))
        system('nano %s' % path.join(backupTo, 'dirs.lst'))
      
      with open(path.join(backupTo, 'dirs.lst')) as f:
        for directory in f:
          if not '#' in directory.strip() and len(directory) > 0 and not backupTo in directory:
            if directory.strip()[::-1][0] == '/':
              directory = directory.strip()[::-1][1:][::-1]
              
            log('copying ' + directory.strip() + ' to ' + backupTo.strip())
            assert system('rsync -azh %s %s' % (directory.strip(), backupTo.strip() )) == 0
            
  except Exception as e:
   log('ERROR: '+e.message)
   notify(e.message)
   exit()
  log('Completed.')
  notify('Backup completed.')

if __name__ == '__main__':
  try:
    assert getegid() == 0
  except AssertionError:
    print "Needs root privs"
  main()

#!/usr/bin/python
from os import walk, system, path
from subprocess import Popen, PIPE
from USB import USB
from datetime import datetime
from time import time
from notify2 import init, Notification

EXTRA_DIR = path.dirname(__file__)
LOG_FILE = path.join(EXTRA_DIR, 'log.log')


def log(data):
  print data
  if not data:
    data = 'None'
  with open(LOG_FILE, 'a') as f:
    f.write('[ %s | %s ]: %s \n' % (str(time()), str(datetime.now()), str(data)))


CanNotify = True
try:
  init("Auto Backup.")
except:
  CanNotify = False
  log('ERROR: Notifications failed to load')

if path.isfile(path.join(EXTRA_DIR, '.installdirectory')):
  userInteraction = True
else:
  userInteraction = False


def sys(cmd):
  return Popen(cmd, shell=True, stdout=PIPE).stdout.read()

def notify(message):
  print message
  if CanNotify:
    Notification('Auto Backup', message).show()

def get_backup_dev():
  USB_DEVS = [USB(usb) for usb in set(
    [x for x in sys("for devlink in /dev/disk/by-id/usb*; do readlink -f ${devlink}; done").split('\n') if len(x) > 0])
              if USB(usb).data]
  
  if len(USB_DEVS) > 0:
    log('Usbs found '+str(USB_DEVS))
    
    for usb in USB_DEVS:
      for _, _, files in walk(usb.data.target):
        if 'backup_dev.rip' in files:
          with open(path.join(usb.data.target, 'backup_dev.rip')) as f:
            name = f.read().strip('\n ')
          yield usb, name
  
def main():
  
  log('Starting backup')
  DEVS = list(get_backup_dev())
  
  if not len(DEVS) > 0:
    log('No devices found')
    notify('Make sure your Backup device is mounted.')
    exit()
  
  notify('Backup started.')
  for dev, name in get_backup_dev(): # Get all of our back up devices
    try:
      enc_dev = USB('/dev/mapper/' + name)
      
      if path.isfile(path.join(dev.data.target, 'tempSave.tmp')):
        with open(path.join(dev.data.target, 'tempSave.tmp')) as f:
          backupTo = f.read().strip('\n ')
        
        if not enc_dev.data.target == backupTo:
          if enc_dev.data.target and not enc_dev.data.target in ['', '/']:
            backupTo = enc_dev.data.target
            log('Tempfile and mount location conflict... resolving now.')
            with open(dev.data.target, 'tempSave.tmp') as f:
              f.write(backupTo)
          else:
            raise OSError('OS and Application conflict. Application believes it\'s active, while the OS says it is not mounted.\n'
                          'Fyi, we\'re taking the OS\'s advice - mount the encrypted fs.')
        
      else:
        if enc_dev.data.target and not enc_dev.data.target in ['', '/']:
          
          with open(path.join(dev.data.target, 'tempSave.tmp'), 'w') as f:
            f.write(enc_dev.data.target)
          log('Recovered and reconfigured tempSave.tmp')
          
        else:
          raise OSError('No tempSave.tmp file in USB, and '+name+' is not mounted')
    
      if not path.isfile(path.join(backupTo, 'dirs.lst')):
        if userInteraction:
          system('echo "# This file is a configuration of which directories you\'d like to backup.\n'
                 '# This specific configuration is specific for (as for the moment of this install) \n'
                 '# %s " > %s' % (dev.data.source, path.join(backupTo, 'dirs.lst')))
          system('nano %s' % path.join(backupTo, 'dirs.lst'))
        else:
          notify(enc_dev.data.source+' from '+dev.data.source+' can be auto sync\'ed, but "dirs.lst" wasn\'t found')
          break
          
      with open(path.join(backupTo, 'dirs.lst')) as f:
        for directory in f:
          if not '#' in directory.strip() and len(directory) > 0 and not backupTo in directory:
            if directory.strip()[::-1][0] == '/':
              directory = directory.strip()[::-1][1:][::-1]
              
            log('copying ' + directory.strip() + ' to ' + backupTo.strip())
            assert system('rsync -azvh %s %s' % (directory.strip(), backupTo)) == 0
    
      print('Completed '+name+' at /dev/mapper/'+name+'\non USB Device: '+dev.data.source+'\nbacked-up to '+backupTo)
      
    except Exception as e:
      log('ERROR: '+e.message)
      notify(e.message)
    
  log('Completed.')
  notify('Backup completed.')

if __name__ == '__main__':
  main()

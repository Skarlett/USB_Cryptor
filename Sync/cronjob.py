#!/usr/bin/python
from os import walk, system, path
from subprocess import Popen, PIPE
from USB import USB
from datetime import datetime
from time import time
from notify2 import init, Notification
from sys import exc_info
from traceback import format_tb

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
  

userInteraction = False
if path.isfile(path.join(EXTRA_DIR, '.installdirectory')):
  userInteraction = True

def sys(cmd):
  return Popen(cmd, shell=True, stdout=PIPE).stdout.read()

def notify(message):
  print message
  if CanNotify:
    Notification('Auto Backup', message).show()

def get_backup_dev():
  USB_DEVS = [USB(usb) for usb in set(
    [x for x in sys("for devlink in /dev/disk/by-id/usb*; do readlink -f ${devlink}; done").split('\n') if len(x) > 0])
              if not '*' in usb and USB(usb).data]
  
  print USB_DEVS
  
  if len(USB_DEVS) > 0:
    log('Usbs found '+str(USB_DEVS))
    
    for usb in USB_DEVS:
      for _, _, files in walk(usb.data.target):
        if 'backup_dev.rip' in files:
          with open(path.join(usb.data.target, 'backup_dev.rip')) as f:
            name = f.read().strip('\n ')
          yield usb, name
  else:
    raise AssertionError('No USB devices found.')
  
def main():
  
  log('Starting backup')
  try:
    DEVS = list(get_backup_dev())
  except AssertionError:
    log('No devices found')
    notify('Make sure your Backup device is mounted.')
    exit()
  
  notify('Backup started.')
  for dev, name in DEVS: # Get all of our back up devices
    try:
      try:
        enc_dev = USB('/dev/mapper/' + name) # get attributes of the encrypted drive
      except AssertionError:
        notify('Encrypted FS on '+dev.data.source+' is not mounted. Failed to backup')
        raise OSError('Could not mount Encryped FS on '+dev.data.source+' located at '+dev.data.target)
      
      if enc_dev.data: # Encrypted FS mounted
        try:
          assert not enc_dev.data.source in ['', '/'] and\
                 not enc_dev.data.target in ['', '/']
        except:
          break
        backupTo = enc_dev.data.target
        
      else: # Encrypted FS not mounted
        raise Exception('Encrypted FS not mounted on '+dev.data.source)
        
        
      if not path.isfile(path.join(backupTo, 'dirs.lst')): # mounted but not configured
        if userInteraction: # hey you there?
          system('echo "# This file is a configuration of which directories you\'d like to backup.\n'
                 '# This specific configuration is specific for (as for the moment of this install) \n'
                 '# %s " > %s' % (dev.data.source, path.join(backupTo, 'dirs.lst')))
          system('nano %s' % path.join(backupTo, 'dirs.lst'))
        else: # senpai notice me
          raise OSError(enc_dev.data.target+' from '+dev.data.source+' can be auto sync\'ed, but "dirs.lst" wasn\'t found')
          
      # Hey we're configured!
      with open(path.join(backupTo, 'dirs.lst')) as f: # Mwahaha.
        for directory in f:
          if not '#' in directory.strip() and len(directory.strip()) > 0 and not backupTo in directory.strip():
            print directory
            if directory.strip()[::-1][0] == '/': # Don't give me any bs
              directory = directory.strip()[::-1][1:][::-1]
              
            log('copying ' + directory.strip() + ' to ' + backupTo.strip()) # our very own diary
            assert system('rsync -azh %s %s' % (directory.strip(), backupTo)) == 0 # Work or else.
    
      log('Completed '+name+' at /dev/mapper/'+name+'\non USB Device: '+dev.data.source+'\nbacked-up to '+backupTo)
      
    except Exception as e: # Errr... Something happened.
      type_, value_, traceback_ =exc_info()
      traceback = format_tb(traceback_)
      log('ERROR: '+e.message) # We'll tell you more about it
      for t in traceback:
        log(t)
      notify('Error, Check logs at '+LOG_FILE) # We'll even try to get your attention
     
  log('Completed.')
  notify('Backup completed.')

if __name__ == '__main__':
  main()

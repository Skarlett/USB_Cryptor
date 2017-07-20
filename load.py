#!/usr/bin/python

#
# . [IN USB]
# crypto.fs
# lost+found/
# backup_dev.rip

from cmtab import cmtab
from os import path, system, getegid, mkdir, remove, walk, removedirs, getlogin
from sys import argv
try:
  from utils import move_file, copy_file, sys
except:
  print(argv[0] + ' m [Mount to] | Mount Encrypted drive\n' + argv[0] + ' u | umount encrypted drive')
  #print('Needs root privs')
  exit(6)

TARGET          = path.dirname(path.abspath(__file__))
CMTAB_FP        = '/etc/cryptmount/cmtab'
ENCRYPTED_DEV   = path.join(TARGET, 'crypto.fs')
INFO_FILE       = path.join(TARGET, 'backup_dev.rip')

try:
  assert getegid() == 0
except AssertionError:
  print('Needs root privleges.')
  exit(2)


with open(INFO_FILE) as f:
  NAME          = f.read().strip(' \n')
MOUNTED_TO      = None


try:
  assert path.isfile(INFO_FILE)
except AssertionError:
  print('Needs backup_dev.rip info file | Otherwise not a BACKUP_DEV')
  exit(1)


if path.isfile(path.join(TARGET, 'tempSave.tmp')):
  with open(path.join(TARGET, 'tempSave.tmp')) as f:
    MOUNTED_TO = f.read().strip(' \n')


def mount(mountTo):
  try:
    assert path.isdir('/etc/cryptmount/keys/')
    
  except Exception as e:
    print('You might need to install the actual program and convert this USB to load it.')
    exit()
 
  key_fp = path.join('/etc/cryptmount/keys/', NAME+'.key')

  try:
    assert path.isfile(key_fp)
  except Exception as e:
    print('No key Found.')
    raise e
    
  if not path.isdir(mountTo):
    mkdir(mountTo)
  
  copy_file(CMTAB_FP, path.join(TARGET, 'cmtab.bak'))
  
  system('echo "%s" > /etc/cryptmount/cmtab' % cmtab(mountTo, ENCRYPTED_DEV, NAME, key_fp).make())
  system('chown -R %s:%s %s' % (getlogin(), getlogin(), mountTo))
  system('chmod 0700 %s' % mountTo)
  
  with open(path.join(TARGET, 'tempSave.tmp'), 'w') as f:
    f.write(mountTo)
  
  assert system('cryptmount '+NAME) == 0
  return True

def umount():
  if not path.isfile(CMTAB_FP):
    print('Fatal Error of losing cmtab - Attempting recovery...')
    try:
      assert system('echo "%s" > /etc/cryptmount/cmtab' % cmtab(
        MOUNTED_TO, ENCRYPTED_DEV, NAME,
        path.join('/etc/cryptmount/keys/', NAME+'.key')
        ).make()) == 0
    except AssertionError:
      raise AssertionError('Could not umount encrypted fs')
  mountData = sys('cryptmount -u ' + NAME + ' && sync')
  if 'is not recognized' in mountData:
    assert system('umount /dev/mapper/'+NAME) == 0
  else: print mountData
  del mountData
  
  print('unmounted '+NAME+' from '+str(MOUNTED_TO))
  print('Cleaning up...')
  
  data = []
  for root, dirs, files in walk(MOUNTED_TO):
    data.extend(files)
    data.extend(dirs)
    break
  
  if len(data) == 0:
    removedirs(MOUNTED_TO)
  
  
  if path.isfile(path.join(TARGET, 'tempSave.tmp')):
    remove(path.join(TARGET, 'tempSave.tmp'))
  
  try:
    if path.isfile(path.join(TARGET, 'cmtab.bak')):
      move_file(path.join(TARGET, 'cmtab.bak'), CMTAB_FP, True)
    
  except:
    raise OSError('Couldn\'t write original cmtab into place, manually move it.')
  print('done.')
  

if __name__ == '__main__':
  try:
    action = argv[1]
    if action == 'm':
      mount(argv[2])
    
    elif action == 'u':
      umount()
    
    elif action == '--help' or action == '-h':
      print(argv[0]+' m [Mount to] | Mount Encrypted drive\n'+argv[0]+' u | umount encrypted drive')
      
    else:
      print(argv[0] + ' m [Mount to] | Mount Encrypted drive\n' + argv[0] + ' u | umount encrypted drive')

  except Exception as e:
     print e.message
     print(argv[0] + ' m [Mount to] | Mount Encrypted drive\n' + argv[0] + ' u | umount encrypted drive')
     

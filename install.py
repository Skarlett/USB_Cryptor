#!/usr/bin/python

from os import system, mkdir, rmdir
from mountutils import *
from USB import USB
from raw_format import raw_format
from time import sleep
from random import choice
from string import ascii_letters, digits
from cmtab import cmtab
from utils import *
from sys import argv


FILEDIR  = path.dirname(path.abspath(__file__))
USB_DEVS = set([x for x in sys("for devlink in /dev/disk/by-id/usb*; do readlink -f ${devlink}; done").split('\n')
                if len(x) > 0 and not '*' in x])
USB_LIST = []

for x in USB_DEVS:
  try:
    usb = USB(x)
    if not usb.data == None and not usb.data.target == FILEDIR:
      USB_LIST.append(usb)
  except AssertionError:
    pass


additional_files = [path.abspath(x) for x in ['cmtab.py', 'load.py', 'mountutils.py',
                    'raw_format.py', 'scrub_hands.py', 'USB.py', 'utils.py']]
additional_files.append(__file__)


def checkInstalled(packageName):
  return sys('dpkg --get-selections | grep '+packageName).replace('install', '').strip() == packageName


def main(usb=None):
  if not usb is None:
    try:
      assert not USB(usb).data.target == '/' and \
             not USB(usb).data.target == FILEDIR
    except:
      print 'Cannot mount root directory or current file directory'
      exit()
      
  try:
    assert getegid() == 0
  except: print('Needs root privs'); exit(6)
  
  
  if not checkInstalled('cryptmount'):
    print('Installing cryptmount...')
    system('apt-get install -y cryptmount')
  
  # if not path.isdir('/etc/cryptmount/keys'):
  #   print('Making our key directory...')
  #   mkdir('/etc/cryptmount/keys')
  
  usbToUse = None
  
  
  print('Attempting to find USB to install into')
  if usb == None:
    if len(USB_LIST) > 0:
      if len(USB_LIST) > 1:
        data = [x for x in enumerate(USB_LIST)]
        for i, _usb in data:
          print(i, _usb.data)
        
        devID = raw_input('Input choice: ')
        try:
          assert devID.isdigit()
          devID = int(devID)
        except AssertionError:
          raise AssertionError('Input needs to be a Number!')
        for i, x in data:
          if i == devID:
            usbToUse = x
            break
        else:
          raise ValueError('Not a number')
      else:
        usbToUse = USB_LIST[0]
        print('Found only one USB device - Assuming device as ' + usbToUse.data.source)
        if not raw_input('Format '+usbToUse.data.source+' and convert to encrypted backup device? [Y/N]: ').lower().startswith('y'):
          exit()
    else:
      raise ValueError('No USB Flash drive Devices Found.')
  else:
    usbToUse = usb
  # Ensure we have a usb
  try:
    assert not usbToUse == None
  except AssertionError:
    AssertionError('Couldn\'t find usb to use')
    
  
  print('Formatting device into ext4...')
  raw_format(usbToUse.data.source.strip('0987654321'), 'ext4', 'BackupDev', 1000, 1000)
  system('sync')
  sleep(5)
  print('Remounting device')
  system('mount '+usbToUse.data.source+' '+usbToUse.data.target+' && sync')
  print('Creating filesystem...')
  
  system('dd if=/dev/zero of="%s" bs=1M count="%d"' % (
     path.join(usbToUse.data.target, 'crypto.fs'),
     getDevEstimate(usbToUse.data.source)
  ))
  
  name = ''.join(choice(ascii_letters + digits) for _ in range(12))
  
  
  print('Creating back up of cmtab at '+path.join(usbToUse.data.target, 'cmtab.bak'))
  copy_file('/etc/cryptmount/cmtab', path.join(usbToUse.data.target, 'cmtab.bak'))
  print('Injecting generated cmtab')
  
  tmpdir = path.join('/tmp/', ''.join(choice(ascii_letters + digits) for _ in range(12)))
  
  if not path.isdir(tmpdir):
    mkdir(tmpdir)
  
  system('echo "%s" > /etc/cryptmount/cmtab' %
         cmtab(tmpdir, path.join(usbToUse.data.target, 'crypto.fs'),
               name, path.join(usbToUse.data.target, name+'.key')).make())
  
  
  print('creating crypto key, use a 12+ character for moderate security, 20+ for state security, but past 32 has no more effect than 1000 charcters')
  sleep(5)
  assert system('cryptmount --generate-key 32 ' + name) == 0
  
  print('Prepare dev for cryptmount')
  assert system('cryptmount --prepare ' + name) == 0
  print('Appending to /dev/mapper...')
  assert system('mke2fs -j "/dev/mapper/"' + name) == 0
  print('Releasing handles...')
  assert system('cryptmount --release ' + name) == 0
  system('sync')
  
  print('Cloning install files, and tools onto usb')
  for x in additional_files:
    copy_file(x, path.join(usbToUse.data.target, x.split('/')[::-1][0]))
  
  print('Moving backup to original Location...')
  move_file(path.join(usbToUse.data.target, 'cmtab.bak'), '/etc/cryptmount/cmtab', True)
  
  print('Adding unique identifier')
  with open(path.join(usbToUse.data.target, 'backup_dev.rip'), 'wb') as f:
    f.write(name)
  
  rmdir(tmpdir)
  
  print('Installation complete, now run\n'
        'python load.py m [directory to mount to](to mount encrypted drive)\n'
        'python load.py u (to umount encrypted drive)\n'
        'To safely remove device, ensure encrypted filesystem is unmounted, and then run umount on the device')


if __name__ == '__main__':
  if len(argv) > 1:
    if not argv[1] == '-h' and not argv[1] == '--help':
      main(argv[1])
    else:
      print(argv[0]+' --help/-h\n'+
            argv[0]+ '/dev/sdXx\n'+
            argv[0]
            )
  else:
    main()
  

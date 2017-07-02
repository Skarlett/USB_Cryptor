from os import system, mkdir
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
USB_DEVS = set([x for x in sys("for devlink in /dev/disk/by-id/usb*; do readlink -f ${devlink}; done").split('\n') if len(x) > 0])
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


def main(mountTo, usb=None):
  try:
    assert getegid() == 0
  except: print('Needs root privs'); exit(6)
  
  
  if not checkInstalled('cryptmount'):
    print('Installing cryptmount...')
    system('apt-get install -y cryptmount')
  
  if not path.isdir('/etc/cryptmount/keys'):
    print('Making our key directory...')
    mkdir('/etc/cryptmount/keys')
  
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
        print('Found only one USB device - Assuming device as '+usbToUse.data.source)
    else:
      #print('No USB Flash drive devices found.')
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
  
  
  # Inject cmtab | copy shit
  # prepare, map and encrypt
  
  print('Creating back up of cmtab at '+path.join(usbToUse.data.target, 'cmtab.bak'))
  copy_file('/etc/cryptmount/cmtab', path.join(usbToUse.data.target, 'cmtab.bak'))
  print('Injecting generated cmtab')
  #with open(, 'w') as f:
  print path.join(usbToUse.data.target, 'crypto.fs')
  system('echo "%s" > /etc/cryptmount/cmtab' % cmtab(mountTo, path.join(usbToUse.data.target, 'crypto.fs'), name, path.join('/etc/cryptmount/keys/', name+'.key')).make())
  
  
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
  print('Moving backup to original Location...')
  
  print('Cloning install files, and tools onto usb')
  for x in additional_files:
    copy_file(x, path.join(usbToUse.data.target, x.split('/')[::-1][0]))
  move_file(path.join(usbToUse.data.target, 'cmtab.bak'), '/etc/cryptmount/cmtab', True)
  
  print('Adding unique identifier')
  with open('backup_dev.rip', 'wb') as f:
    f.write(name)
  
  
  print('Installation complete, now run\n'
        'python load.py m [directory to mount to](to mount encrypted drive)\n'
        'python load.py u (to umount encrypted drive)\n\n'
        'To safely remove device, ensure encrypted filesystem is unmounted, and then run umount on the device')
  
if __name__ == '__main__':
  #./ mount dev
  #./ mount
  if len(argv) > 1:
    if len(argv) > 2:
      # ./ mount dev
      main(*argv[1:])
    else:
      # ./ mount
      main(argv[1])
  else:
    print(
''' %s [Directory]
 %s [Directory] [/dev/path/]
'''.replace('%s', argv[0])
)

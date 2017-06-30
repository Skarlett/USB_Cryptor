#!/usr/bin/python

from os import system, path
from string import digits
from USB import USB
from sys import argv

MOUNTED_AT = path.dirname(path.abspath(__file__))
DEV        = USB(MOUNTED_AT)



def zero_out(dev_path):
  system('dd if=/dev/zero of='+dev_path.strip(digits))

if __name__ == '__main__':
  if len(argv) > 1:
    if argv[1] == '-y':
      print('Scrub scrub...')
      zero_out(DEV.data.source)
      print('Done.')
      
  print('This will zero out every byte on the drive; All data will NOT BE RECOVERABLE')
  if raw_input('Please response with [Y/N]: ').lower().startswith('y'):
    print('Scrub scrub...')
    zero_out(DEV.data.source)
    print('Done.')
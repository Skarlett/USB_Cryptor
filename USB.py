from os import path
from collections import namedtuple
from subprocess import Popen, PIPE

def sys(cmd):
  return Popen(cmd, stdout=PIPE, shell=True).stdout.read()


class USB:
  '''

  Depends on findmnt to find source from target and extra information like fs type

  '''
  
  def __init__(self, target):
    try:
      assert path.exists(target) and not path.isfile(target)
    except AssertionError:
      raise AssertionError('Needs target (mounted to)')
    if path.isdir(target):
      self.data = self._get_info(target, 'T')
    else:
      self.data = self._get_info(target, 'S')

  def _get_info(self, d, v, splitchar='|'):
      for i, x in enumerate(sys("findmnt -%s \"%s\"" % (v, d)).split('\n')):
        if i > 0:
          return namedtuple('USB_info', 'target source fstype options')(*splitchar.join(x.split()).split(splitchar, 3))
  
  
  def __repr__(self):
    return '<%s | %s>' % (self.data.source, self.data.target)
  
# print USB('/dev/sdb1').data

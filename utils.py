from subprocess import PIPE, Popen
from os import remove, path, getegid


def sys(cmd):
  return Popen(cmd, stdout=PIPE, shell=True).stdout.read()

def copy_file(fp, to):
  try:
    with open(fp, 'rb') as reader:
      with open(to, 'wb') as writer:
        for line in reader:
          writer.write(line)
  except Exception as e:
    if path.isfile(to):
      remove(to)
    raise e
  return True

def move_file(fp, to, force=False):
  if path.isfile(to) and not force:
    return False
  elif path.isfile(to) and force:
    copy_file(fp, to)
    remove(fp)
    return True
  else:
    copy_file(fp, to)
    remove(fp)
    return True
  
  

def humansize(nbytes, suffix=None):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    final = []
    
    if not suffix == None:
      for x in suffixes:
        final.append(x)
        if x == suffix:
          break
    
    else: final.extend(suffixes)
    del suffixes
    
    if nbytes == 0: return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(final)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, final[i])

def getDevEstimate(dev_path):
  try:
    assert getegid() == 0
  except:
    raise AssertionError('Root privs required.')
  
  return int(round(float(humansize(int(sys('blockdev --getsize64 ' + dev_path).strip()), suffix='MB').split(' ')[0])))-1200

print getDevEstimate('/dev/sdb1')


class cmtab:
  def __init__(self, target, source, name, keyfile, **kwargs):
    self.name = name
    self.dir = target  # /media/$USER/$MEDIANAME        | or in this case ~/crypto/unlocked_(name)
    self.source = source  # /dev/sdX                    | or in this case ~/crypto/crypto.fs
    self.fstype = 'ext3'
    self.mountoptions = 'defaults'
    self.cipher = 'aes'
    self.keyformat = 'builtin'
    self.keyfile = keyfile
    
    for _id, val in kwargs.items():
      if hasattr(self, _id) and type(getattr(self, _id)) == type(val):
        setattr(self, _id, val)
   
   
  def make(self):
    configuration = [('dev', self.source), ('dir', self.dir),
                     ('fstype', self.fstype), ('mountoptions', self.mountoptions),
                     ('cipher', self.cipher), ('keyformat', self.keyformat),
                     ('keyfile', self.keyfile)]
    
    for id, val in configuration:
      assert len(val) > 0
    
    data = self.name + ' {\n'
    for tag, val in configuration:
      data += '  %s=%s\n' % (tag, val)
    data += '}'
    return data


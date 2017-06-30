from mountutils import *


def execute(command):
  call(command)
  call(["sync"])


def raw_format(device_path, fstype, volume_label, uid, gid):
  do_umount(device_path)
  
  partition_path = "%s1" % device_path
  if fstype == "fat32":
    partition_type = "fat32"
  if fstype == "ntfs":
    partition_type = "ntfs"
  elif fstype == "ext4":
    partition_type = "ext4"
  
  # First erase MBR and partition table , if any
  execute(["dd", "if=/dev/zero", "of=%s" % device_path, "bs=512", "count=1"])
  
  # Make the partition table
  execute(["parted", device_path, "mktable", "msdos"])
  
  # Make a partition (primary, with FS ID ext3, starting at 1MB & using 100% of space).
  # If it starts at 0% or 0MB, it's not aligned to MB's and complains
  execute(["parted", device_path, "mkpart", "primary", partition_type, "1", "100%"])
  
  # Call wipefs on the new partitions to avoid problems with old filesystem signatures
  execute(["wipefs", "-a", partition_path, "--force"])
  
  # Format the FS on the partition
  if fstype == "fat32":
    execute(["mkdosfs", "-F", "32", "-n", volume_label, partition_path])
  if fstype == "ntfs":
    execute(["mkntfs", "-f", "-L", volume_label, partition_path])
  elif fstype == "ext4":
    execute(["mkfs.ext4", "-E", "root_owner=%s:%s" % (uid, gid), "-L", volume_label, partition_path])

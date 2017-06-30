# USB_Cryptor
This project is designed to create an encrypted Filesystem onto your USB device.
Currently this project only works on linux like systems.

It's only been tested on `16.04 Ubuntu | 4.4.0-53-generic`


##Features 

  - Portable USB Encryption
  
  - AES 256 and Luks Encryption

  - Acts just like it's own Storage device


## Recommendations

  - 16+ GB Drive
  - +3.0 USB Port and Device
  

This software has *many* heavy dependencies. Most of them are essential defaults, but a couple will need to be added, if not already added implemented into the installer.


##### Dependencies

  - Python 2.7
  - findmnt
  - cryptmount
  
  ---
Some lower level requirements...

  - udev
  - bash logic
  - blockdev
  - dd
  - parted
  - wipefs
  - mkfs

  ---
  
##### Install Instructions
##### mapscheme:
  
  - \# comment
  - [Required]
  - (explaination)
  - {optional}


    

        git clone Https//github.com/ixtabinnovations/USB_Cryptor
        cd USB_Cryptor/
        
        # Install on USB
        sudo ./install.py [TempDirectoryToUse] {/dev/sdXN}
        
        # Now we can switch to the usb and load the encrypted FS
        cd /media/user/usb/
        sudo ./load.py m ~/usb/ (Mount to Directory)
        
        # And finally unmount
        sudo ./load.py u
    
##### Component Structure
So how does it all work? The script is designed to automatically make and attempt to inject its own configurations. First, it will identify the device you'd like to use for installation. If multiple USB devices are present, you will be prompted to select one. Otherwise it will choose the only one you have mounted into the machine. If none are present/findable it will return an error and/or message. It will then format the device into `ext4`. Finally it just has to make the file system, keys, and then inject and mount the new filesystem.


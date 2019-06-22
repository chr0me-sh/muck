# muck
#### Multiboot USB Creation Kit
___

Muck has been created with the aim of providing a tool that, given a number of bootable images and a USB, is able to seamlessly create a multiboot device containing the images of your choosing. 

At this stage I have decided to make use of the *memdisk* kernel module, which will hopefully result in a wide range of bootable software being supported with minimal configuration changes. The caveat to this being that Syslinux must be used (which isn't as pretty as GRUB) and that a the machine booting the images must contain enough RAM to load the image into memory.



import parted
import os
import subprocess
import re
import glob
import shutil

def show_devices():
    """Prints a list of storage devices and some attributes."""
    print("{:<15} {:<30} {:<}".format("Device Path", "Device Model",
                                      "Capacity (MB)"))

    for device in parted.getAllDevices():
        print("{:<15} {:<30} {:<}".format(device.path, device.model,
                                          device.getSize()))


def select_device():
    """Returns a device object, retrieved from the users selection.
       Loops until a valid device is chosen, and the user has confirmed
       their selection."""
    show_devices()

    while True:
        device_path = input("\nInput the device to use: ")
        try:
            device = parted.getDevice(device_path)
        except parted.IOException:
            print(device_path + ": Cannot retrieve device.")
            pass

        print("\nALL DATA ON", device_path, "WILL BE LOST!")

        confirm = input("Really use this device? (y/N): ")
        if confirm != "y":
            print("Lets try that again.")
            pass
        else:
            return device


def wipe_device(device_path):
    """Recieves a device object
       Destroys all device metadata"""
    with open(device_path, "wb") as d:
        d.write(bytearray(1024))

def wipe(device):
    partitions = glob.glob('{}[0-9]*'.format(device.path))    

    for part in partitions:
        wipe_device(part)

    wipe_device(device.path)

def unmount(device):
    with open("/proc/mounts", 'r') as f:
        for line in f:
            m = re.match(device.path + "[0-9]", line)
            if m:
                print(f"Unmounting {m.group(0)}...")
                subprocess.run(["umount", m.group(0)])


def partition(device):
    """Recieves a device object.
       Wipes the device and creates a single partition."""


    wipe(device)

    disk = parted.freshDisk(device, 'msdos')
    geometry = parted.Geometry(device=device, start=1, length=device.getLength() - 1)
    filesystem = parted.FileSystem(type='ext4', geometry=geometry)
    partition = parted.Partition(disk=disk, type=parted.PARTITION_NORMAL,
                                 fs=filesystem, geometry=geometry)

    disk.addPartition(partition=partition,
                      constraint=device.optimalAlignedConstraint)

    partition.setFlag(parted.PARTITION_BOOT)

    disk.commit()


def format(partition_path):
    subprocess.run(["mkfs.ext4", partition_path])


def mount(partition_path, mount_path):
    if not os.path.isdir(mount_path):
        os.makedirs(mount_path)

    subprocess.run(["mount", partition_path, mount_path])


def install_syslinux(device_path, mount_dir):
    syslinux_dir = mount_dir + "/syslinux/"
    os.mkdir(syslinux_dir) 

    subprocess.run(["extlinux", "--install", syslinux_dir])
    subprocess.run(["dd", "bs=440", "count=1", "conv=notrunc",
                    "if=/usr/lib/syslinux/mbr/mbr.bin", "of=" + device_path])

    shutil.copyfile('/usr/lib/syslinux/memdisk', syslinux_dir + 'memdisk')

def create_muck_disk(device):
    partition = device.path + "1"
    mount_dir = "/tmp/muck/mnt"

    unmount(device)
    format(partition)
    mount(partition, mount_dir)

    install_syslinux(device.path, mount_dir)






print("Welcome to MUCK!\n")

working_device = select_device()
partition(working_device)
create_muck_disk(working_device)

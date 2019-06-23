import parted
import os
import subprocess
import glob

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


def wipe_device(device):
    """Recieves a device object
       Destroys all device metadata"""
    with open(device.path, 'wb') as d:
        d.write(bytearray(1024))

def prep_device(device):
    """Recieves a device object.
       Wipes the device and creates a single partition."""

    wipe_device(device)

    disk = parted.freshDisk(device, 'msdos')
    geometry = parted.Geometry(device=device, start=1, length=device.getLength() - 1)
    filesystem = parted.FileSystem(type='ext4', geometry=geometry)
    partition = parted.Partition(disk=disk, type=parted.PARTITION_NORMAL,
                                 fs=filesystem, geometry=geometry)

    disk.addPartition(partition=partition,
                      constraint=device.optimalAlignedConstraint)

    partition.setFlag(parted.PARTITION_BOOT)

    disk.commit()


def init_muck_disk(device):
    partition_path = device.path + "1"
    subprocess.run(["mkfs.ext4", partition_path])

    mount_path = "/tmp/muck/mnt"

    if not os.path.isdir(mount_path):
        os.makedirs(mount_path)

    subprocess.run(["mount", partition_path, mount_path])



print("Welcome to MUCK!\n")

working_device = select_device()


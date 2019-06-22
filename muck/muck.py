import parted

def prep_device(device):
    with open(device.path, 'wb') as p:
        p.write(bytearray(1024))

    disk = parted.freshDisk(device, 'msdos')
    geometry = parted.Geometry(device=device, start=1, length=device.getLength() - 1)
    filesystem = parted.FileSystem(type='ext4', geometry=geometry)
    partition = parted.Partition(disk=disk, type=parted.PARTITION_NORMAL,
                                 fs=filesystem, geometry=geometry)

    disk.addPartition(partition=partition,
                      constraint=device.optimalAlignedConstraint)

    partition.setFlag(parted.PARTITION_BOOT)

    disk.commit()


def show_devices():
    print("{:<15} {:<30} {:<}".format("Device Path", "Device Model",
                                      "Capacity (MB)"))

    for device in parted.getAllDevices():
        print("{:<15} {:<30} {:<}".format(device.path, device.model,
                                          device.getSize()))


def select_device():
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


print("Welcome to MUCK!\n")

working_device = select_device()
prep_device(working_device)




#try:
#    device = parted.getDevice(device_path)
#except parted.IOException:
#    print(device_path + ": Device cannot be accessed or does not exist!")
#    sys.exit(1)
#else:
#    print("Device valid. Continuing...")

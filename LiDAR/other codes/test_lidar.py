from rplidar import RPLidar

lidar = RPLidar('/dev/cu.SLAB_USBtoUART')
print(lidar.get_info())
print(lidar.get_health())

for i, scan in enumerate(lidar.iter_scans()):
    print(f'Scan {i+1}: {len(scan)} points')
    if i >= 4:
        break

lidar.stop()
lidar.disconnect()

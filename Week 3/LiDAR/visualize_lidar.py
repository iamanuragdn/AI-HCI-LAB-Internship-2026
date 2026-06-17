import serial
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

PORT = '/dev/cu.SLAB_USBtoUART'
BAUD = 460800

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(0.1)

# Stop then start scan
ser.write(b'\xA5\x25')
time.sleep(0.1)
ser.reset_input_buffer()
ser.write(b'\xA5\x20')
time.sleep(0.1)
ser.read(7)  # discard descriptor

# Setup plot
fig = plt.figure(figsize=(8, 8), facecolor='black')
ax = fig.add_subplot(111, projection='polar', facecolor='black')
ax.set_ylim(0, 6000)
ax.set_title('RPLIDAR C1 - Live Scan', color='white', pad=20)
ax.tick_params(colors='white')
ax.grid(color='green', alpha=0.3)
scat = ax.scatter([], [], s=2, c='lime', alpha=0.8)

scan_angles = []
scan_dists = []

def update(frame):
    global scan_angles, scan_dists

    new_angles, new_dists = [], []
    for _ in range(500):
        raw = ser.read(5)
        if len(raw) < 5:
            continue
        b0, b1, b2, b3, b4 = raw
        angle = ((b1 | (b2 << 8)) >> 1) / 64.0
        distance = (b3 | (b4 << 8)) / 4.0
        if distance > 0:
            new_angles.append(np.radians(angle))
            new_dists.append(distance)

    if new_angles:
        scan_angles = new_angles
        scan_dists = new_dists

    scat.set_offsets(np.c_[scan_angles, scan_dists])
    return scat,

ani = animation.FuncAnimation(fig, update, interval=100, blit=False)

try:
    plt.tight_layout()
    plt.show()
except KeyboardInterrupt:
    pass
finally:
    ser.write(b'\xA5\x25')
    ser.close()

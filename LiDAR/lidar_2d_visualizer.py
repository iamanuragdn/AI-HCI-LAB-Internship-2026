import serial
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

PORT = '/dev/cu.SLAB_USBtoUART'
BAUD = 460800

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(0.1)
ser.write(b'\xA5\x25')
time.sleep(0.1)
ser.reset_input_buffer()
ser.write(b'\xA5\x20')
time.sleep(0.1)
ser.read(7)  # discard descriptor

fig = plt.figure(figsize=(8, 8), facecolor='black')
ax = fig.add_subplot(111, projection='polar', facecolor='black')
ax.set_ylim(0, 6000)
ax.set_title('RPLIDAR C1 - Live Scan', color='lime', pad=20, fontsize=14)
ax.tick_params(colors='gray')
ax.grid(color='green', alpha=0.2)
scat = ax.scatter([], [], s=3, c='lime', alpha=0.9)

# Store one full sweep worth of data
sweep_angles = np.zeros(360)
sweep_dists = np.zeros(360)

def update(frame):
    # Read a big chunk — enough for a full sweep (~500 points per rotation)
    for _ in range(800):
        raw = ser.read(5)
        if len(raw) < 5:
            continue
        b0, b1, b2, b3, b4 = raw
        angle = ((b1 | (b2 << 8)) >> 1) / 64.0
        distance = (b3 | (b4 << 8)) / 4.0
        if distance > 0 and distance < 6000:
            idx = int(angle) % 360
            sweep_angles[idx] = np.radians(angle)
            sweep_dists[idx] = distance

    # Only plot non-zero points
    mask = sweep_dists > 0
    scat.set_offsets(np.c_[sweep_angles[mask], sweep_dists[mask]])
    scat.set_array(sweep_dists[mask])  # color by distance
    return scat,

ani = animation.FuncAnimation(fig, update, interval=150,
                               blit=False, cache_frame_data=False)

try:
    plt.tight_layout()
    plt.show()
except KeyboardInterrupt:
    pass
finally:
    ser.write(b'\xA5\x25')
    ser.close()
    print("Stopped.")

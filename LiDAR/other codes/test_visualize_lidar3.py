import serial
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from collections import deque

PORT = '/dev/cu.SLAB_USBtoUART'
BAUD = 460800

ser = serial.Serial(PORT, BAUD, timeout=0.1)
time.sleep(0.1)
ser.write(b'\xA5\x25')
time.sleep(0.1)
ser.reset_input_buffer()
ser.write(b'\xA5\x20')
time.sleep(0.1)
ser.read(7)

# 3600 slots = 0.1 degree resolution
SLOTS = 3600
sweep_angles = np.full(SLOTS, np.nan)
sweep_dists  = np.full(SLOTS, np.nan)

fig = plt.figure(figsize=(9, 9), facecolor='#0a0a0a')
ax  = fig.add_subplot(111, projection='polar', facecolor='#0a0a0a')
ax.set_ylim(0, 5000)
ax.set_theta_zero_location('N')   # 0° at top like a compass
ax.set_theta_direction(-1)         # clockwise
ax.set_title('RPLIDAR C1', color='lime', fontsize=15, pad=22)
ax.tick_params(colors='#555555')
ax.grid(color='#1a3a1a', linewidth=0.8)
for spine in ax.spines.values():
    spine.set_edgecolor('#1a3a1a')

# Distance rings labels
ax.set_yticks([1000, 2000, 3000, 4000, 5000])
ax.set_yticklabels(['1m','2m','3m','4m','5m'], color='#555555', fontsize=8)

scat = ax.scatter([], [], s=1.5, cmap='plasma', alpha=0.85, linewidths=0)
fig.colorbar(scat, ax=ax, pad=0.1, shrink=0.6,
             label='Distance (mm)').ax.yaxis.label.set_color('gray')

info_text = ax.text(0, 0, '', transform=ax.transAxes,
                    color='lime', fontsize=9, va='top')

frame_count = [0]

def update(frame):
    frame_count[0] += 1

    # Read all available bytes (non-blocking)
    waiting = ser.in_waiting
    if waiting < 5:
        return scat,

    # Read in multiples of 5
    n = (min(waiting, 5000) // 5) * 5
    raw_all = ser.read(n)

    for i in range(0, len(raw_all) - 4, 5):
        b0,b1,b2,b3,b4 = raw_all[i:i+5]
        angle    = ((b1 | (b2 << 8)) >> 1) / 64.0
        distance = (b3 | (b4 << 8)) / 4.0
        quality  = b0 >> 2

        if 0 < distance < 5000 and quality > 5:
            idx = int(angle * 10) % SLOTS
            sweep_angles[idx] = np.radians(angle)
            sweep_dists[idx]  = distance

    mask = ~np.isnan(sweep_dists)
    if mask.sum() > 0:
        a = sweep_angles[mask]
        d = sweep_dists[mask]
        scat.set_offsets(np.c_[a, d])
        scat.set_array(d)
        scat.set_clim(0, 5000)
        pts = mask.sum()
        info_text.set_text(f'Points: {pts}  Frame: {frame_count[0]}')

    return scat,

ani = animation.FuncAnimation(fig, update, interval=100,
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

import serial
import struct
import time

PORT = '/dev/cu.SLAB_USBtoUART'
BAUD = 460800

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(0.1)

# Stop any ongoing scan first
ser.write(b'\xA5\x25')
time.sleep(0.1)
ser.reset_input_buffer()

# Start scan command
ser.write(b'\xA5\x20')
time.sleep(0.1)

# Read and discard the response descriptor (7 bytes)
descriptor = ser.read(7)
print(f"Descriptor: {descriptor.hex()}")

print("Reading scan data... (press Ctrl+C to stop)\n")

scan_points = []
try:
    while True:
        raw = ser.read(5)  # each data packet is 5 bytes
        if len(raw) < 5:
            continue

        b0, b1, b2, b3, b4 = raw

        # Parse angle and distance
        quality = b0 >> 2
        angle = ((b1 | (b2 << 8)) >> 1) / 64.0
        distance = (b3 | (b4 << 8)) / 4.0  # in mm

        if distance > 0:
            scan_points.append((angle, distance))
            print(f"Angle: {angle:6.2f}°  Distance: {distance:7.1f} mm  Quality: {quality}")

except KeyboardInterrupt:
    print(f"\nTotal points collected: {len(scan_points)}")
    ser.write(b'\xA5\x25')  # stop scan
    ser.close()

import serial
import time

# C1 uses 460800 baud rate (different from older models)
ser = serial.Serial('/dev/cu.SLAB_USBtoUART', 460800, timeout=1)

# Send GET_INFO command
ser.write(b'\xA5\x50')
time.sleep(0.5)

response = ser.read(ser.in_waiting)
print("Raw response:", response.hex())
print("Length:", len(response), "bytes")

ser.close()

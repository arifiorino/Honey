import serial, time
import numpy as np

motors = serial.Serial(port='/dev/tty.usbmodem1101', baudrate = 250000)
time.sleep(2)
print('connected')

def cmd(x):
    motors.write(bytes('G0 %s F300\n'%x, 'utf-8'))

def printShape(points):
  prev = points[0]
  for curr in points[1:]+[points[0]]:
    diff = (curr[0] - prev[0], curr[1] - prev[1])
    motors.write(b'G1 X%f Y%f E0.04 F3.0\n'%diff)
    time.sleep(0.1)
    prev = curr
  cmd('Z5')

motors.write(b'M17\n') #re enable steppers
motors.write(b'G91\n') #relative motion mode
time.sleep(5)
printShape([(0,0),(10,0),(10,10),(0,10)])
time.sleep(5)
motors.close()


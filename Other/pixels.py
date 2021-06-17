import serial, time
import numpy as np
from PIL import Image

#L/R: X
#F/B: Y
#U/D: Z

motors = serial.Serial(port='/dev/tty.usbmodem1101', baudrate = 250000)

cmds = []
cmd = lambda x:cmds.append(b'G0 %s F300\n'%bytes(x,'utf-8'))

def pixel(s, n):
  points = []
  points.append((0,n))
  for i in range(n-1):
    points.append((1+i,n))
    points.append((0,n-1-i))
  points.append((n,n))
  points.append((0,0))
  for i in range(n-1):
    points.append((n,n-1-i))
    points.append((1+i,0))
  points.append((n,0))
  for i in range(len(points)):
    points[i] = (points[i][0]/n*s, points[i][1]/n*s)
  prev = points[0]
  cmds.append(b'G0 X%f Y%f F200\n'%(points[0]))
  for curr in points[1:]:
    diff = (curr[0] - prev[0], curr[1] - prev[1])
    cmds.append(b'G1 X%f Y%f E0.005 F200\n'%diff)
    #motors.write(b'G0 X%f Y%f F50\n'%diff)
    prev = curr
  cmds.append(b'G0 X%f Y%f F200\n'%(-points[-1][0], -points[-1][1]))
  cmds.append(b'G1 E-0.01 F3.0\n')

time.sleep(2)
print('connected')
motors.write(b'M17\n') #re enable steppers
motors.write(b'G91\n') #relative motion mode
for _ in range(50):
  pixel(8, 4)
  cmd('Z10')
  cmd('X8')
  cmd('Z-10')
for c in cmds:
  input('?')
  motors.write(c)
motors.close()

#motors.write(b'G0 X-10.0 F6000\n')
#motors.write(b'G0 X10.0 F6000\n')
#time.sleep(0.1)
#motors.write(b'G0 Y-10.0 F6000\n')
#motors.write(b'G0 Y10.0 F6000\n')
#time.sleep(0.1)
#motors.write(b'G0 Z-10.0 F6000\n')
#motors.write(b'G0 Z10.0 F6000\n')

#Extrude:
#motors.write(b'G1 F3.0\n')
#motors.write(b'G1 E0.05\n')

import serial, time
import numpy as np
from PIL import Image

#66k -> 37
#L/R: X
#F/B: Y
#U/D: Z

motors = serial.Serial(port='/dev/tty.usbmodem1101', baudrate = 250000)

def move(x):
  motors.write(b'G0 %s F300\n'%bytes(x,'utf-8'))
  time.sleep(5)
def extrude(x):
  motors.write(b'G1 E%f F3.0\n'%x)
  time.sleep(5)

time.sleep(2)
print('connected')
motors.write(b'M17\n') #re enable steppers
motors.write(b'G91\n') #relative motion mode
im = Image.open('mona.png')
px = im.load()

#17hr
move('Z5')
move('X5')
for j in range(75):
  for i in range(50):
    alpha = px[i, 49-j]
    if alpha <= 200:
      extrude((1-(alpha/255))*0.01)
      time.sleep(5)
      move('Z-5')
      move('Z5')
    move('X3')
  move('X-12 Y3')
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

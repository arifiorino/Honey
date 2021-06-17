import serial, time
import numpy as np

motors = serial.Serial(port='/dev/tty.usbmodem1101', baudrate = 250000)
time.sleep(2)
print('connected')

def cmd(x):
  if x[0]=='E':
    motors.write(bytes('G1 %s F3.0\n'%x, 'utf-8'))
  else:
    motors.write(bytes('G0 %s F600\n'%x, 'utf-8'))


motors.write(b'M17\n') #re enable steppers
motors.write(b'G91\n') #relative motion mode
time.sleep(5)
while 1:
  cmd(input('?'))
time.sleep(5)
motors.close()


import serial, time
import numpy as np

motors = serial.Serial(port='/dev/tty.usbmodem1101', baudrate = 250000)
time.sleep(2)
print('connected')

def getZ(x,y):
  x1=0
  x2=190
  y1=0
  y2=235
  Q11=0
  Q21=-1.3
  Q22=-1.3
  Q12=-0.6
  A=np.array([x2-x,x-x1])
  B=np.array([[Q11,Q12],[Q21,Q22]])
  C=np.array([y2-y,y-y1]).T
  return (1/((x2-x1)*(y2-y1))) * (A@B@C)

def cmd(x):
  if x[0]=='E':
    motors.write(bytes('G1 %s F3.0\n'%x, 'utf-8'))
  else:
    motors.write(bytes('G0 %s F900\n'%x, 'utf-8'))


motors.write(b'M17\n') #re enable steppers
motors.write(b'G91\n') #relative motion mode
time.sleep(5)
points=[(80,0),(190,0),(0,200),(80,200),(190,200),(0,235),(80,235),(190,235)]
curr=[0,0,0]
for p in points:
  cmd('Z%f'%(20-curr[2]))
  curr[2]=20
  cmd('X%fY%f'%(p[0]-curr[0],p[1]-curr[1]))
  curr[0]=p[0]
  curr[1]=p[1]
  cmd('Z%f'%(-20+getZ(p[0],p[1])))
  curr[2]=getZ(p[0],p[1])
  print(curr)
  input('?')
time.sleep(5)
motors.close()


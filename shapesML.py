import serial, time
import numpy as np
from pyueye import ueye
import numpy as np
import cv2
import sys

motors = serial.Serial(port='COM3', baudrate = 250000)
time.sleep(2)
print('connected')

def getZ(x,y):
  x1,y1=0,0
  x2=190
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
    motors.write(bytes('G0 %s F300\n'%x, 'utf-8'))

def printShape(points, extrusions):
  prev = points[0]
  cmd('E%f'%extrusions[0])
  for i in range(len(points)):
    curr = points[(i+1)%len(points)]
    params = (curr[0] - prev[0], curr[1] - prev[1], extrusions[i+1])
    motors.write(b'G1 X%f Y%f E%f F3.0\n'%params)
    time.sleep(0.1)
    prev = curr
#Camera
#Z+50
#X-62.5
#Y-9
cameraPos = (-62.5,-9,50)
motors.write(b'M17\n') #re enable steppers
motors.write(b'G91\n') #relative motion mode
time.sleep(5)
points =           [(0,0),(3,0),(6,0),(9,0),(9,3),(9,6),(9,9),(6,9),(3,9),(0,9),(0,6),(0,3) ]
#Good:
extrusions = [0.002, 0.01, 0.00, 0.00, 0.01, 0.00, 0.00,  0.01,  0.00, 0.00, 0.01, 0.00, 0.00]

def takePicture():
  hCam = ueye.HIDS(0)
  sInfo = ueye.SENSORINFO()
  cInfo = ueye.CAMINFO()
  pcImageMemory = ueye.c_mem_p()
  MemID = ueye.int()
  rectAOI = ueye.IS_RECT()
  pitch = ueye.INT()
  nBitsPerPixel = ueye.INT(24)
  m_nColorMode = ueye.INT()
  bytes_per_pixel = int(nBitsPerPixel / 8)
  nRet = ueye.is_InitCamera(hCam, None)
  nRet = ueye.is_GetCameraInfo(hCam, cInfo)
  nRet = ueye.is_GetSensorInfo(hCam, sInfo)
  #nRet = ueye.is_ResetToDefault( hCam)
  nRet = ueye.is_SetDisplayMode(hCam, ueye.IS_SET_DM_DIB)
  ueye.is_GetColorDepth(hCam, nBitsPerPixel, m_nColorMode)
  bytes_per_pixel = int(nBitsPerPixel / 8)
  nRet = ueye.is_AOI(hCam, ueye.IS_AOI_IMAGE_GET_AOI, rectAOI, ueye.sizeof(rectAOI))
  width = rectAOI.s32Width
  height = rectAOI.s32Height
  nRet = ueye.is_AllocImageMem(hCam, width, height, nBitsPerPixel, pcImageMemory, MemID)
  nRet = ueye.is_SetImageMem(hCam, pcImageMemory, MemID)
  nRet = ueye.is_SetColorMode(hCam, m_nColorMode)
  nRet = ueye.is_FreezeVideo(hCam, ueye.IS_WAIT)
  nRet = ueye.is_InquireImageMem(hCam, pcImageMemory, MemID, width, height, nBitsPerPixel, pitch)
  array = ueye.get_data(pcImageMemory, width, height, nBitsPerPixel, pitch, copy=False)
  frame = np.reshape(array,(height.value, width.value, bytes_per_pixel))
  frame = cv2.resize(frame,(0,0),fx=0.5, fy=0.5)
  #cv2.imshow("SimpleLive_Python_uEye_OpenCV", frame)
  ueye.is_FreeImageMem(hCam, pcImageMemory, MemID)
  ueye.is_ExitCamera(hCam)
  #cv2.destroyAllWindows()
  return frame
  
while 1:
  cmd(input('?'))
for _ in range(1):
  for _ in range(1):
    #extrusions=np.random.rand(len(extrusions))*0.015
    for e in extrusions:
      print("%.05f"%e,end="\t")
    print()
    #time.sleep(2*60 + 15)
    printShape(points, extrusions)
    cmd('X%fY%fZ%f'%cameraPos)
    #cmd('Z%f'%(20))
    #cmd('X15')
    #cmd('Z%f'%(-20))
  #cmd('Z%f'%(20))
  #cmd('X%fY%f'%(-15*5,15))
  #cmd('Z%f'%(-20))
time.sleep(5)
motors.close()


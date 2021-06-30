import serial, time
import numpy as np
from pyueye import ueye
import numpy as np
import cv2
import sys

motors = serial.Serial(port='COM3', baudrate = 250000)
lights = serial.Serial(port='COM4', baudrate = 9600)
time.sleep(2)
print('connected')

def lightsOn():
  lights.write(b'210101010255\n')

def cmd(x):
  if x[0]=='E':
    motors.write(bytes('G1 %s F3.0\n'%x, 'utf-8'))
  else:
    motors.write(bytes('G0 %s F900\n'%x, 'utf-8'))

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
#X-62.5
#Y-9
#Z+50
cameraPos = (-64,-9.5,50)
motors.write(b'M17\n') #re enable steppers
motors.write(b'G91\n') #relative motion mode
time.sleep(5)
points =           [(0,0),(2.66,0),(5.33,0),(8,0),(8,2.66),(8,5.33),(8,8),(5.33,8),(2.66,8),(0,8),(0,5.33),(0,2.66)]
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
  #cv2.imwrite("C:\\Users\\AM ARES 2\\Desktop\\img.png", frame)

  print(height.value, width.value)
  cv2.imwrite("C:\\Users\\AM ARES 2\\Desktop\\img.png", frame)
  input('1')
  ueye.is_FreeImageMem(hCam, pcImageMemory, MemID)
  ueye.is_ExitCamera(hCam)
  #cv2.destroyAllWindows()
  return frame

lightsOn()
print(takePicture())
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


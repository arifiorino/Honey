from PIL import Image, ImageDraw
import numpy as np
from bayes_opt import BayesianOptimization, UtilityFunction
import time, sys

width, height = 300,300
count=1
  
def drawConfig(E,save=True):
  global count
  image = Image.new('RGB', (width, height), (255,255,255))
  image1 = ImageDraw.Draw(image)
  line = [50,250,250,250]
  if E[0] < 0.006:
    line[0] = 50+(1-(E[0]/0.006))*100
  image1.line(line, fill='black', width=20)
  line = [250,250,250,50]
  if E[4] < 0.01:
    line[1] = 250-(1-(E[4]/0.01))*100
  image1.line(line, fill='black', width=20)
  line = [250,50,50,50]
  if E[7] < 0.01:
    line[0] = 250-(1-(E[7]/0.01))*100
  image1.line(line, fill='black', width=20)
  line = [50,50,50,250]
  if E[10] < 0.01:
    line[1] = 50+(1-(E[10]/0.01))*100
  image1.line(line, fill='black', width=20)
  r = (E[0]+E[1]+E[2]+E[3])/0.016*10
  image1.ellipse([250-r,250-r,250+r,250+r], fill='black')
  r = (E[4]+E[5]+E[6])/0.01*10
  image1.ellipse([250-r,50-r,250+r,50+r], fill='black')
  r = (E[7]+E[8]+E[9])/0.01*10
  image1.ellipse([50-r,50-r,50+r,50+r], fill='black')
  r = (E[10]+E[11]+E[12])/0.01*10
  image1.ellipse([50-r,250-r,50+r,250+r], fill='black')
  if save:
    image.save('img/img_%d.png'%count)
  return image

def scoreImage(image):
  global count
  O = []
  diffImage = Image.new('RGB', (width, height), (255,255,255))
  diffPix = diffImage.load()
  for j in range(299,0,-100):
    for i in range(0,300,100):
      if j==199 and i==100:
        continue
      diff=0
      for i2 in range(100):
        for j2 in range(100):
          x= sum(image.getpixel((i+i2,j-j2))) < 127*3
          xT= sum(targetImage.getpixel((i+i2,j-j2))) < 127*3
          if x==xT:
            diffPix[i+i2,j-j2]=(0,255,0)
          else:
            diffPix[i+i2,j-j2]=(255,0,0)
            diff+=1
      O.append(diff)
  diffImage.save('img/diff_%d.png'%count)
  count+=1
  return O
  
targetImage=drawConfig([0.006,0.01,0,0,0.01,0,0,0.01,0,0,0.01,0,0],False)
#image=drawConfig([0.015, 0.0, 0.0, 0.005676, 0.01015, 0.0, 0.0, 0.009922, 0.0, 0.0, 0.01053, 0.0, 0.0],False)


Es=[]
Os=[]

for _ in range(2):
  E=list(np.random.rand(13)*0.015)
  O=scoreImage(drawConfig(E))
  Es.append(E)
  Os.append(O)

dependsOn = [[0,10,11,12],[0],[0,1,2,3,4],[10],[4],[7,8,9,10],[7],[4,5,6,7]]


def black_box_function(**kwargs):
  E = []
  for i in range(13):
    E.append(kwargs['E%d'%i])
  image = drawConfig(E)
  return -scoreImage(image)

optimizers=[]
for Oi in range(8):
  pbounds = dict()
  for i in dependsOn[Oi]:
    pbounds['E%d'%i]=(0,0.015)
  optimizer = BayesianOptimization(f=black_box_function, pbounds=pbounds)
  optimizers.append(optimizer)

pbounds = dict()
for i in range(13):
  pbounds['E%d'%i]=(0,0.015)

utility = UtilityFunction(kind="ucb", kappa=2.5, xi=0.0)

#register warmup iterations - 1
for i in range(1):
  for Oi in range(8):
    params=dict()
    for j in dependsOn[Oi]:
      params['E%d'%j]=Es[i][j]
    optimizers[Oi].register(params = params, target = -Os[i][Oi])

#multiply objectives
for i in range(100):
  newE = np.zeros(13)
  counts = np.zeros(13,dtype=int)
  for Oi in range(8):
    params=dict()
    for j in dependsOn[Oi]:
      params['E%d'%j]=Es[-1][j]
    #register last iteration
    try:
      optimizers[Oi].register(params = params, target = -Os[-1][Oi])
    except Exception as e:
      print(params)
      #print(-Os[-1][Oi])
      #print(Oi)
      #print(params)
      #print(Es)
      #print(Os)
      #sys.exit()
    best = optimizers[Oi].suggest(utility)
    for j in dependsOn[Oi]:
      counts[j]+=1
      newE[j]+=best['E%d'%j]
  print(counts)
  for i in range(13):
    newE[i] /= counts[i]
  newO=scoreImage(drawConfig(newE))
  Es.append(list(newE))
  Os.append(newO)
  print([round(x,4) for x in newE])
bestI = 0
best = 50000
for i in range(len(Os)):
  if sum(Os[i])<best:
    bestI = i
    best = sum(Os[i])
print('best',best,bestI)
print(Es[bestI])
print(Os[bestI])

import dronesim as airsim
import numpy as np
import time
import cv2
import sys

import time
import threading


client = airsim.VehicleClient(ip="192.168.1.100")
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)

#client.takeoff()
#print("takeoff over!")
start=time.time()


class PID:
  def __init__(self):
    self.dest=0
    self.Kp=4.2
    self.Ki=0.078
    self.Kd=0.02
    self.preerror=0
    self.prederror=0
    self.out=0
    self.buf=[0,0,0,0,0]

  def setdest(self,dest):
    self.dest=dest

  def GetTime(self):#获取程序运行时间
    Time=time.time()-start
    Time=round(Time,3)
    return Time

  def update(self,feedback):
    global now
    self.buf.insert(len(self.buf),feedback)
    self.buf.remove(self.buf[0])
    a = np.array(self.buf)
    b = np.mean(a,axis=0)
    #print(b)#打印当前高度

    #print(client.getBarometerData().altitude)#打印当前高度
    error=self.dest-b
    #if error<0.1 and error>-0.1: error=0
    derror=error-self.preerror
    dderror=derror-self.prederror
    self.preerror=error
    self.prederror=derror

    deltu = self.Kp*derror + self.Ki*error + self.Kd*dderror
    self.out+=deltu

    if self.out>1.0:self.out=1.0
    elif self.out<0.0:self.out=0.0

    return self.out

pid = PID()

def FlyAhead(Time,height):
  global throttle,pitch,yaw_rate

  pitch=0.0
  roll=0.0
  throttle=0.6125
  yaw_rate=0.0
  t=pid.GetTime()#开始时程序运行的总时间
  print(t)

  while(pid.GetTime()<=Time+t):
    h = client.getBarometerData().altitude
    throttle = pid.update(h)
    client.moveByAngleThrottle(pitch,roll,throttle,yaw_rate,0.01)
    #print(client.getImuData())
    #time.sleep(0.01)
    #print(throttle)
    pid.setdest(height)
    #print(pid.GetTime())#打印时间

    pitch=-0.08

def FlyHorizontal(Time,height,side):#横向移动 4向左 6向右
  global throttle,pitch,yaw_rate
  #pid = PID()

  pitch=0.0
  roll=0.0
  throttle=0.6125
  yaw_rate=0.0
  t=pid.GetTime()#开始时程序运行的总时间
  print(t)

  while(pid.GetTime()<=Time+t):
    h = client.getBarometerData().altitude
    throttle = pid.update(h)
    client.moveByAngleThrottle(pitch,roll,throttle,yaw_rate,0.01)

    pid.setdest(height)
    if(side==4):
      roll=-0.1
    elif(side==6):
      roll=0.1

def TurnAngle(Time,side,height):#转动 4向左 6向右
  global throttle,pitch,yaw_rate
  #pid = PID()

  pitch=0.0
  roll=0.0
  throttle=0.6125
  yaw_rate=0.0
  t=pid.GetTime()#开始时程序运行的总时间
  print(t)

  while(pid.GetTime()<=Time+t):
    h = client.getBarometerData().altitude
    throttle = pid.update(h)
    client.moveByAngleThrottle(pitch,roll,throttle,yaw_rate,0.01)

    pid.setdest(height)
    if(side==4):
      yaw_rate=-0.5
    elif(side==6):
      yaw_rate=0.5

FlyAhead(3,20)
time.sleep(3)
TurnAngle(3,4,20)

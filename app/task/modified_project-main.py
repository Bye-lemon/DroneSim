# 准备运行示例：PythonClient / multirotor / hello_drone.py
import dronesim as airsim
import time
import numpy as np

from app.driver.cross import Cross
from app.vision.number import Number

import math
import cv2

t1 = time.time()
# 连接到AirSim模拟器
client = airsim.VehicleClient()
client.connection()

uav = airsim.VehicleMotion(client)
uav.start()

image = airsim.VehicleImage(client)
number = Number(image)


# 定位地面高度
takeoffHigh = client.getBarometerData().altitude
print('takeoffHigh =', round(takeoffHigh, 4))

cross = Cross(client, image, number, uav, takeoffHigh)

# 起飞
# client.takeoff()
uav.flyCmd('up', 'fast')
time.sleep(5)
uav.flyCmd('stop')
time.sleep(3)

# 定位初始方向
x0 = client.getMagnetometerData().magnetic_field_body.x_val
y0 = client.getMagnetometerData().magnetic_field_body.y_val

num = 1
# 1
cross.adjustPositionCentripetally()
cross.moveToCircle()
cross.adjustDrone()
cross.saveFrontSense(num)
num += 1

while(num <= 10):
    cross.moveCircle_N()
    cross.adjustDrone()
    cross.saveFrontSense(num)
    num += 1

t2 = time.time()
print('10-Circle complete time:', (t2-t1)/60, 'min')

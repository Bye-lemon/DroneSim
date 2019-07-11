# 准备运行示例：PythonClient / multirotor / hello_drone.py
import dronesim as airsim
import time
import numpy as np
from PIL import Image
import scipy.misc
import cv2
import warnings

#消除警告
warnings.simplefilter('ignore')

# 连接到AirSim模拟器
client = airsim.MultirotorClient()  # 将client变量赋予无人机操作者的属性
# 用confirmConnection方法每1秒检查一次连接状态，并在Console中报告，以便用户可以看到连接的进度。
client.confirmConnection()
client.enableApiControl(True)  # 使无人机可以通过API控制
client.armDisarm(True)  # enableApiControl和armDisarm同时使用以将车辆设为原始启动状态


# 前进n次


def moveNTimes(n):
    for i in range(1, n):
        client.moveByAngleThrottle(-90, 0, 5, 0, 0.25)
        time.sleep(1)


# 读取相机图像


def getCameraImage(image_num=0):
    responses = client.simGetImages([
        airsim.ImageRequest(0, airsim.ImageType.Scene),
        airsim.ImageRequest(0, airsim.ImageType.DepthPerspective, True, False),
        airsim.ImageRequest(3, airsim.ImageType.Scene)])
    return responses[image_num]


# 拍照并保存


def saveFrontSense(num):
    rawImageF=client.getFrontSense()
    rawImageD=client.getDepthImage()
    rawImageF=rawImageF[:,:,0]
    rawImageF[np.where(rawImageD==255)]=0
    rawImageF[np.where(rawImageF<200)]=0
    fileName = 'Number' + str(num) + '.jpg'
    cv2.imwrite(fileName, rawImageF)

    '''
   response = image(1)         #'height': 480,'  'width': 640  image_data_uint8': b'\x00',
   rawImage = np.array(response.image_data_float)       # (307200,) 307200 float64
   rawImage = rawImage.reshape(response.height, response.width)  #(480, 640)  307200   float64
   #print(rawImage)
   '''

# 调节左右对准


def adjustPositionHorizontally():
    while (True):
        rawImage = client.getDepthImage()
        L = 0
        R = 0
        [rows, cols] = rawImage.shape
        rawImage = np.delete(rawImage, np.s_[361:rows], axis=0)
        rawImage = np.delete(rawImage, np.delete(
            np.arange(0, 361), np.s_[::10], axis=0), axis=0)
        rawImage = np.delete(rawImage, np.delete(
            np.arange(0, cols), np.s_[::10], axis=0), axis=1)
        rawImage[np.where(rawImage == 255)] = 0
        rawImage = np.hsplit(rawImage, 2)
        for i in rawImage[0].flat:
            L += i
        for i in rawImage[1].flat:
            R += i
        print('L =', L, ' R =', R)
        if L < R * 1.6 and R < L * 1.6:
            break
        # 微观调控部分
        if L >= R * 1.6 and R != 0:
            client.moveByAngleThrottle(0, -90, 5, 0, 0.1)
            time.sleep(1)
        elif L >= R * 1.6 and R == 0:
            client.moveByAngleThrottle(0, -90, 5, 0, 0.2)
            time.sleep(1)
        if R >= L * 1.6 and L != 0:
            client.moveByAngleThrottle(0, 90, 5, 0, 0.1)
            time.sleep(1)
        elif R >= L * 1.6 and L == 0:
            client.moveByAngleThrottle(0, 90, 5, 0, 0.2)
            time.sleep(1)


# 移动至检测环：前进：8；左移：4；右移：6；


def moveToCircle(turn=8):
    z = 0
    while (True):
        # 检测
        rawImage = client.getDepthImage()
        up = 0
        [rows, cols] = rawImage.shape
        rawImage = np.delete(rawImage, np.arange(320, rows), axis=0)
        rawImage = np.delete(rawImage, np.delete(
            np.arange(0, 320), np.s_[::10], axis=0), axis=0)
        rawImage = np.delete(rawImage, np.delete(
            np.arange(0, cols), np.s_[::10], axis=0), axis=1)
        rawImage[np.where(rawImage == 255)] = 0
        for i in rawImage.flat:
            up += i
        if up >= 50:
            break
        # 前进
        if turn == 8:
            client.moveByAngleThrottle(-90, 0, 5, 0, 0.25)
            time.sleep(1)
            z += 1
            if z == 2:
                client.moveByAngleThrottle(0, 0, -5, 0, 0.2)
                time.sleep(1)
                z = 0
        # 左移
        if turn == 4:
            client.moveByAngleThrottle(0, -90, 3, 0, 0.2)
            time.sleep(1)
            z += 1
            if z == 2:
                client.moveByAngleThrottle(0, 0, -5, 0, 0.2)
                time.sleep(1)
                z = 0
        # 右移
        if turn == 6:
            client.moveByAngleThrottle(0, 90, 3, 0, 0.2)
            time.sleep(1)
            z += 1
            if z == 2:
                client.moveByAngleThrottle(0, 0, -5, 0, 0.2)
                time.sleep(1)
                z = 0


# 宏观调节高度
def coarseAdjustPositionVertically(H):
    while (True):
        dH = client.getBarometerData().altitude - takeoffHigh
        if dH <= H + 0.7 and dH >= H - 0.7:
            break
        elif dH < H - 0.7:
            client.moveByAngleThrottle(0, 0, 3, 0, 0.5)
            time.sleep(1)
        elif dH > H + 0.7:
            client.moveByAngleThrottle(0, 0, -3, 0, 0.5)
            time.sleep(2)
# 微观调节高度
def fineAdjustPositionVertically(H):
    while (True):
        dH = client.getBarometerData().altitude - takeoffHigh
        if dH <= H + 0.2 and dH >= H - 0.2:
            break
        elif dH < H - 0.2:
            client.moveByAngleThrottle(0, 0, 3, 0, 0.15)
            time.sleep(1)
        elif dH > H + 0.2:
            client.moveByAngleThrottle(0, 0, -3, 0, 0.2)
            time.sleep(1)
        print('High now =', round(client.getBarometerData().altitude - takeoffHigh, 4))

# 估算大概高度

def getHeight():
    dH = client.getBarometerData().altitude - takeoffHigh
    if dH < 0.95:
        print('High now =', dH, 'High gusuan =', 0.4)
        return 0.4
    elif dH >= 0.95 and dH < 2:
        print('High now =', dH, 'High gusuan =', 1.45)
        return 1.45
    elif dH >= 2:
        print('High now =', dH, 'High gusuan =', 3.45)
        return 3.5

# 二次检查高度
'''
def checkHeight():
    while (True):
        rawImage = client.getDepthImage()
        rawImage[np.where(rawImage == 255)] = 0
        U = 0
        D = 0
        up = 0
        [rows, cols] = rawImage.shape
        rawImageu = np.delete(rawImage, np.arange(120, rows), axis=0)
        for i in rawImageu[np.nonzero(rawImageu)]:
            up += i
        if up <= 5100:
            client.moveByAngleThrottle(0, 0, -5, 0, 0.2)
            time.sleep(1)
            continue
        rawImage = np.delete(rawImage, np.arange(384, rows), axis=0)
        rawImage = np.delete(rawImage, np.delete(
            np.arange(0, 384), np.s_[::8], axis=0), axis=0)
        rawImage = np.delete(rawImage, np.delete(
            np.arange(0, 640), np.s_[::10], axis=0), axis=1)
        rawImage = np.vsplit(rawImage, 2)
        for i in rawImage[0].flat:
            U += i
        for i in rawImage[1].flat:
            D += i
        print('U =', U, ' D =', D, ' up =', up)
        if up <= 100:
            client.moveByAngleThrottle(0, 0, -5, 0, 0.2)
            time.sleep(1)
            continue
        if U < D * 1.8 and D < U * 1.8:
            break
        # 微观调控部分
        elif D >= U * 1.8 and U != 0:
            client.moveByAngleThrottle(0, 0, 5, 0, 0.1)
            time.sleep(1)
        elif U >= D * 1.8 and D != 0:
            client.moveByAngleThrottle(0, 0, -5, 0, 0.1)
            time.sleep(1)
'''

#检测数字位置-调整过环高度


def checkNumber():
    while(True):
        rawImageF=client.getFrontSense()
        rawImageD=client.getDepthImage()
        rawImageF=rawImageF[:,:,0]
        rawImageF[np.where(rawImageD==255)]=0
        rawImageF[np.where(rawImageF<200)]=0

        rawImageD[np.where(rawImageD == 255)] = 0
        up = 0
        [rows, cols] = rawImageD.shape
        rawImageD= np.delete(rawImageD, np.arange(120, rows), axis=0)
        for i in rawImageD.flat:
            up += i
        if up <= 5100:
            client.moveByAngleThrottle(0, 0, -5, 0, 0.2)
            time.sleep(1)
            continue
        U=0
        W=0
        D=0
        rawImage=np.vsplit(rawImageF,5)
        rawImageU=np.add(rawImage[0],rawImage[1])
        rawImageU=np.add(rawImageU,rawImage[2])
        rawImageD=np.delete(rawImage[4],np.arange(0,90),axis=0)
        for i in rawImageU.flat:
            U+=i
        for i in rawImage[3].flat:
            W+=i
        for i in rawImageD.flat:
            D+=i
        print('U =',U,' W =',W,' D =',D)
        if U>5000:
            if U>500000:
                client.moveByAngleThrottle(0,0,5,0,0.3)
                time.sleep(1)
            else:
                client.moveByAngleThrottle(0,0,5,0,0.15)
                time.sleep(1)
            continue
        if W<200000 or D>5000:
            client.moveByAngleThrottle(0,0,-5,0,0.15)
            time.sleep(1)
            continue

        break

# 测距

def getDistance():
    rawImage = client.getDepthImage()
    ju = 0
    n = 0
    [rows, cols] = rawImage.shape
    rawImage[np.where(rawImage == 255)] = 0
    rawImage = np.delete(rawImage, np.arange(320, rows), axis=0)
    for i in rawImage[np.nonzero(rawImage)]:
        ju += i
        n += 1
    if n == 0:
        return 0
    else:
        print('ju =', ju / n)
        return ju / n

# 调节与环的距离

def adjustPositionNormally():
    while (True):
        ce = getDistance()
        if ce < 2.5 and ce > 2:
            break
        elif ce >= 2.5:
            client.moveByAngleThrottle(-90, 0, 3, 0, 0.1)
            time.sleep(1)
        elif ce == 0:
            client.moveByAngleThrottle(90, 0, 3, 0, 0.15)
            time.sleep(1)
            moveToCircle(8)
            adjustPositionHorizontally()
        elif ce > 0 and ce <= 2:
            client.moveByAngleThrottle(90, 0, 3, 0, 0.1)
            time.sleep(1)


# 检测环所处区间


def circleDection():
    response = getCameraImage(0)
    rawImage = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
    planets = cv2.imdecode(rawImage, cv2.IMREAD_UNCHANGED)

    planets[:, :, 0:2] = 0
    planets[np.where(planets < 200)] = 0

    gray_img = cv2.cvtColor(planets, cv2.COLOR_BGR2GRAY)

    img = cv2.medianBlur(gray_img, 5)
    cimg = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    circles = cv2.HoughCircles(
        img, cv2.HOUGH_GRADIENT, 1, 15, param1=100, param2=30, minRadius=0, maxRadius=100)

    circles = np.uint16(np.around(circles))
    huan_x = 320
    huan_y = 240
    for i in circles[0, :]:
        if i[2] > circles[0][0][2]:
            circles[0] = i
    huan_x = circles[0][0][0]
    huan_y = circles[0][0][1]
    print('-- x =', circles[0][0][0], 'y =',
          circles[0][0][1], 'r =', circles[0][0][2])
    if huan_x > 380:
        return 1
    elif huan_x < 260:
        return 2
    elif huan_y < 200:
        return 3
    elif huan_y > 280:
        return 4
    else:
        return 0


# 检测扫描环的错误


def getCircle():
    try:
        Z = circleDection()
    except AttributeError:
        print("AtAttributeError time + 1")
        time.sleep(1)
        Z = getCircle()
        return Z
    else:
        return Z


# 横移调节至正对环


def adjustPositionCentripetally():
    while (True):
        Z = getCircle()
        if Z == 0:
            if getCircle() != 0:
                continue
            break
        elif Z == 1:
            client.moveByAngleThrottle(0, 90, 5, 0, 0.2)
            time.sleep(1)
        elif Z == 2:
            client.moveByAngleThrottle(0, -90, 5, 0, 0.2)
            time.sleep(1)
        elif Z == 3:
            client.moveByAngleThrottle(0, 0, 5, 0, 0.3)
            time.sleep(1)
        elif Z == 4:
            client.moveByAngleThrottle(0, 0, -5, 0, 0.2)
            time.sleep(1)


# 方向归正


def resetGesture():
    while (True):
        x = client.getMagnetometerData().magnetic_field_body.x_val - x0
        y = client.getMagnetometerData().magnetic_field_body.y_val - y0
        print('x =', x, ' y =', y)
        if (x <= 0.01 and x >= -0.01) and y < 0.28:
            break
        elif x < 0 and x > -0.2 and y < 0.28:
            client.moveByAngleThrottle(0, 0, 5, -100, 0.08)
            time.sleep(1)
        elif x > 0 and x < 0.2 and y < 0.28:
            client.moveByAngleThrottle(0, 0, 5, 100, 0.08)
            time.sleep(1)
        elif x < 0 and y < 0.28:
            client.moveByAngleThrottle(0, 0, 5, -100, 0.3)
            time.sleep(1)
        elif x > 0 and y < 0.28:
            client.moveByAngleThrottle(0, 0, 5, 100, 0.3)
            time.sleep(1)
        elif x > 0 and y > 0.28:
            client.moveByAngleThrottle(0, 0, 5, 100, 0.7)
            time.sleep(2)
        elif x < 0 and y > 0.28:
            client.moveByAngleThrottle(0, 0, 5, -100, 0.7)
            time.sleep(2)


# 转向调节至正对环


def adjustGestureCentripetally():
    while (True):
        Z = getCircle()
        if Z == 0:
            if getCircle() != 0:
                continue
            break
        elif Z == 1:
            client.moveByAngleThrottle(0, 0, 5, 100, 0.15)
            time.sleep(1)
        elif Z == 2:
            client.moveByAngleThrottle(0, 0, 5, -100, 0.15)
            time.sleep(1)
        elif Z == 3:
            client.moveByAngleThrottle(0, 0, 5, 0, 0.3)
            time.sleep(1)
        elif Z == 4:
            client.moveByAngleThrottle(0, 0, -5, 0, 0.2)
            time.sleep(1)


# 通用于检测环近处调节


def adjustDrone(High):
    adjustPositionHorizontally()
    adjustPositionNormally()
    adjustPositionHorizontally()
    coarseAdjustPositionVertically(High)
    fineAdjustPositionVertically(High)
    adjustPositionNormally()
    adjustPositionHorizontally()
    checkNumber()
    adjustPositionHorizontally()


# 起飞
client.takeoff()

# 定位初始高度
takeoffHigh = client.getBarometerData().altitude
# 定位初始方向
x0 = client.getMagnetometerData().magnetic_field_body.x_val
y0 = client.getMagnetometerData().magnetic_field_body.y_val


print('takeoffHigh =', round(takeoffHigh, 4), end=' ')
time.sleep(1)

# 第1
adjustPositionCentripetally()
High = getHeight()
moveToCircle(8)
adjustDrone(High)
saveFrontSense(1)
print('High of number 1 =', round(
    client.getBarometerData().altitude - takeoffHigh, 4))
moveNTimes(4)
time.sleep(2)

# 第2
adjustPositionCentripetally()
High = getHeight()
moveToCircle(8)
adjustDrone(High)
saveFrontSense(2)
print('High of number 2 =', round(
    client.getBarometerData().altitude - takeoffHigh, 4))
moveNTimes(4)

# 第3
adjustPositionCentripetally()
High = getHeight()
moveToCircle(8)
adjustDrone(High)
saveFrontSense(3)
print('High of number 3 =', round(
    client.getBarometerData().altitude - takeoffHigh, 4))
moveNTimes(4)

# 第4
coarseAdjustPositionVertically(0.5)
fineAdjustPositionVertically(0.5)
High = 0.5
moveToCircle(8)
adjustDrone(High)
saveFrontSense(4)
print('High of number 4 =', round(
    client.getBarometerData().altitude - takeoffHigh, 4))
for i in range(1, 9):  # 前进
    client.moveByAngleThrottle(-90, 0, 5, 0, 0.25)
    time.sleep(1)

# 第5
coarseAdjustPositionVertically(0.5)
fineAdjustPositionVertically(0.5)
moveToCircle(6)
High=getHeight()
adjustDrone(High)
saveFrontSense(5)
print('High of number 5 =', round(
    client.getBarometerData().altitude - takeoffHigh, 4))
moveNTimes(8)

# 第6
coarseAdjustPositionVertically(0.4)
fineAdjustPositionVertically(0.4)
High = 0.4
moveToCircle(6)
adjustDrone(High)
saveFrontSense(6)
print('High of number 6 =', round(
    client.getBarometerData().altitude - takeoffHigh, 4))
moveNTimes(9)

# 第7
coarseAdjustPositionVertically(0.7)
fineAdjustPositionVertically(0.7)
High = 1.2
moveToCircle(4)
adjustDrone(High)
saveFrontSense(7)
print('High of number 7 =', round(
    client.getBarometerData().altitude - takeoffHigh, 4))
moveNTimes(9)
# 第8
fineAdjustPositionVertically(2.5)
High = 3.5
moveToCircle(6)
adjustDrone(High)
saveFrontSense(8)
print('High of number 8 =', round(
    client.getBarometerData().altitude - takeoffHigh, 4))
moveNTimes(6)

# 第9
coarseAdjustPositionVertically(0.5)
moveToCircle(4)
High = 0.4
adjustDrone(High)
saveFrontSense(9)
print('High of number 9 =', round(
    client.getBarometerData().altitude - takeoffHigh, 4))
moveNTimes(9)

# 第10
moveToCircle(4)
High = getHeight()
adjustDrone(High)
saveFrontSense(10)
print('High of number 10 =', round(
    client.getBarometerData().altitude - takeoffHigh, 4))
moveNTimes(4)

client.hover()
time.sleep(5)
client.reset()

from __future__ import print_function
import dronesim as airsim
from dronesim.types import *

import msgpackrpc
import numpy as np
import msgpack
import time
import math
import logging
import numpy as np
import cv2
import pickle


class Cross:
    def __init__(self, client, image, number, motion, takeHigh):
        self.image = image
        self.client = client
        self.number = number
        self.motion = motion
        self.takeHigh = takeHigh
        self.turn = 1
        self.error = 0

    # 读取相机图像

    def getCameraImage(self, image_num=0):
        responses = self.client.simGetImages([
            airsim.ImageRequest(0, airsim.ImageType.Scene),
            airsim.ImageRequest(0, airsim.ImageType.DepthPerspective, True, False),
            airsim.ImageRequest(3, airsim.ImageType.Scene)])
        return responses[image_num]

    # 检测数字前进

    def saveFrontSense(self, num):
        # n=self.number.getNumber()
        n = num
        if (n != num):
            print('number error! getnumber=', n, ' num=', num)
            self.error += 1
            if self.error >= 10:
                self.error = 0
                self.turn = -self.turn
                self.motion.flyCmd('backward', 'fast')
                time.sleep(8)
                self.motion.flyCmd('stop')
                time.sleep(3)
                self.moveCircle_N()
            else:
                self.saveFrontSense(num)
        else:
            print('number ', num, ' right!')
            self.motion.flyCmd('up')
            time.sleep(2)
            self.motion.flyCmd('forward', 'fast')
            time.sleep(3)
            self.motion.flyCmd('stop')
            time.sleep(3)
            self.motion.flyToHeight(self.takeHigh + 3.7, 20)
            self.motion.flyCmd('stop')
            time.sleep(2)

    # 调节左右对准

    def adjustPositionHorizontally(self):
        while (True):
            rawImage = self.image.getDepthImage()
            L = 0
            R = 0
            [rows, cols] = rawImage.shape
            rawImage = np.delete(rawImage, np.s_[361:rows], axis=0)
            rawImage = np.delete(rawImage, np.delete(np.arange(0, 361), np.s_[::10], axis=0), axis=0)
            rawImage = np.delete(rawImage, np.delete(np.arange(0, cols), np.s_[::10], axis=0), axis=1)
            rawImage[np.where(rawImage == 255)] = 0
            rawImage = np.hsplit(rawImage, 2)
            for i in rawImage[0].flat:
                L += i
            for i in rawImage[1].flat:
                R += i
            print('L =', L, ' R =', R)
            if L < R * 1.45 and R < L * 1.45:
                self.motion.flyCmd('stop')
                time.sleep(3)
                break
            # 微观调控部分
            if L >= R * 1.45:
                self.motion.flyCmd('stop')
                self.motion.flyCmd('moveleft')
            if R >= L * 1.45:
                self.motion.flyCmd('stop')
                self.motion.flyCmd('moveright')

    # 移动至检测环：前进：8；左移：4；右移：6；

    def moveToCircle(self, Turn=8):
        # 飞行
        if (Turn == 8):
            self.motion.flyCmd('forward')
        elif (Turn == 6):
            self.motion.flyCmd('moveright')
        elif (Turn == 4):
            self.motion.flyCmd('moveleft')
        while (True):
            # 检测
            rawImage = self.image.getDepthImage()
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
                self.motion.flyCmd('stop')
                time.sleep(3)
                break

    # 检测数字位置-调整过环高度

    def checkNumber(self):
        UD = 0
        while (True):
            rawImageF = self.image.getFrontSense()
            rawImageD = self.image.getDepthImage()
            rawImageF = rawImageF[:, :, 0]
            rawImageF[np.where(rawImageD == 255)] = 0
            rawImageF[np.where(rawImageF < 200)] = 0
            rawImageD[np.where(rawImageD == 255)] = 0
            up = 0
            [rows, cols] = rawImageD.shape
            rawImageD = np.delete(rawImageD, np.arange(120, rows), axis=0)
            for i in rawImageD.flat:
                up += i
            if up <= 5100:
                if UD == 1:
                    self.motion.flyCmd('stop')
                    time.sleep(2)
                    UD = 0
                self.motion.flyCmd('down')
                continue
            U = 0
            W = 0
            D = 0
            rawImage = np.vsplit(rawImageF, 5)
            rawImageU = np.add(rawImage[0], rawImage[1])
            rawImageU = np.add(rawImageU, rawImage[2])
            rawImageD = np.delete(rawImage[4], np.arange(0, 90), axis=0)
            for i in rawImageU.flat:
                U += i
            for i in rawImage[3].flat:
                W += i
            for i in rawImageD.flat:
                D += i
            print('U =', U, ' W =', W, ' D =', D)
            if U > 5000:
                if UD == 0:
                    self.motion.flyCmd('stop')
                    time.sleep(2)
                    UD = 1
                self.motion.flyCmd('up')
                continue
            if W < 200000 or D > 5000:
                if UD == 1:
                    self.motion.flyCmd('stop')
                    time.sleep(2)
                    UD = 0
                self.motion.flyCmd('down')
                continue
            self.motion.flyCmd('stop')
            time.sleep(1)
            break

    # 测距

    def getDistance(self):
        rawImage = self.image.getDepthImage()
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

    def adjustPositionNormally(self):
        while (True):
            ce = self.getDistance()
            if ce < 2.7 and ce > 2:
                self.motion.flyCmd('stop')
                time.sleep(2.5)
                break
            elif ce >= 2.7:
                self.motion.flyCmd('forward')
            elif ce == 0:
                self.client.moveByAngleThrottle(90, 0, 3, 0, 0.15)
                time.sleep(1)
                self.moveToCircle(8)
                self.adjustPositionHorizontally()
            elif ce > 0 and ce <= 2:
                self.motion.flyCmd('backward')

    # 正对检测园环所处区间

    def circleDection(self):
        response = self.getCameraImage(0)
        rawImage = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
        img0 = cv2.imdecode(rawImage, cv2.IMREAD_UNCHANGED)

        # 处理仅剩红色部分
        HSV = cv2.cvtColor(img0, cv2.COLOR_BGR2HSV)
        H, S, V = cv2.split(HSV)
        LowerRed = np.array([156, 43, 46])
        UpperRed = np.array([180, 255, 255])
        mask = cv2.inRange(HSV, LowerRed, UpperRed)
        imga = cv2.bitwise_and(img0, img0, mask=mask)

        LowerRed_1 = np.array([0, 43, 46])
        UpperRed_1 = np.array([10, 255, 255])
        mask1 = cv2.inRange(HSV, LowerRed_1, UpperRed_1)
        imgb = cv2.bitwise_and(img0, img0, mask=mask1)

        img = cv2.addWeighted(imga, 0.5, imgb, 0.5, 0)

        '''
        img_dressb = np.where(img0[:, :, 0] > 200) or np.where(img0[:, :, 1] > 200)
        img0[:, :, 0:2] = 0
        img0[np.where(img0 < 200)] = 0
        img0[img_dressb] = 0
        '''

        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 灰度图化
        ret, img0 = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY_INV)  # 黑白二值化

        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

        # 侵蚀与稀释，去噪，因为黑白反转故侵蚀与稀释反转
        img1 = cv2.dilate(img0, kernel, iterations=1)
        img1 = cv2.erode(img1, kernel, iterations=4)
        img1 = cv2.dilate(img1, kernel, iterations=3)

        # 求梯度偏导后得出边缘
        sobelx = cv2.Sobel(img1, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(img1, cv2.CV_64F, 0, 1, ksize=3)
        sobelxy = cv2.Sobel(img1, cv2.CV_64F, 1, 1, ksize=3)
        sobel = np.sqrt(sobelx ** 2 + sobely ** 2 + sobelxy ** 2)

        ret, img = cv2.threshold(sobel, 0, 255, cv2.THRESH_BINARY_INV)  # 黑白反转，轮廓为黑色

        img = img.astype(np.uint8)
        img = cv2.medianBlur(img, 5)

        circles = cv2.HoughCircles(
            img, cv2.HOUGH_GRADIENT, 1, 15, param1=100, param2=30, minRadius=10, maxRadius=90)

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

    # 检测正对扫描环的错误

    def getCircle(self):
        try:
            Z = self.circleDection()
        except AttributeError:
            print("AtAttributeError time + 1")
            time.sleep(1)
            Z = self.getCircle()
            return Z
        else:
            return Z

    # 横移调节至正对环

    def adjustPositionCentripetally(self):
        Z = self.getCircle()
        while (True):
            time.sleep(0.1)
            N = self.getCircle()
            if N == 0:
                self.motion.flyCmd('stop')
                time.sleep(3)
                if self.getCircle() != 0:
                    continue
                break
            if Z != N:
                self.motion.flyCmd('stop')
                time.sleep(3)
                Z = N
            if N == 1:
                self.motion.flyCmd('moveright')
            elif N == 2:
                self.motion.flyCmd('moveleft')
            elif N == 3:
                self.motion.flyCmd('up')
            elif N == 4:
                self.motion.flyCmd('down')

    # 通用于检测环近处调节

    def adjustDrone(self):
        self.adjustPositionHorizontally()
        self.adjustPositionNormally()
        self.adjustPositionHorizontally()
        self.adjustPositionNormally()
        self.adjustPositionHorizontally()
        self.checkNumber()
        self.adjustPositionHorizontally()

    # 横移检测环

    def moveCircle_N(self):
        # 飞行
        if (self.turn == 1):
            self.motion.flyCmd('moveright')
            self.turn = 1
        elif (self.turn == -1):
            self.motion.flyCmd('moveleft')
            self.turn = -1
        while (True):
            try:
                R = self.getCircle_R()
            except AttributeError:
                continue
            else:
                if R >= 23:
                    self.motion.flyCmd('stop')
                    print('found Circle_R>=23')
                    time.sleep(3)
                    self.adjustPositionCentripetally()
                    self.moveToCircle()
                    break
                else:
                    continue

    # 检测正对扫描环的错误

    def getCircle_R(self):
        # 检测
        response = self.getCameraImage(0)
        responseD = self.image.getDepthImage()
        rawImage = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
        img0 = cv2.imdecode(rawImage, cv2.IMREAD_UNCHANGED)
        # 进行边界检测
        responseF = img0.copy()
        responseF = responseF[:, :, 1]
        responseD[np.where(responseF > 200)] = 255
        responseD[np.where(responseD == 255)] = 0
        responseD = np.hsplit(responseD, 8)
        D_R = 0
        D_L = 0
        for i in responseD[7].flat:
            D_R += i
        for i in responseD[0].flat:
            D_L += i
        if self.turn == 1 and D_R > 50:
            self.motion.flyCmd('stop')
            time.sleep(4)
            self.motion.flyToHeight(self.takeHigh + 3.8, 20)
            self.motion.flyCmd('stop')
            time.sleep(2)
            print('D-Right=', D_R)
            self.turn = -1
            self.motion.flyCmd('moveleft')
            time.sleep(5)
        elif self.turn == -1 and D_L > 50:
            self.motion.flyCmd('stop')
            time.sleep(4)
            self.motion.flyToHeight(self.takeHigh + 3.8, 20)
            self.motion.flyCmd('stop')
            time.sleep(2)
            print('D-Left=', D_L)
            self.turn = 1
            self.motion.flyCmd('moveright')
            time.sleep(5)

        # 开始检测圆环
        img0 = img0[:, 120:520, :]

        # 处理仅剩红色部分
        HSV = cv2.cvtColor(img0, cv2.COLOR_BGR2HSV)
        H, S, V = cv2.split(HSV)
        LowerRed = np.array([156, 43, 46])
        UpperRed = np.array([180, 255, 255])
        mask = cv2.inRange(HSV, LowerRed, UpperRed)
        imga = cv2.bitwise_and(img0, img0, mask=mask)

        LowerRed_1 = np.array([0, 43, 46])
        UpperRed_1 = np.array([10, 255, 255])
        mask1 = cv2.inRange(HSV, LowerRed_1, UpperRed_1)
        imgb = cv2.bitwise_and(img0, img0, mask=mask1)

        img = cv2.addWeighted(imga, 0.5, imgb, 0.5, 0)

        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 灰度图化
        ret, img0 = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY_INV)  # 黑白二值化

        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

        # 侵蚀与稀释，去噪，因为黑白反转故侵蚀与稀释反转
        img1 = cv2.dilate(img0, kernel, iterations=1)
        img1 = cv2.erode(img1, kernel, iterations=4)
        img1 = cv2.dilate(img1, kernel, iterations=3)

        # 求梯度偏导后得出边缘
        sobelx = cv2.Sobel(img1, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(img1, cv2.CV_64F, 0, 1, ksize=3)
        sobelxy = cv2.Sobel(img1, cv2.CV_64F, 1, 1, ksize=3)
        sobel = np.sqrt(sobelx ** 2 + sobely ** 2 + sobelxy ** 2)

        ret, img = cv2.threshold(sobel, 0, 255, cv2.THRESH_BINARY_INV)  # 黑白反转，轮廓为黑色

        img = img.astype(np.uint8)
        img = cv2.medianBlur(img, 5)

        circles = cv2.HoughCircles(
            img, cv2.HOUGH_GRADIENT, 1, 15, param1=100, param2=30, minRadius=10, maxRadius=90)

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
        return circles[0][0][2]

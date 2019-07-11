from __future__ import print_function

from .utils import *

import numpy as np
import cv2
import pickle

import warnings

warnings.simplefilter("ignore", DeprecationWarning)


class Number:
    def __init__(self, image):
        self.image = image
        self.num = 1

    # self.client = client
    def image_cut(self, image):
        # image = cv2.imread('Number2.jpg',0)

        m = n = i = j = x = y = a = b = c = d = 0
        mm = nn = ii = jj = xx = yy = aa = bb = cc = dd = 0
        image_x = image.sum(axis=1).reshape(480, 1)
        image_y = image.sum(axis=0).reshape(640, 1)
        for m in range(0, 480):
            if image_x[m, 0] >= 10000:
                mm = m
                #  print(m)
                break
        for n in range(0, 480):
            if image_x[479 - n, 0] >= 10000:
                nn = 479 - n
                #  print(n)
                break

        for i in range(0, 640):
            if image_y[i, 0] >= 10000:
                ii = i
                #  print(i)
                break
        for j in range(0, 640):
            if image_y[639 - j, 0] >= 10000:
                jj = 639 - j
                #  print(j)
                break
        mm = mm + 20
        nn = nn - 10
        ii = ii + 20
        jj = jj - 20
        image_cut = image[mm:nn, ii:jj]
        image_cut_x = image_cut.sum(axis=1)
        image_cut_y = image_cut.sum(axis=0)
        x = nn - mm
        y = jj - ii
        # print(image_cut_x)
        # print(image_cut_y)
        for p in range(0, x):
            for q in range(0, y):
                if image_cut[p, q] >= 100:
                    image_cut[p, q] = 0
                else:
                    image_cut[p, q] = 255
        image_cx = image_cut.sum(axis=1).reshape(x, 1)
        image_cy = image_cut.sum(axis=0).reshape(y, 1)
        # print(x,y)
        for a in range(0, x):
            if image_cx[a, 0] > 0:
                aa = a
                #     print(a)
                break
        for b in range(0, x):
            if image_cx[x - b - 1, 0] > 0:
                bb = x - b
                #    print(b)
                break
        for c in range(0, y):
            if image_cy[c, 0] > 0:
                cc = c
                #     print(c)
                break
        for d in range(0, y):
            if image_cy[y - d - 1, 0] > 0:
                dd = y - d
                #     print(d)
                break
        x = bb - aa
        y = dd - cc
        image_cut = image_cut[aa:bb, cc:dd]
        # cv2.imshow('imshow',image_cut)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # cv2.imwrite(r'C:\Users\hiyyc\image_example\result1.jpg',image_cut)
        return image_cut

    def pretreatment(self, ima):

        # ima=ima.convert('L')         #转化为灰度图像
        im = np.array(ima)  # 转化为二维数组
        for i in range(im.shape[0]):  # 转化为二值矩阵
            for j in range(im.shape[1]):
                if im[i, j] == 255:
                    im[i, j] = 1
                else:
                    im[i, j] = 0
        return im

    # 提取图片特征
    def feature(self, A):
        midx = int(A.shape[1] / 2) + 1
        midy = int(A.shape[0] / 2) + 1
        A1 = A[0:midy, 0:midx].mean()
        A2 = A[midy:A.shape[0], 0:midx].mean()
        A3 = A[0:midy, midx:A.shape[1]].mean()
        A4 = A[midy:A.shape[0], midx:A.shape[1]].mean()
        A5 = A.mean()
        AF = [A1, A2, A3, A4, A5]
        return AF

    def distance(self, v1, v2):
        vector1 = np.array(v1)
        vector2 = np.array(v2)
        Vector = (vector1 - vector2) ** 2
        #   print(Vector)
        distance = Vector.sum() ** 0.5
        #   print(distance)
        return distance

    def knn(self, train_set, V, k):
        distance_sort = np.zeros(([9, 2]))
        key_sort = np.zeros(([9, 2]))
        # 获取每个键值中数据集与测试集的distance，并使键值对应distance
        for n in range(1, 10):
            for m in range(1, 3):
                distance_sort[n - 1][m - 1] = self.distance(train_set[n][m - 1], V)
                key_sort[n - 1][m - 1] = n
        distance_sort = distance_sort.flatten()
        key_sort = key_sort.flatten()
        #  print(distance_sort)
        #  print(key_sort)
        #  print(len(distance_sort))
        # 将误差升序排序，并经key值也置换到相同位置

        for i in range(1, len(distance_sort)):
            for j in range(0, len(distance_sort) - i):
                if distance_sort[j] > distance_sort[j + 1]:
                    key_sort[j], key_sort[j + 1] = key_sort[j + 1], key_sort[j]
                    distance_sort[j], distance_sort[j + 1] = distance_sort[j + 1], distance_sort[j]
        distance_sort = distance_sort.tolist()
        key_sort = key_sort.tolist()
        distance_sort = distance_sort[0:k]
        key_sort = key_sort[0:k]
        # 定义一个字典，记录元素及次数
        d = {}
        # 记录最大次数的元素
        max_key = None
        for i in key_sort:
            # 判断字典中是否没有该元素
            if i not in d:
                # 计算该元素在列表中出现的次数
                count = key_sort.count(i)
                # 保存到字典中
                d[i] = count
                # 记录最大元素
                if count > d.get(max_key, 0):
                    max_key = i
        #    print(max_key)
        #    print(result)
        #    print(distance_sort)
        #    print(key_sort)
        return max_key

    # ima = image_cut()
    # ima = PIL.Image.fromarray(ima)
    # cv2.imshow('imshow',ima)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # print(train_set)
    # print(AF)
    def getNumber(self):
        # ima=PIL.Image.open(r'C:\Users\hiyyc\image_example\QQ截图20190704191835.png')
        rawImageF = self.image.getFrontSense()
        rawImageD = self.image.getDepthImage()
        rawImageF = rawImageF[:, :, 0]
        rawImageF[np.where(rawImageD == 255)] = 0
        rawImageF[np.where(rawImageF < 200)] = 0
        fileNameB = 'Number' + str(self.num) + '.jpg'
        cv2.imwrite(fileNameB, rawImageF)
        ima = self.image_cut(rawImageF)
        fileNameBG = 'getNumber' + str(self.num) + '.jpg'
        cv2.imwrite(fileNameBG, ima)
        ima = cv2.imread(fileNameBG, 0)
        # train_set=training()
        pkl_file = open('train_set.pkl', 'rb')
        train_set = pickle.load(pkl_file)

        im = self.pretreatment(ima)  # 预处理
        AF = self.feature(im)
        result = self.knn(train_set, AF, 2)
        # print(int(result))
        self.num += 1
        return int(result)

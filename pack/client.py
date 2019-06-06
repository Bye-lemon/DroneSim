from __future__ import print_function

from .utils import *
from .types import *

import msgpackrpc #install as admin: pip install msgpack-rpc-python
import numpy as np #pip install numpy
import msgpack
import time
import math
import logging


class VehicleClient:
    def __init__(self, ip = "", port = 41451, timeout_value = 3600):
        if (ip == ""):
            ip = "127.0.0.1"
        self.client = msgpackrpc.Client(msgpackrpc.Address(ip, port), timeout = timeout_value, pack_encoding = 'utf-8', unpack_encoding = 'utf-8')

    # -----------------------------------  Common vehicle APIs ---------------------------------------------
    def reset(self):
        self.client.call('reset')

    def ping(self):
        return self.client.call('ping')

    def getClientVersion(self):
        return 1 # sync with C++ client
    def getServerVersion(self):
        return 1#self.client.call('getServerVersion')
    def getMinRequiredServerVersion(self):
        return 1 # sync with C++ client
    def getMinRequiredClientVersion(self):
        return 1#self.client.call('getMinRequiredClientVersion')

# basic flight control
    def enableApiControl(self, is_enabled):
        return self.client.call('enableApiControl', is_enabled)
    def isApiControlEnabled(self):
        return self.client.call('isApiControlEnabled')
    def armDisarm(self, arm):
        return self.client.call('armDisarm', arm)

    def confirmConnection(self):
        if self.ping():
            print("Connected!")
        else:
             print("Ping returned false!")
        server_ver = self.getServerVersion()
        client_ver = self.getClientVersion()
        server_min_ver = self.getMinRequiredServerVersion()
        client_min_ver = self.getMinRequiredClientVersion()

        ver_info = "Client Ver:" + str(client_ver) + " (Min Req: " + str(client_min_ver) + \
              "), Server Ver:" + str(server_ver) + " (Min Req: " + str(server_min_ver) + ")"

        if server_ver < server_min_ver:
            print(ver_info, file=sys.stderr)
            print("AirSim server is of older version and not supported by this client. Please upgrade!")
        elif client_ver < client_min_ver:
            print(ver_info, file=sys.stderr)
            print("AirSim client is of older version and not supported by this server. Please upgrade!")
        else:
            print(ver_info)
        print('')


    # camera control
    # simGetImage returns compressed png in array of bytes
    # image_type uses one of the ImageType members
    def simGetImages(self, requests):
        responses_raw = self.client.call('simGetImages', requests)
        return [ImageResponse.from_msgpack(response_raw) for response_raw in responses_raw]


    # sensor APIs
    def getImuData(self):
        return ImuData.from_msgpack(self.client.call('getImudata'))

    def getBarometerData(self):
        return BarometerData.from_msgpack(self.client.call('getBarometerdata'))

    def getMagnetometerData(self):
        return MagnetometerData.from_msgpack(self.client.call('getMagnetometerdata'))


    # control APIs
    def takeoff(self, max_wait_seconds = 15):
        return self.client.call('takeoff', max_wait_seconds)
    def land(self, max_wait_seconds = 60):
        return self.client.call('land', max_wait_seconds)
    def hover(self):
        return self.client.call('hover')
    def moveByAngleThrottle(self, pitch, roll, throttle, yaw_rate, duration):
        return self.client.call('moveByAngleThrottle', pitch, roll, throttle, yaw_rate, duration)



class MultirotorClient(VehicleClient, object):
    def __init__(self):
        super(MultirotorClient, self).__init__()
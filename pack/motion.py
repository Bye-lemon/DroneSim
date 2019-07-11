import time
import math
import msvcrt
import threading


class PID:
    INIT_VALUE = 0.5869 * 10000  # 抵消重力的油门常数
    MAX_VALUE = INIT_VALUE + 0.4 * 10000
    MIN_VALUE = INIT_VALUE - 0.4 * 10000

    def __init__(self, kp=40, ki=0.001, kd=500):
        self.dest = 0
        self.Kp = kp
        self.Ki = ki
        self.kd = kd
        self.preerror = 0
        self.prederror = 0
        self.out = PID.INIT_VALUE

    def setDest(self, dest):
        self.dest = dest

    def update(self, feedback):
        error = self.dest - feedback
        derror = error - self.preerror
        dderror = derror - self.prederror
        self.preerror = error
        self.prederror = derror

        deltu = self.Kp * derror + self.Ki * error + self.kd * dderror
        self.out += deltu

        if self.out > PID.MAX_VALUE:
            self.out = PID.MAX_VALUE
        elif self.out < PID.MIN_VALUE:
            self.out = PID.MIN_VALUE

        return self.out / 10000


class VehicleMotion(threading.Thread):
    THROTTLE_CONSTANT_GRAVITY = 0.5869  # 抵消重力的油门常数

    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw_rate = 0.0
        self.throttle = VehicleMotion.THROTTLE_CONSTANT_GRAVITY
        self.moving_flag = False
        self.thread_stop = False
        self.altitude = 0.0
        self.nowcmd = "stop"

    def flyCmd(self, cmd, speed="slow"):
        if cmd == "forward" and self.nowcmd != "forward":
            if speed == "slow":
                self.pitch = -0.01
            elif speed == "fast":
                self.pitch = -0.05
            else:
                self.pitch = 0.0
            self.throttle = VehicleMotion.THROTTLE_CONSTANT_GRAVITY / math.cos(self.pitch)
            self.roll = 0.0
            self.yaw_rate = 0.0
            self.moving_flag = True
            self.nowcmd = cmd
        elif cmd == "backward" and self.nowcmd != "backward":
            if speed == "slow":
                self.pitch = 0.01
            elif speed == "fast":
                self.pitch = 0.05
            else:
                self.pitch = 0.0
            self.throttle = VehicleMotion.THROTTLE_CONSTANT_GRAVITY / math.cos(self.pitch)
            self.roll = 0.0
            self.yaw_rate = 0.0
            self.moving_flag = True
            self.nowcmd = cmd
        elif cmd == "moveleft" and self.nowcmd != "moveleft":
            if speed == "slow":
                self.roll = -0.01
            elif speed == "fast":
                self.roll = -0.05
            else:
                self.roll = 0.0
            self.throttle = VehicleMotion.THROTTLE_CONSTANT_GRAVITY / math.cos(self.roll)
            self.pitch = 0.0
            self.yaw_rate = 0.0
            self.moving_flag = True
            self.nowcmd = cmd
        elif cmd == "moveright" and self.nowcmd != "moveright":
            if speed == "slow":
                self.roll = 0.01
            elif speed == "fast":
                self.roll = 0.05
            else:
                self.roll = 0.0
            self.throttle = VehicleMotion.THROTTLE_CONSTANT_GRAVITY / math.cos(self.roll)
            self.pitch = 0.0
            self.yaw_rate = 0.0
            self.moving_flag = True
            self.nowcmd = cmd
        elif cmd == "turnleft" and self.nowcmd != "turnleft":
            if speed == "slow":
                self.yaw_rate = -0.1
            elif speed == "fast":
                self.yaw_rate = -0.3
            else:
                self.yaw_rate = 0.0
            self.throttle = VehicleMotion.THROTTLE_CONSTANT_GRAVITY
            self.pitch = 0.0
            self.roll = 0.0
            self.moving_flag = True
            self.nowcmd = cmd
        elif cmd == "turnright" and self.nowcmd != "turnright":
            if speed == "slow":
                self.yaw_rate = 0.1
            elif speed == "fast":
                self.yaw_rate = 0.3
            else:
                self.yaw_rate = 0.0
            self.throttle = VehicleMotion.THROTTLE_CONSTANT_GRAVITY
            self.pitch = 0.0
            self.roll = 0.0
            self.moving_flag = True
            self.nowcmd = cmd
        elif cmd == "up" and self.nowcmd != "up":
            self.pitch = 0.0
            self.roll = 0.0
            self.yaw_rate = 0.0
            if speed == "slow":
                self.throttle = VehicleMotion.THROTTLE_CONSTANT_GRAVITY + 0.005
            elif speed == "fast":
                self.throttle = VehicleMotion.THROTTLE_CONSTANT_GRAVITY + 0.02
            self.moving_flag = True
            self.nowcmd = cmd
        elif cmd == "down" and self.nowcmd != "down":
            self.pitch = 0.0
            self.roll = 0.0
            self.yaw_rate = 0.0
            if speed == "slow":
                self.throttle = VehicleMotion.THROTTLE_CONSTANT_GRAVITY - 0.005
            elif speed == "fast":
                self.throttle = VehicleMotion.THROTTLE_CONSTANT_GRAVITY - 0.02
            self.moving_flag = True
            self.nowcmd = cmd
        elif cmd == "stop":
            self.moving_flag = False
            self.pitch = 0.0
            self.roll = 0.0
            self.yaw_rate = 0.0
            self.throttle = VehicleMotion.THROTTLE_CONSTANT_GRAVITY
            self.nowcmd = cmd

    def run(self):
        while True:
            if self.thread_stop:
                break
            if self.moving_flag:
                self.altitude = self.client.getBarometerData().altitude
                self.client.moveByAngleThrottle(self.pitch, self.roll, self.throttle, self.yaw_rate, 0.5)
            time.sleep(0.1)

    def endThread(self):
        self.thread_stop = True

    def getMotionState(self):
        s = "pitch=" + str(self.pitch) + ",roll=" + str(self.roll) + ",yaw_rate=" + str(
            self.yaw_rate) + ",throttle=" + str(self.throttle) + ",height=" + str(self.altitude)
        return s

    # close-loop
    def flyToHeight(self, dest_height, delay=30):
        pid = PID()
        pid.setDest(dest_height)
        self.moving_flag = False
        count = 0
        while True:
            self.altitude = self.client.getBarometerData().altitude
            t = pid.update(self.altitude)
            self.client.moveByAngleThrottle(0, 0, t, 0, 0.5)
            # print("dest_height="+str(dest_height)+",altitude="+str(self.altitude)+",throttle="+str(t))
            time.sleep(0.5)
            count = count + 1
            if count == delay:
                break

    # test
    def testGravityConstant(self):
        while True:
            key = msvcrt.getch()
            if key == b'q':
                self.endThread()
                break
            if key == b'c':
                self.pitch = 0.0
                self.roll = 0.0
                self.yaw_rate = 0.0
                self.throttle = self.throttle + 0.0001
                self.moving_flag = True
            if key == b'v':
                self.pitch = 0.0
                self.roll = 0.0
                self.yaw_rate = 0.0
                self.throttle = self.throttle - 0.0001
                self.moving_flag = True
            if key == b'p':
                self.moving_flag = False
                self.pitch = 0.0
                self.roll = 0.0
                self.yaw_rate = 0.0
                self.throttle = VehicleMotion.THROTTLE_CONSTANT_GRAVITY
            print("throttle=" + str(self.throttle) + ",height=" + str(self.altitude))

    def keyControlTest(self):
        key = msvcrt.getch()
        if key == b'Q' or key == b'q': return "quit"
        if key == b'W': self.flyCmd("forward", "fast")
        if key == b'w': self.flyCmd("forward", "slow")
        if key == b'S': self.flyCmd("backward", "fast")
        if key == b's': self.flyCmd("backward", "slow")
        if key == b'A': self.flyCmd("moveleft", "fast")
        if key == b'a': self.flyCmd("moveleft", "slow")
        if key == b'D': self.flyCmd("moveright", "fast")
        if key == b'd': self.flyCmd("moveright", "slow")
        if key == b'Z': self.flyCmd("turnleft", "fast")
        if key == b'z': self.flyCmd("turnleft", "slow")
        if key == b'X': self.flyCmd("turnright", "fast")
        if key == b'x': self.flyCmd("turnright", "slow")
        if key == b'C': self.flyCmd("up", "fast")
        if key == b'c': self.flyCmd("up", "slow")
        if key == b'V': self.flyCmd("down", "fast")
        if key == b'v': self.flyCmd("down", "slow")
        if key == b'P' or key == b'p': self.flyCmd("stop")
        print(self.getMotionState())

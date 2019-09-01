#!/usr/bin/python3

from sphero.spheromini import SpheroMini
from sphero.messages import *
import time

state = {
    ResponseCode_OK:"Command succeeded",
    ResponseCode_EGEN:"General, non-specific error",
    ResponseCode_ECHKSUM:"Received checksum failure",
    ResponseCode_EFRAG:"Received command fragment",
    ResponseCode_EBAD_CMD:"Unknown command ID",
    ResponseCode_EUNSUPP:"Command currently unsupported",
    ResponseCode_EBAD_MSG:"Bad message format",
    ResponseCode_EPARAM:"Parameter value(s) invalid",
    ResponseCode_EEXEC:"Failed to execute command",
    ResponseCode_EBAD_DID:"Unknown Device ID",
    ResponseCode_MEM_BUSY:"Generic RAM access needed but it is busy",
    ResponseCode_BAD_PASSWORD:"Supplied password incorrect",
    ResponseCode_POWER_NOGOOD:"Voltage too low for reflash operation",
    ResponseCode_PAGE_ILLEGAL:"Illegal page number provided",
    ResponseCode_FLASH_FAIL:"Page did not reprogram correctly",
    ResponseCode_MA_CORRUPT:"Main Application corrupt",
    ResponseCode_MSG_TIMEOUT:"Msg state machine timed out"
}

dev = SpheroMini("dc:b9:9d:18:0a:f9")
dev.connect()
print("Connected!!")
print()

print(dev.ping())
print()
#print(dev.getVersioning())
#print()
#print(dev.setDeviceName("Bolita"))
#print()
#print(dev.getBluetoothInfo())
#print()
#print(dev.getPowerState())
#print()
#print(dev.setPowerNotification(True))
#print()
#print(dev.sleep(65535))
#print()
#print(dev.setInactivityTimeout(600))
#print()
#print(dev.pollPacketTimes())
#print()

#*******************************************************************************************************/
#***********************************        Sphero commands         *************************************
#*******************************************************************************************************/
#print(dev.setHeading(20))
#print()
#print(dev.setStabilisation(True))
#print()
#print(dev.getChassisId())
#print()

"""op = {
    'startStop':0,#0-1
    'finalAngle':0,#0-1
    'sleep':0,#0-1
    'controlSystem':0,#0-1
    'angleLimit':0,#0-90
    'timeout':0,#0-255
    'trueTime':0#0-255
}
print(dev.selfLevel(op))
print()"""

"""op = {
    'N':2, 'M':3, 'PCNT':4,

    'accelXRaw':1, 'accelYRaw':1, 'accelZRaw':1,
    'gyroXRaw':0, 'gyroYRaw':0, 'gyroZRaw':0,
    'rightEMFRaw':0, 'leftEMFRaw':0,
    'leftPWMRaw':0, 'rightPWMRaw':0,
    'pitchIMU':0, 'rollIMU':0, 'yawIMU':0,
    'accelX':0, 'accelY':0, 'accelZ':0,
    'gyroX':0, 'gyroY':0, 'gyroZ':0,
    'rightEMF':0, 'leftEMF':0,

    'q0':0, 'q1':0, 'q2':0, 'q3':0,
    'odometerX':0, 'odometerY':0,
    'accelOne':0,
    'velocityX':0, 'velocityY':0
}
print(dev.setDataStreaming(op))
print()"""

"""op = {
    'meth':0,
    'xt':0,
    'xspd':0,
    'yt':0,
    'yspd':0,
    'dead':0
}
print(dev.configureCollisionDetection(op))
print()"""

"""op = {
    'autoCalibrate':1,
    'x':0,
    'y':0,
    'yawTare':0
}
print(dev.configureLocator(op))
print()"""

#print(dev.readLocator())
#print()
#print(dev.setRGBLedOutput(100, 0, 0, True))
#print()
#print(dev.setBackLEDOutput(100))
#print()
#print(dev.getRGBLed())
#print()
#print(dev.roll(10, 0, 1))
#print()
#print(dev.setRAWMotorValues(1, 50, 1, 50))
#print()
#print(dev.setMotionTimeout(2000))
#print()

"""op = {
    'sleepCharge':0,
    'vectorDrive':0,
    'selfLevelingCharger':0,
    'forceTailLED':0,
    'motionTimeOuts':0,
    'retailDemoMode':0,
    'awakeLight':0,
    'awakeHeavy':0,
    'gyroMaxAsync':0
}
print(dev.setPermanentOptionFlags(op))
print()"""

#print(dev.getPermanentOptionFlags())
#print()
#print(dev.setTemporaryOptionFlags(1))
#print()
#print(dev.getTemporaryOptionFlags())
#print()

#dev.sleep(65535)
dev.disconnect()
print("Disconected!!")

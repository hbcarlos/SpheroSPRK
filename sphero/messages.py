#!/usr/bin/python3

import binascii

# ResponseCode
ResponseCode_OK = 0
ResponseCode_EGEN = 1
ResponseCode_ECHKSUM = 2
ResponseCode_EFRAG = 3
ResponseCode_EBAD_CMD = 4
ResponseCode_EUNSUPP = 5
ResponseCode_EBAD_MSG = 6
ResponseCode_EPARAM = 7
ResponseCode_EEXEC = 8
ResponseCode_EBAD_DID = 9
ResponseCode_MEM_BUSY = 10
ResponseCode_BAD_PASSWORD = 11
ResponseCode_POWER_NOGOOD = 49
ResponseCode_PAGE_ILLEGAL = 50
ResponseCode_FLASH_FAIL = 51
ResponseCode_MA_CORRUPT = 52
ResponseCode_MSG_TIMEOUT = 53

# AsyncResponseIdCode
AsyncResponseId_Invalid = 0
AsyncResponseId_PowerNotification = 1
AsyncResponseId_Level1DiagnosticResponse = 2
AsyncResponseId_SensorDataStreaming = 3
AsyncResponseId_ConfigBlockContents = 4
AsyncResponseId_PreSleepWarning10Sec = 5
AsyncResponseId_MacroMarkers = 6
AsyncResponseId_CollisionDetected = 7
AsyncResponseId_orbBasicPrintMessage = 8
AsyncResponseId_orbBasicErrorMessageASCII = 9
AsyncResponseId_orbBasicErrorMessageBinary = 10
AsyncResponseId_SelfLevelResult = 11
AsyncResponseId_GyroAxisLimitExceeded = 12
AsyncResponseId_SpheroSoulData = 13
AsyncResponseId_LevelUpNotification = 14
AsyncResponseId_ShieldDamageNotification = 15
AsyncResponseId_XPUpdateNotification = 16
AsyncResponseId_BoostUpdateNotification = 17

# Battery
Battery_Charging = 1
Battery_Ok = 2
Battery_Low = 3
Battery_Critical = 4

# SelfLevelRoutine
SelfLevel_Unknown = 0
SelfLevel_TimedOut = 1
SelfLevel_SensorsError = 2
SelfLevel_Disabled = 3
SelfLevel_Aborted = 4
SelfLevel_ChargerNotFound = 5
SelfLevel_Success = 6

class Message(object):

    def __init__(self, sop2, did, cid, seq, data):
        self.sop1 = b'\xff'
        self.sop2 = sop2
        self.did = did
        self.cid = cid
        self.seq = seq.to_bytes(1,"big")
        self.dlen = (len(data)+1).to_bytes(1,"big")
        self.data = data
        self.chk = self.checksum([self.did, self.cid, self.seq, self.dlen] + self.data)

    def __str__(self):
        return str(self.packet())

    def checksum(self, data):
        value = 0
        for b in data:
            for i in range(0, len(b)):
                value += b[i]

        return (255-(value%256)).to_bytes(1,'big')

    def packet(self):
        return [self.sop1, self.sop2, self.did, self.cid, self.seq, self.dlen] + self.data + [self.chk]

class Response(object):

    def __init__(self, packet):
        self.sop1 = bytes.hex(packet[0].to_bytes(1,"big"))
        self.sop2 = bytes.hex(packet[1].to_bytes(1,"big"))
        self.mrsp = packet[2]
        self.seq = packet[3]
        self.dlen = packet[4]
        self.data = [x.to_bytes(1,"big") for x in packet[5:-1]] if self.dlen > 0 else []
        self.chk = packet[-1]

    def __str__(self):
        return str(self.packet())

    def checksum(self, data, chk):
        value = (255-(sum(data)%256))
        return value == int.from_bytes(chk, "big")

    def packet(self):
        return [self.sop1, self.sop2, self.mrsp, self.seq, self.dlen] + self.data + [self.chk]

class ResponseAsync(object):

    def __init__(self, packet):
        self.sop1 = bytes.hex(packet[0].to_bytes(1,"big"))
        self.sop2 = bytes.hex(packet[1].to_bytes(1,"big"))
        self.idcode = packet[2]
        self.dlen = ( packet[3] << 4 ) + packet[4]
        self.data = [x.to_bytes(1,"big") for x in packet[5:-1]] if self.dlen > 0 else []
        self.chk = packet[-1]

    def __str__(self):
        return str(self.packet())

    def checksum(self, data, chk):
        value = (255-(sum(data)%256))
        return value == int.from_bytes(chk, "big")

    def packet(self):
        return [self.sop1, self.sop2, self.idcode, self.dlen] + self.data + [self.chk]

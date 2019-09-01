#!/usr/bin/python3

import bluepy
from .messages import *
from .event import *

class Delegate(bluepy.btle.DefaultDelegate):


    def __init__(self, device, lock, async, handlerAsync):
        bluepy.btle.DefaultDelegate.__init__(self)
        self.device = device
        self.bufferBytes = b''

        self.seqList = {}
        self.lock = lock
        self.asyncMessage = Event()
        self.asyncMessage += async
        self.asyncMessage += handlerAsync

    def handleNotification(self, cHandle, data):
        self.bufferBytes =  self.bufferBytes + data

        #print(self.bufferBytes)

        for i in range(0, len(self.bufferBytes)):
            if self.bufferBytes[i] == 255 :
                break

        for j in range(i, len(self.bufferBytes)+1):
            packet = self.bufferBytes[i:j]
            if self.checkChecksum(packet) and packet[1] == 255 :
                resp = Response(packet)
                self.device.messages[resp.seq] = resp
                self.seqList[resp.seq] = resp.seq

                #print("Simple Response: ")
                #print(resp)
                self.bufferBytes = self.bufferBytes[j:]
                break

            if self.checkChecksumAsync(packet) and packet[1] == 254 :
                resp = ResponseAsync(packet)
                self.asyncMessage(resp)

                #print("Async Response: ")
                #print(resp)
                self.bufferBytes = self.bufferBytes[j:]
                break

    def waitResp(self, seq, timeout=None):
        self.seqList[seq] = None;
        while(self.seqList[seq] == None):
            with self.lock:
                self.device.device.waitForNotifications(0.005)
        return self.seqList.pop(seq)

    def checkChecksum(self, packet):
        if len(packet) < 5 :
            return False
        if packet[0] != 255 :
            return False

        if packet[4] != 255 and packet[4] != len(packet[4:-1]) :
            return False

        chk = (255-(sum(packet[2:-1])%256))
        return chk == packet[-1]

    def checkChecksumAsync(self, packet):
        if len(packet) < 5 :
            return False
        if packet[0] != 255 :
            return False

        if ((packet[3] << 8) + packet[4]) != len(packet[4:-1]) :
            return False

        chk = (255-(sum(packet[2:-1])%256))
        return chk == packet[-1]

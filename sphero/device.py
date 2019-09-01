#!/usr/bin/python3

import time
import binascii
import threading

from bluepy import btle
from .delegate import Delegate
from .messages import *

class Device(object):

    def __init__(self, config, addres, handlerAsync, name="SK-5FD4"):
        self.config = config
        self.addres = addres
        self.name = name
        self.device = None

        self.notifier = None
        self.handlerAsync = handlerAsync
        self.connected = False
        self.seq = 0

        self.rate = 10
        self.lock = threading.RLock()

        self.RCCharacteristics = {}
        self.BLECharacteristics = {}

        self.messages = {}
        self.messagesAsync = {}

    def connect(self):
        self.device = btle.Peripheral(self.addres, addrType=btle.ADDR_TYPE_RANDOM)
        self.notifier = Delegate(self, self.lock, self.responseAsync, self.handlerAsync)
        self.device.withDelegate(self.notifier)

        self.devModeOn()
        self.connected = True

        #get the command service
        service = self.device.getServiceByUUID(self.config["RobotControlService"])
        characteristics = service.getCharacteristics()

        for characteristic in characteristics:
            uuid = binascii.b2a_hex(characteristic.uuid.binVal).decode('utf-8')
            self.RCCharacteristics[uuid] = characteristic

    def disconnect(self):
        del self.device
        del self.notifier
        self.connect = False

        self.RCCharacteristics = {}
        self.BLECharacteristics = {}

        self.messages = {}
        self.messagesAsync = {}

    def devModeOn(self):
        service = self.device.getServiceByUUID(self.config["BLEService"])
        characteristics = service.getCharacteristics()

        for characteristic in characteristics:
            uuid = binascii.b2a_hex(characteristic.uuid.binVal).decode('utf-8')
            self.BLECharacteristics[uuid] = characteristic

        self.BLECharacteristics[self.config["AntiDosCharacteristic"]].write("011i3".encode(),True)
        self.BLECharacteristics[self.config["TXPowerCharacteristic"]].write((7).to_bytes(1, 'big'),True)
        #self.BLECharacteristics[self.config["WakeCharacteristic"]].write((1).to_bytes(1, 'big'),True)

    def sendCommand(self, did, cid, data=[], resp=True):
        sop2 = b'\xff' if resp else b'\xfe'
        seq = self.getSequence()
        msg = Message(sop2, did, cid, seq, data)
        #print(msg)

        enviado = False
        while enviado == False :
            try:
                with self.lock:
                    self.RCCharacteristics[self.config["CommandsCharacteristic"]].write(b"".join(msg.packet()))
                    if resp :
                        self.notifier.waitResp(seq)
                    enviado = True
            except btle.BTLEDisconnectError:
                self.connect()
                print("Intentando conectar...")

        return seq

    def reciveAsync(self, idcode):
        msg = self.messagesAsync.get(idcode, None)
        if msg != None:
            self.messagesAsync.pop(idcode)

        return msg

    def response(self, seq):
        #print(self.messages)
        return self.messages.pop(seq)

    def responseAsync(self, msg):
        self.messagesAsync[msg.idcode] = msg

    def getSequence(self):
        val = self.seq
        self.seq += 1
        self.seq = self.seq%256
        return val

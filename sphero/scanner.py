#!/usr/bin/python3

from bluepy import btle

def scan(timeout=1):
    sc = btle.Scanner()
    devices = sc.scan(timeout)

    for dev in devices:
        name = dev.getValueText(9)
        if name != None and (name.startswith('SK-') or name.startswith('SM-')) :
	        print("Device %s with addres %s (%s), RSSI=%d dB" % (dev.getValueText(9), dev.addr, dev.addrType, dev.rssi))
	        for (adtype, desc, value) in dev.getScanData():
	            print( "  %s = %s" % (desc, value))

def getInfoDevice(address):
    device = btle.Peripheral(address, addrType=btle.ADDR_TYPE_RANDOM)

    print("Device: ", address)
    services = device.getServices()
    for service in services:
        print("\tService: ", service.uuid)
        characteristics = service.getCharacteristics()
        for characteristic in characteristics:
            print("\t\tCharacteristic: ", characteristic.uuid)
            print("\t\t\t+ ", characteristic.propertiesToString())

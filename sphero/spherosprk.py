#!/usr/bin/python3

import time
import binascii
import threading

from .device import Device
from .messages import *
from .commands import *

def async(self):
    return 0

config = {
    "RobotControlService":"22bb746f2ba075542d6f726568705327",
    "ResponseCharacteristic":"22bb746f2ba675542d6f726568705327",
    "CommandsCharacteristic":"22bb746f2ba175542d6f726568705327",
    "BLEService":"22bb746f2bb075542d6f726568705327",
    "AntiDosCharacteristic":"22bb746f2bbd75542d6f726568705327",
    "TXPowerCharacteristic":"22bb746f2bb275542d6f726568705327",
    "WakeCharacteristic":"22bb746f2bbf75542d6f726568705327"
}

name = "SK-5FD4"
address = "d3:57:0a:71:5f:d4"

class SpheroSPRK(object):

    def __init__(self, addres, handlerAsync=async):
        self.addres = addres
        self.stream = {}
        self.device = Device(config, self.addres, handlerAsync)

    def connect(self):
        self.device.connect()

    def disconnect(self):
        self.device.disconnect()

    def ping(self):
        """The Ping command is used to verify both a solid data link with the Client
        and that Sphero is awake and dispatching commands.Even though Ping is neither
        a set or getformat command, it still enjoys a Simple Response."""

        seq = self.device.sendCommand(DeviceId_CORE, CoreCommandId_PING)
        msg = self.device.response(seq)

        #print("Ping: ", msg.mrsp)
        return (msg.mrsp, None)

    def getVersioning(self):
        """The Get Versioning command returns a whole slew of software
        and hardware information. It’s useful if your Client Application
        requires a minimum version number of some resource within Sphero
        in order to operate. The data recordstructure is comprised of fieldsfor
        each resource that encodesthe version number according to the specified format."""

        seq = self.device.sendCommand(DeviceId_CORE, CoreCommandId_VERSION)
        msg = self.device.response(seq)

        #print("_getVersioning: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))
        #print(msg)
        res = {}
        res["RECV"] = int.from_bytes(msg.data[0], "big")
        res["MDL"] = bytes.hex(msg.data[1])
        res["HW"] = int.from_bytes(msg.data[2], "big")
        res["MSAver"] = int.from_bytes(msg.data[3], "big")
        res["MSArev"] = int.from_bytes(msg.data[4], "big")

        n = (int.from_bytes(msg.data[5], "big") & 240) >> 4
        d = (int.from_bytes(msg.data[5], "big") & 15) / 10.0 if (int.from_bytes(msg.data[5], "big") & 15) < 10 else (int.from_bytes(msg.data[5], "big") & 15) / 100.0
        res["BL"] = n + d
        n = (int.from_bytes(msg.data[6], "big") & 240) >> 4
        d = (int.from_bytes(msg.data[6], "big") & 15) / 10.0 if (int.from_bytes(msg.data[6], "big") & 15) < 10 else (int.from_bytes(msg.data[6], "big") & 15) / 100.0
        res["BAS"] = n + d
        n = (int.from_bytes(msg.data[7], "big") & 240) >> 4
        d = (int.from_bytes(msg.data[7], "big") & 15) / 10.0 if (int.from_bytes(msg.data[7], "big") & 15) < 10 else (int.from_bytes(msg.data[7], "big") & 15) / 100.0
        res["MACRO"] = n + d

        #res.APImaj = static_cast<int>(msg.data[8]);
        #res.APImin static_cast<int>(msg.data[9]);

        return (ResponseCode_OK, res)

    def _setUARTTxLine(self, enable=True):
        """This is a factory command that either enables or disables the CPU's
        UART transmit line so that another physicallyconnected client can
        configure the Bluetooth module. The receive line is always listening,
        which is how you can re-enable the Tx line later. Or just reboot as this
        setting is not persistent."""

        flag_enable = b'\x01' if enable else b'\x00'

        seq = self.device.sendCommand(DeviceId_CORE, CoreCommandId_CONTROL_UART_TX, [flag_enable])
        msg = self.device.response(seq)

        #print("_setUARTTxLine: ", msg.mrsp)
        return (msg.mrsp, None)

    def setDeviceName(self, name):
        """This formerly reprogrammed the Bluetooth module to advertise with a
        different name, but this is no longer the case. This assigned name is
        held internally and produced as part of the Get Bluetooth Info service below.
        Names are clipped at 48 characters in length to support UTF-8 sequences;
        you can send something longer but the extra will be discarded.This field defaults
        to the Bluetooth advertising name

        To alter the Bluetooth advertising name from the standard Sphero-RGB pattern you
        will need to $$$ into the RN-42 within 60 seconds after power up, issue the command
        SN,mynewname and finish withr,1 to reboot the module"""

        aux = [b.to_bytes(1,"big") for b in bytearray(name, 'ascii')]

        seq = self.device.sendCommand(DeviceId_CORE, CoreCommandId_SET_BT_NAME, aux)
        msg = self.device.response(seq)

        #print("setDeviceName: ", msg.mrsp)
        return (msg.mrsp, None)

    def getBluetoothInfo(self):
        """This returns a structure containing the textual name in ASCII of
        the ball (defaults to the Bluetooth advertising name but can be changed),
        the Bluetooth address in ASCII and the ID colors the ball blinks when not connected
        to a smartphone.

        The ASCII name field is padded with zeros to its maximum size.

        This is provided as a courtesy for Clients that have don’t have a method
        to interrogate their underlying Bluetooth stack for this information"""

        seq = self.device.sendCommand(DeviceId_CORE, CoreCommandId_GET_BT_NAME)
        msg = self.device.response(seq)

        #print("getBluetoothInfo: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))
        res = {}
        res["name"] = ''.join([str(b, 'ascii') for b in msg.data[:16]]).rstrip(' \t\r\n\0')
        bta = [str(b, 'ascii') for b in msg.data[16:28]]
        res["bta"] = ':'.join([ bta[i]+bta[i+1] for i in range(0, len(bta), 2) ])
        res["idColors"] = ''.join([str(b, 'ascii') for b in msg.data[29:32]])

        return (ResponseCode_OK, res)

    def _setAutoReconnect(self, enable=True, secTimeout=30):
        """This configures the control of the Bluetooth module in its attempt to
        automatically reconnect with the last mobile Apple device. This is a courtesy behavior
        since the Apple Bluetooth stack doesn't initiate automatic reconnection on its own.

        The two parameters are simple: flag is00h to disable or 01h to enable, and time is
        the number of seconds after power-up in which to enable auto reconnectmode.
        For example, if time = 30 then the module will be attempt reconnecting30 secondsafte
        waking up.(refer to RN-APL-EVAL pg.7 for more info)"""

        flag_enable = b'\x01' if enable else b'\x00'
        seq = self.device.sendCommand(DeviceId_CORE, CoreCommandId_SET_AUTO_RECONNECT, [flag_enable, secTimeout.to_bytes(1,"big")])
        msg = self.device.response(seq)

        #print("_setAutoReconnect: ", msg.mrsp)
        return (msg.mrsp, None)

    def _getAutoReconnect(self):
        """This returnsthe Bluetooth auto reconnect values as defined in the “Set Auto Reconnect” command."""

        seq = self.device.sendCommand(DeviceId_CORE, CoreCommandId_GET_AUTO_RECONNECT)
        msg = self.device.response(seq)

        #print("_getAutoReconnect: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))
        res = {}
        res["flag"] = True if msg.data[0] == b'\x01' else False
        res["time"] = int.from_bytes(msg.data[1], "big")

        return (ResponseCode_OK, res)

    def getPowerState(self):
        """This returns the current power state and some additional
        parameters to theClient. They are detailed below."""

        seq = self.device.sendCommand(DeviceId_CORE, CoreCommandId_GET_PWR_STATE)
        msg = self.device.response(seq)

        #print("getPowerState: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))
        #print(msg)
        res = {}
        res["RecVer"] = int.from_bytes(msg.data[0], "big")
        res["PowerState"] = int.from_bytes(msg.data[1], "big")
        res["BattVoltage"] = ( (int.from_bytes(msg.data[2], "big") << 8) + int.from_bytes(msg.data[3], "big") ) / 100.0
        res["NumCharges"] = (int.from_bytes(msg.data[4], "big") << 8) + int.from_bytes(msg.data[5], "big")
        res["TimeSinceChg"] = (int.from_bytes(msg.data[6], "big") << 8) + int.from_bytes(msg.data[7], "big")

        return (ResponseCode_OK, res)

    def setPowerNotification(self, enable=True):
        """This enables Sphero to asynchronously notify the Client periodically
        with the power state or immediately when the power manager detects a statechange.
        Timed notifications arrive every 10 seconds until they're explicitly disabled
        or Sphero is unpaired. The flag is as you would expect, 00h to disable and 01h
        to enable. This setting is volatile and therefore not retained across sleep cycles"""

        flag_enable = b'\x01' if enable else b'\x00'
        seq = self.device.sendCommand(DeviceId_CORE, CoreCommandId_SET_PWR_NOTIFY, [flag_enable])
        msg = self.device.response(seq)

        #print("setPowerNotification: ", msg.mrsp)
        return (msg.mrsp, None)

    def sleep(self, secSleepDuration=65535):
        """This command puts Sphero to sleep immediately. There are three optional parameters that program the
        robot for future actions:

            Wakeup: The number of seconds for Sphero to sleep for and then automatically
            reawaken. Zero does not program a wakeup interval, so he sleeps forever.
            FFFFh attempts to put him into deep sleep (if supported in hardware) and
            returns an error if the hardware does notsupport it.

            MacroIf non-zero, Sphero will attempt to run this macro ID upon wakeup.

            orbBasicIf non-zero, Sphero will attempt to run an orbBasic program in Flash from
            this line number."""

        wakemsb = ((secSleepDuration >> 8) & 255).to_bytes(1,"big")
        wakelsb = (secSleepDuration & 255).to_bytes(1,"big")
        macro = b'\x00'
        orbmsb = b'\x00'
        orblsb = b'\x00'
        data = [wakemsb, wakelsb, macro, orbmsb, orblsb]
        seq = self.device.sendCommand(DeviceId_CORE, CoreCommandId_SLEEP, data)
        msg = self.device.response(seq)

        #print("sleep: ", msg.mrsp)
        return (msg.mrsp, None)

    def _getVoltageTripPoints(self):
        """This returns the voltage trip points for what Sphero considers
        Low battery and Critical battery. The values are expressed in 100ths
        of a volt, so the defaults of 7.00V and 6.50V respectively are returned
        as 700 and 650."""

        seq = self.device.sendCommand(DeviceId_CORE, CoreCommandId_GET_POWER_TRIPS)
        msg = self.device.response(seq)

        #print("_getVoltageTripPoints: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))
        res = {}
        res["voltLow"] = ((int.from_bytes(msg.data[0], "big") << 8) + int.from_bytes(msg.data[1], "big")) / 100.0
        res["voltCritical"] = ((int.from_bytes(msg.data[2], "big") << 8) + int.from_bytes(msg.data[3], "big")) / 100.0

        return (ResponseCode_OK, res)

    def _setVoltageTripPoints(self, voltLow=700, voltCritical=650):
        """This assigns the voltage trip points for Low and Critical battery voltages. The values are specified in
        100ths of a voltand the limitations on adjusting these away from their defaults are:

        +Vlow must be in the range 675 to 725(±25)
        +Vcrit must be in the range 625 to 675(±25)
        +There must be 0.25V of separation between the two values

        Shifting these values too low could result in very little warning before Sphero forces himself to sleep,
        depending on the age and history of the battery pack.So be careful"""

        voltLow = voltLow * 100
        voltLowMSB = ((voltLow >> 8) & 255).to_bytes(1,"big")
        voltLowLSB = (voltLow & 255).to_bytes(1,"big")

        voltCritical = voltCritical * 100
        voltCriticalMSB = ((voltCritical >> 8) & 255).to_bytes(1,"big")
        voltCriticalLSB = (voltCritical & 255).to_bytes(1,"big")

        data = [voltLowMSB, voltLowLSB, voltCriticalMSB, voltCriticalLSB]
        seq = self.device.sendCommand(DeviceId_CORE, CoreCommandId_SET_POWER_TRIPS, data)
        msg = self.device.response(seq)

        #print("_setVoltageTripPoints: ", msg.mrsp)
        return (msg.mrsp, None)

    def setInactivityTimeout(self, secInactivityTimeout=600):
        """To save battery power, Sphero normally goes to sleep after a period of inactivity. From the factory this
        value is set to 600 seconds (10 minutes) but this API command can alter it to any value of 60 seconds or
        greater.

        The inactivity timer is reset every time an API command is received over Bluetooth or a shell command
        is executed in User Hack mode. In addition, the timer is continually reset when a macro is running unless
        the MF_STEALTH flag is set, and the same for orbBasic unless the BF_STEALTH flag is set."""

        secInactivityTimeoutMSB = ((secInactivityTimeout >> 8) & 255).to_bytes(1,"big")
        secInactivityTimeoutLSB = (secInactivityTimeout & 255).to_bytes(1,"big")

        data = [secInactivityTimeoutMSB, secInactivityTimeoutLSB]
        seq = self.device.sendCommand(DeviceId_CORE, CoreCommandId_SET_INACTIVE_TIMER, data)
        msg = self.device.response(seq)

        #print("setInactivityTimeout: ", msg.mrsp)
        return (msg.mrsp, None)

    def _jumpToBootloader(self):
        """This command requests a jump into the Bootloaderto prepare for a firmware download. It always
        succeeds, because you can always stop where you are, shut everything down and transfer execution. All
        commands after this one must comply with the Bootloader Protocol Specification, which is a separate
        document.

        Note that just because you can always vector into the Bootloader, it doesn't mean you can get anything
        done. Further details are explained in the associated document but in short: the Bootloader doesn't
        implement the entire Core Device messageset and if the battery is deemed too low to execute
        reflashing operations, all you can do is return to the Main Application."""

        seq = self.device.sendCommand(DeviceId_CORE, CoreCommandId_GOTO_BL)
        msg = self.device.response(seq)

        #print("_jumpToBootloader: ", msg.mrsp)
        return (msg.mrsp, None)

    def _performLevel1Diagnostics(self):
        """This is a developer-level command to help diagnose aberrant behavior. Most system counters, process
         flags, and system states are decoded into human readable ASCII. There are two responses to this
         command: a Simple Response followed by a large async message containing the results of the diagnostic
         tests. As of FW version 0.99, the answer was well over 1K in length and similar to:"""

        seq = self.device.sendCommand(DeviceId_CORE, CoreCommandId_RUN_L1_DIAGS)
        msg = self.device.response(seq)

        #print("_performLevel1Diagnostics: ", msg.mrsp)
        return (msg.mrsp, None)

    def _performLevel2Diagnostics(self):
        seq = self.device.sendCommand(DeviceId_CORE, CoreCommandId_RUN_L2_DIAGS)
        msg = self.device.response(seq)

        #print("_performLevel2Diagnostics: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))
        res = {}
        res["RecVer"] = (int.from_bytes(msg.data[0], "big") << 8) | int.from_bytes(msg.data[1], "big")

        #empty: int.from_bytes(msg.data[1], "big")

        res["Rx_Good"] = (int.from_bytes(msg.data[3], "big") << 24) | (int.from_bytes(msg.data[4], "big") << 16) | (int.from_bytes(msg.data[5], "big") << 8) | int.from_bytes(msg.data[6], "big")
        res["Rx_Bad_DID"] = (int.from_bytes(msg.data[7], "big") << 24) | (int.from_bytes(msg.data[8], "big") << 16) | (int.from_bytes(msg.data[9], "big") << 8) | int.from_bytes(msg.data[10], "big")
        res["Rx_Bad_DLEN"] = (int.from_bytes(msg.data[11], "big") << 24) | (int.from_bytes(msg.data[12], "big") << 16) | (int.from_bytes(msg.data[13], "big") << 8) | int.from_bytes(msg.data[14], "big")
        res["Rx_Bad_CID"] = (int.from_bytes(msg.data[15], "big") << 24) | (int.from_bytes(msg.data[16], "big") << 16) | (int.from_bytes(msg.data[17], "big") << 8) | int.from_bytes(msg.data[18], "big")
        res["Rx_Bad_CHK"] = (int.from_bytes(msg.data[19], "big") << 24) | (int.from_bytes(msg.data[20], "big") << 16) | (int.from_bytes(msg.data[21], "big") << 8) | int.from_bytes(msg.data[22], "big")
        res["Rx_Buff_Ovr"] = (int.from_bytes(msg.data[23], "big") << 24) | (int.from_bytes(msg.data[24], "big") << 16) | (int.from_bytes(msg.data[25], "big") << 8) | int.from_bytes(msg.data[26], "big")
        res["Tx_Msgs"] = (int.from_bytes(msg.data[27], "big") << 24) | (int.from_bytes(msg.data[28], "big") << 16) | (int.from_bytes(msg.data[29], "big") << 8) | int.from_bytes(msg.data[30], "big")
        res["Tx_Buff_Ovr"] = (int.from_bytes(msg.data[31], "big") << 24) | (int.from_bytes(msg.data[32], "big") << 16) | (int.from_bytes(msg.data[33], "big") << 8) | int.from_bytes(msg.data[34], "big")

        res["LastBootReason"] = int.from_bytes(msg.data[35], "big")

        l = []
        for i in range(36, 2, 68):
            l.append((int.from_bytes(msg.data[i], "big") << 8) | int.from_bytes(msg.data[i+1], "big"))
        res["BootCounters"] = l

        #empty: (int.from_bytes(msg.data[68], "big") << 8) | int.from_bytes(msg.data[69], "big")

        res["ChargeCount"] = (int.from_bytes(msg.data[70], "big") << 8) | int.from_bytes(msg.data[71], "big")
        res["SecondsSinceCharge"] = (int.from_bytes(msg.data[72], "big") << 8) | int.from_bytes(msg.data[73], "big")
        res["SecondsOn"] = (int.from_bytes(msg.data[74], "big") << 24) | (int.from_bytes(msg.data[75], "big") << 16) | (int.from_bytes(msg.data[76], "big") << 8) | int.from_bytes(msg.data[77], "big")
        res["DistanceRolled"] = (int.from_bytes(msg.data[78], "big") << 24) | (int.from_bytes(msg.data[79], "big") << 16) | (int.from_bytes(msg.data[80], "big") << 8) | int.from_bytes(msg.data[81], "big")
        res["SensorFailures"] = (int.from_bytes(msg.data[82], "big") << 8) | int.from_bytes(msg.data[83], "big")
        res["GyroAdjustCount"] = (int.from_bytes(msg.data[84], "big") << 24) | (int.from_bytes(msg.data[85], "big") << 16) | (int.from_bytes(msg.data[86], "big") << 8) | int.from_bytes(msg.data[87], "big")

        return (ResponseCode_OK, res)

    def _clearCouters(self):
        """This is a developers-only command to clear the various system counters described in command 41h. It is
        denied when Sphero is in Normal mode"""

        seq = self.device.sendCommand(DeviceId_CORE, CoreCommandId_CLEAR_COUNTERS)
        msg = self.device.response(seq)

        #print("_clearCouters: ", msg.mrsp)
        return (msg.mrsp, None)

    def _assignTimeValue(self, timeValue=0):
        """Sphero contains a 32-bit counter that increments every millisecond. It has no absolute temporal
        meaning, just a relative one. This command assigns the counter a specific value for subsequent
        sampling.Though it starts at zero when Sphero wakes up, assigning it too high of a value with this
        command could cause it to roll over."""

        data = [((timeValue >> 24) & 255).to_bytes(1,"big"), ((timeValue >> 16) & 255).to_bytes(1,"big"), ((timeValue >> 8) & 255).to_bytes(1,"big"), ((timeValue) & 255).to_bytes(1,"big")]
        seq = self.device.sendCommand(DeviceId_CORE, CoreCommandId_ASSIGN_TIME, data)
        msg = self.device.response(seq)

        #print("_assignTimeValue: ", msg.mrsp)
        return (msg.mrsp, None)

    def pollPacketTimes(self):
        """This command helps the Client application profile the transmission and processing latencies in Sphero so
        that a relative synchronization of timebases can be performed. This technique is based upon the scheme
        in theNetwork Time Protocol (RFC 5905) and allows the Client to reconcile time stamped messages
        from Sphero to its own time stamped events.In the following discussion, each 32-bit value is a count of
        milliseconds from some referencewithin the device.

        The scheme is as follows: the Client sends the command with the Client Tx time (T1) filled in. Upon
        receipt of the packet, the command processor in Sphero copies that time into the response packet and
        places the current value of the millisecond counter into the Sphero Rx time field(T2). Just before the
        transmit engine streams it into the Bluetooth module, the Sphero Tx time value (T3) is filled in. If the
        Client then records the time at which the response is received (T4) the relevant time segments can be
        computed from the four time stampsT1-T4:

            -The value offset represents the maximum-likelihood time offset of the Client clock to Sphero's
            system clock:

                    offset = 1/2 * [(T2 -T1) + (T3 -T4)]

            -The value delay represents the round-trip delay between the Client and Sphero:

                    delay = (T4 -T1) -(T3 -T2)
        """

        spheroTxTime = int(round(time.time() * 1000))
        data = [((spheroTxTime >> 24) & 255).to_bytes(1,"big"), ((spheroTxTime >> 16) & 255).to_bytes(1,"big"), ((spheroTxTime >> 8) & 255).to_bytes(1,"big"), ((spheroTxTime) & 255).to_bytes(1,"big")]
        seq = self.device.sendCommand(DeviceId_CORE, CoreCommandId_POLL_TIMES, data)
        msg = self.device.response(seq)
        t4 = int(round(time.time() * 1000))

        #print("pollPacketTimes: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))
        t1 = spheroTxTime#(int.from_bytes(msg.data[0], "big") << 24) | (int.from_bytes(msg.data[1], "big") << 16) | (int.from_bytes(msg.data[2], "big") << 8) | int.from_bytes(msg.data[3], "big")
        t2 = (int.from_bytes(msg.data[4], "big") << 24) | (int.from_bytes(msg.data[5], "big") << 16) | (int.from_bytes(msg.data[6], "big") << 8) | int.from_bytes(msg.data[7], "big")
        t3 = (int.from_bytes(msg.data[8], "big") << 24) | (int.from_bytes(msg.data[9], "big") << 16) | (int.from_bytes(msg.data[10], "big") << 8) | int.from_bytes(msg.data[11], "big")

        res = {}
        res["offset"] = ((t2-t1) + (t3-t4)) / 2
        res["delay"] = (t4-t1) - (t3-t2)

        return (ResponseCode_OK, res)

    #*******************************************************************************************************/
    #***********************************        Sphero commands         *************************************
    #*******************************************************************************************************/
    def setHeading(self, heading):
        """This allows the smartphone client to adjust the orientation of Sphero by commanding a new reference
        heading in degrees, which ranges from 0 to 359. You will see the ball respond immediately to this
        command if stabilization is enabled.

        In FW version 3.10 and later thisalso clears the maximum value counters for the rate gyro, effectively
        re-enabling the generation of an async message alerting the client to this event."""

        data = [((heading >> 8) & 255).to_bytes(1,"big"), (heading & 255).to_bytes(1,"big")]
        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SET_CAL, data)
        msg = self.device.response(seq)

        #print("setHeading: ", msg.mrsp)
        return (msg.mrsp, None)

    def setStabilisation(self, enable=True):
        """This turns on or off the internal stabilization of Sphero, in which the IMU is used to match the ball's
        orientation to its various set points. The flag value is as you would expect, 00h for off and 01h for on.
        Stabilization is enabled by default when Sphero powers up. You will want to disable stabilization when
        using Sphero as an external input controlleror even to save battery power during testing that doesn't
        involve movement (orbBasic, etc.)

        An error is returned if the sensor network is dead; without sensors the IMU won't operate and thus
        there is no feedback to control stabilization"""

        flag_enable = b'\x01' if enable else b'\x00'
        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SET_STABILIZ, [flag_enable])
        msg = self.device.response(seq)

        #print("setStabilisation: ", msg.mrsp)
        return (msg.mrsp, None)

    def _setRotationRate(self, rate=128):
        """This allows you to control the rotation rate that Sphero will use to meet new heading commands(DID
        02h, CID 01h). A lower value offers better control but with a larger turning radius. A higher value will
        yield quick turnsbut Sphero may roll over on itselfand lose control.

        The commanded valueisin units of 0.784 degrees/sec. So, setting a value of C8h will set the rotation
        rate to 157 degrees/sec. A value of 255 jumps to the maximum (currently 400 degrees/sec). A value of
        zero doesn't make muchsense so it's interpreted as 1, the minimum."""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SET_ROTATION_RATE, [rate.to_bytes(1,"big")])
        msg = self.device.response(seq)

        #print("setRotationRate: ", msg.mrsp)
        return (msg.mrsp, None)

    def getChassisId(self):
        """Returns the Chassis ID, a 16-bit value, which was set at the factory"""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_GET_CHASSIS_ID)
        msg = self.device.response(seq)

        #print("getChassisId: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))

        res = {}
        res["chassisId"] = (int.from_bytes(msg.data[0], "big") << 8) | int.from_bytes(msg.data[1], "big")

        return (ResponseCode_OK, res)

    def selfLevel(self, op):
        """This command controls the self level routine. The self level routine attempts to achieve a horizontal
        orientation where pitch and roll angles are less than the provided Angle Limit. After both angle limits are
        satisfied, option bits control sleep, final angle (heading), and control system on/off. An asynchronous
        message is returned when the self level routine completes (only when started by API call). The required
        parameters are:

         + Bit 0: (Start/Stop) 0 aborts the routine if in progress. 1 starts the routine.
         + Bit 1: (Final Angle) 0 just stops. 1 rotates to heading equal to beginning heading.
         + Bit 2: (Sleep) 0 stays awake after leveling. 1 goes to sleep after leveling.
         + Bit 3: (Control System) 0 leaves control system off. 1 leaves control system on (after leveling).

         + Angle Limit:
                0     Use the default value
            1 to 90   Set the max angle for completion (in degrees)

         + Timeout
                0     Use the default value
            1 to 255  Set maximum seconds to run the routine

         + True Time
                0     Use the default value
            1 to 255  Set the required “test for levelness” time to 10*True Time (in milliseconds)

        Default values are: Angle = 3, Timeout = 15, True Time = 30 (300 milliseconds)
        True Time*10 specifies the number of milliseconds that the pitch and roll angles must remain below the
        Angle Limit after the routine completes. If one of the values exceeds the Angle Limit, the ball will self
        level again and the accuracy timer will start again from 0."""

        data = []
        aux = ( (op['controlSystem'] << 3) | (op['sleep'] << 2) | (op['finalAngle'] << 1) | op['startStop'] ) & 255
        data.append(aux.to_bytes(1,"big"))
        data.append( (op['angleLimit'] & 255).to_bytes(1,"big") )
        data.append( (op['timeout'] & 255).to_bytes(1,"big") )
        data.append( (op['trueTime'] & 255).to_bytes(1,"big") )

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SELF_LEVEL, data)
        msg = self.device.response(seq)

        #print("selfLevel: ", msg.mrsp)
        return (msg.mrsp, None)

    def setDataStreaming(self, op):
        """Sphero supports asynchronous data streaming of certain control system and sensor parameters. This
        command selects the internal sampling frequency, packet size, parameter mask and optionally, the total
        number of packets.

         + N: Divisor of the maximum sensor sampling rate
         + M: Number of sample frames emitted per packet
         + MASK: Bitwise selector of data sources to stream
         + PCNT: Packet count 1-255 (or 0 for unlimited streaming)
         + MASK2: Bitwise selector of more data sources to stream (optional)

        MASK and PCNT are pretty obvious but the N, M terms bear a little more explanation. Currently the
        control system runs at 400Hz and because it's pretty unlikely you will want to see data at that rate, N
        allows you to divide that down. N = 2 yields data samples at 200Hz, N = 10, 40Hz, etc. Every data sample
        consists of a "frame" made up of the individual sensor values as defined by the MASK. The M value
        defines how many frames to collect in memory before the packet is emitted. In this sense, it controls the
        latency of the data you receive. Increasing N and the number of bits set in MASK drive the required
        throughput. You should experiment with different values of N, M and MASK to see what works best for you.

        The MASK2 bitfield was added to extend MASK when we developed more than 32 data sources. The API
        processor is implemented so that this value is optional; if it isn't included then all of its bits are set to
        zero. (Added in FW 1.15)

        Each parameter is returned as a 16-bit signed integer. The table below defines the bits in MASK to those
        parameters with the indicated ranges and units. If the command is issued with a MASK of zero, then
        data streaming is disabled."""

        data = []
        data.append( ((op['N'] >> 8) & 255).to_bytes(1,"big") )
        data.append( (op['N'] & 255).to_bytes(1,"big") )

        data.append( ((op['M'] >> 8) & 255).to_bytes(1,"big") )
        data.append( (op['M'] & 255).to_bytes(1,"big") )

        mask = ((op['accelXRaw'] & 255) << 7) + ((op['accelYRaw'] & 255) << 6) + ((op['accelZRaw'] & 255) << 5) + ((op['gyroXRaw'] & 255) << 4)
        mask = mask + ((op['gyroYRaw'] & 255) << 3) + ((op['gyroZRaw'] & 255) << 2)
        data.append(mask.to_bytes(1,"big"))

        mask = ((op['rightEMFRaw'] & 255) << 6) + ((op['leftEMFRaw'] & 255) << 5) + ((op['leftPWMRaw'] & 255) << 4)
        mask = mask + ((op['rightPWMRaw'] & 255) << 3) + ((op['pitchIMU'] & 255) << 2) + ((op['rollIMU'] & 255) << 1) + (op['yawIMU'] & 255)
        data.append(mask.to_bytes(1,"big"))

        mask = ((op['accelX'] & 255) << 7) + ((op['accelY'] & 255) << 6) + ((op['accelZ'] & 255) << 5) + ((op['gyroX'] & 255) << 4)
        mask = mask + ((op['gyroY'] & 255) << 3) + ((op['gyroZ'] & 255) << 2)
        data.append(mask.to_bytes(1,"big"))

        mask = ((op['rightEMF'] & 255) << 6) + ((op['leftEMF'] & 255) << 5)
        data.append(mask.to_bytes(1,"big"))

        data.append( (op['PCNT'] & 255).to_bytes(1,"big") )

        mask = ((op['q0'] & 255) << 7) + ((op['q1'] & 255) << 6) + ((op['q2'] & 255) << 5) + ((op['q3'] & 255) << 4)
        mask = mask + ((op['odometerX'] & 255) << 3) + ((op['odometerY'] & 255) << 2) + ((op['accelOne'] & 255) << 1) + (op['velocityX'] & 255)
        data.append(mask.to_bytes(1,"big"))

        mask = (op['velocityY'] << 7)
        data.append(mask.to_bytes(1,"big"))
        data.append(b'\x00')
        data.append(b'\x00')

        self.stream = op
        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SET_DATA_STREAMING, data)
        msg = self.device.response(seq)

        #print("setDataStreaming: ", msg.mrsp)
        return (msg.mrsp, None)

    def configureCollisionDetection(self, op):
        """Sphero contains a powerful analysis function to filter accelerometer data in order to detect collisions.
        Because this is a great example of a high-level concept that humans excel and –but robots do not– a
        number of parameters control the behavior.  When a collision is detected anasynchronous message is
        generated to the client. The configuration fields are defined as follows:

            meth: Detection method type to use. Supportedmethods are 01h, 02h, and 03h (see the collision
                  detection document for details). Use00h to completely disable this service.

            Xt, Yt: An 8-bit settable threshold for the X (left/right) and Y (front/back) axes of Sphero.
                  A value of 00h disables the contribution of that axis.

            Xspd, Yspd: An 8-bit settable speed value for the X and Y axes. This setting is ranged by the speed,
                  then added to Xt, Yt to generate the final threshold value.

            Dead: An 8-bit post-collision dead timeto prevent retriggering; specifiedin 10ms increments.
        """

        data = []
        data.append( (op['meth'] & 255).to_bytes(1,"big") )
        data.append( (op['xt'] & 255).to_bytes(1,"big") )
        data.append( (op['xspd'] & 255).to_bytes(1,"big") )
        data.append( (op['yt'] & 255).to_bytes(1,"big") )
        data.append( (op['yspd'] & 255).to_bytes(1,"big") )
        data.append( (op['dead'] & 255).to_bytes(1,"big") )

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SET_COLLISION_DET, data)
        msg = self.device.response(seq)

        #print("configureCollisionDetection: ", msg.mrsp)
        return (msg.mrsp, None)

    def configureLocator(self, op):
        """Through the streaming interface, Sphero provides real-time location data in the form of (X,Y)
        coordinates on the ground plane. When Sphero wakes up it has coordinates (0,0) and heading 0, which
        corresponds to facing down the positive Y­‐axis with the positive X‐axis to your right. This command
        allows you to move Sphero to a new location and change the alignment of locator coordinates with IMU
        headings.

        When Sphero receives a Set Heading command it changes which direction corresponds to heading 0. By
        default, the locator compensates for this by modifying its value for yaw tare so that the Y-­axis is still
        pointing in the same real-­world direction. For instance, if you wake up Sphero and drive straight, you
        will be driving down the Y­‐axis. If you use the Set Heading feature in the drive app to turn 90 degrees,
        you will still have heading 0, but the locator knows you have turned 90 degrees and are now facing
        down the X­‐axis. This feature can be turned off, in which case the locator knows nothing about the Set
        Heading command. This can lead to some strange results. For instance, if you drive using only roll
        commands with heading 0 and set heading commands to change direction the locator will perceive your
        entire path as lying on the Y-­axis.

            Flags: Bit 0 – Determines whether calibrate commands automatically correct the yaw tare value.
                   When false, the positive Y axis coincides with heading 0 (assuming you do not change the
                   yaw tare manually using this API command).
                   Other Bits - Reserved

            X,Y: The current (X,Y) coordinates of Sphero on the ground plane in centimeters.

            Yaw Tare: Controls how the X,Y-plane is aligned with Sphero’s heading coordinate system. When this
                      parameter is set to zero, it means that having yaw = 0 corresponds to facing down the
                      Y-axis in the positive direction.  The value will be interpreted in the range 0-359
                      inclusive.
        """

        data = []
        data.append( (op['autoCalibrate'] & 1).to_bytes(1,"big") )
        data.append( ((op['x'] & 65280) >> 8).to_bytes(1,"big") )
        data.append( (op['x'] & 255).to_bytes(1,"big") )
        data.append( ((op['y'] & 65280) >> 8).to_bytes(1,"big") )
        data.append( (op['y'] & 255).to_bytes(1,"big") )
        data.append( ((op['yawTare'] & 65280) >> 8).to_bytes(1,"big") )
        data.append( (op['yawTare'] & 255).to_bytes(1,"big") )

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_LOCATOR, data)
        msg = self.device.response(seq)

        #print("configureLocator: ", msg.mrsp)
        return (msg.mrsp, None)

    def _setAccelerometerRange(self, rang=2):
        """Normally, Sphero's solid state accelerometer is set for a range of ±8Gs. There may be times when you
        would like to alter this, say to resolve finer accelerations. This command takes an index for the
        supported range as explained below.

            0 ±2Gs
            1 ±4Gs
            2 ±8Gs (default)
            3 ±16Gs

        Note that setting this to other than the default value will have indeterminate consequences for driving
        and collision detection; you shouldn't expect either to work"""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SET_ACCELERO, [rang.to_bytes(1,"big") ])
        msg = self.device.response(seq)

        #print("setAccelerometerRange: ", msg.mrsp)
        return (msg.mrsp, None)

    def readLocator(self):
        """This reads Sphero's current position(X,Y), component velocitiesand SOG (speed over ground). The
        position is a signed value in centimeters, the component velocitiesare signedcm/sec while the SOG is
        unsigned cm/sec."""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_READ_LOCATOR)
        msg = self.device.response(seq)

        #print("readLocator: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))

        res = {}
        aux = ((int.from_bytes(msg.data[0], "big") << 8) & 65535) + (int.from_bytes(msg.data[1], "big") & 65535)
        sig = int.from_bytes(msg.data[0], "big") >> 7
        res["x"] = -aux if sig else aux

        aux = ((int.from_bytes(msg.data[2], "big") << 8) & 65535) + (int.from_bytes(msg.data[3], "big") & 65535)
        sig = int.from_bytes(msg.data[2], "big") >> 7
        res["y"] = -aux if sig else aux

        aux = ((int.from_bytes(msg.data[4], "big") << 8) & 65535) + (int.from_bytes(msg.data[5], "big") & 65535)
        sig = int.from_bytes(msg.data[4], "big") >> 7
        res["vx"] = -aux if sig else aux

        aux = ((int.from_bytes(msg.data[6], "big") << 8) & 65535) + (int.from_bytes(msg.data[7], "big") & 65535)
        sig = int.from_bytes(msg.data[6], "big") >> 7
        res["vy"] = -aux if sig else aux

        b = ((int.from_bytes(msg.data[8], "big") << 8) & 65535) + (int.from_bytes(msg.data[9], "big") & 65535)
        res["sog"] = b

        return (ResponseCode_OK, res)

    def setRGBLedOutput(self, red, green, blue, persist):
        """This allows you to set the RGB LED color. The composite value is stored as the "application LED color"
        and immediately driven to the LED(if not overridden by a macro or orbBasic operation). If FLAG is true,
        the value is alsosaved as the "user LED color" whichpersists across power cyclesand is rendered in the
        gap between an application connecting and sending this command."""

        flag_persist = b'\x01' if persist else b'\x00'
        data = []
        data.append(red.to_bytes(1,"big"))
        data.append(green.to_bytes(1,"big"))
        data.append(blue.to_bytes(1,"big"))
        data.append(flag_persist)

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SET_RGB_LED, data)
        msg = self.device.response(seq)

        #print("setRGBLedOutput: ", msg.mrsp)
        return (msg.mrsp, None)

    def setBackLEDOutput(self, intensity):
        """This allows you to control the brightness of the back LED. The value does not persist across power
        cycles"""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SET_BACK_LED, [intensity.to_bytes(1,"big")])
        msg = self.device.response(seq)

        #print("setBackLEDOutput: ", msg.mrsp)
        return (msg.mrsp, None)

    def getRGBLed(self):
        """This retrieves the "user LED color" which is stored in the config block (which may or may not be actively
        driven to the RGB LED)"""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_GET_RGB_LED)
        msg = self.device.response(seq)

        #print("getRGBLed: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))

        res = {}
        res["red"] = int.from_bytes(msg.data[0], "big")
        res["green"] = int.from_bytes(msg.data[1], "big")
        res["blue"] = int.from_bytes(msg.data[2], "big")

        return (ResponseCode_OK, res)

    def roll(self, speed, heading, state):
        """This commands Sphero to roll along the provided vector. Both a speedand a heading are required; the
        latter is considered relative to the last calibrated direction.A state valueis also provided. In the CES
        firmware, this was used to gate the control system to either obey the roll vector or ignore it and apply
        optimalbraking to zero speed.Please refer to Appendix C for detailed information.

        The client convention for heading follows the 360 degrees on a circle, relative to the ball: 0 is straight
        ahead, 90 is to the right, 180 is back and 270 is to the left. The valid range is 0..359.

        The roll command takes three parameters: heading, speed and a state variable (internally referred to as
        the "go" value). The heading parameter is self explanatory and always acted upon by the control system
        but the other two bear additional explanation.

        As of the 1.13 Sphero firmware their relationship is as follows:

         Go Speed       Result
         1   >0         Normal driving
         1    0         Rotate in place for setting heading if speed is very small. (If sent when Sphero is
                        driving then it plugs the pitch controller for a far too aggressive stop. This should
                        be avoided.)
         2    X         Force fast rotation to this heading independent of speed.
         0    X         Commence optimal braking to zero speed

         Note that beginning in the 1.16 firmware, there are two different rotation speeds employed when acting
         upon the heading parameter. The first is the value set with the Set Rotation Rate command in the
         Sphero DID and is used for normal driving. The second is a much faster rate used to improve
         performance while rotating in place and setting the heading. It defaults to 1,000 degrees/sec but can be
         accessed through the shell commands hss and hgs.

         Beginning in the 1.21 firmware the "go" parameter will also act on a value of 2 to override the speed-
         dependent nature of fast turning."""

        data = []
        data.append(speed.to_bytes(1,"big"))
        data.append( ((heading & 65280) >> 8 ).to_bytes(1,"big"))
        data.append( (heading & 255).to_bytes(1,"big") )
        data.append(state.to_bytes(1,"big"))

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_ROLL, data)
        msg = self.device.response(seq)

        #print("roll: ", msg.mrsp)
        return (msg.mrsp, None)

    def _boost(self, enable=True):
        """Beginning with FW 1.46 (S2) and 3.25(S3), this executes the boost macro from within the SSB.It takes a
        1 byte parameter which is either 01h to begin boosting or 00h to stop."""

        flag_enable = b'\x01' if enable else b'\x00'

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_BOOST, [flag_enable])
        msg = self.device.response(seq)

        #print("boost: ", msg.mrsp)
        return (msg.mrsp, None)

    def setRAWMotorValues(self, modeLeft, powerLeft, modeRight, powerRight):
        """This allows you to take over one or both of the motor output values, instead of having the stabilization
        system control them. Each motor (left andright) requires a mode(see below) and a power value from 0-255.
        This commandwill disablestabilization if both modes aren't"ignore" so you'll need to re-enable it via
        CID 02h once you're done.

            + 00h Off (motor is open circuit)
            + 01h Forward
            + 02h Reverse
            + 03h Brake (motor is shorted)
            + 04h Ignore (motor mode and power is left unchanged)
        """

        data = []
        data.append(modeLeft.to_bytes(1,"big"))
        data.append(powerLeft.to_bytes(1,"big"))
        data.append(modeRight.to_bytes(1,"big"))
        data.append(powerRight.to_bytes(1,"big"))

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SET_RAW_MOTORS, data)
        msg = self.device.response(seq)

        #print("setRAWMotorValues: ", msg.mrsp)
        return (msg.mrsp, None)

    def setMotionTimeout(self, msecTimeout=2000):
        """This sets the ultimate timeout for the last motion command to keep Sphero from rolling away in the
        case of a crashed (or paused) client app. The TIME parameter is expressed in milliseconds and defaults
        to 2000 upon wake-up.

        If the control system is enabled, the timeout triggers a stop otherwise it commands zero PWM to both
        motors. This"termination behavior" is inhibited if a macro is running with the flag MF_EXCLUSIVE_DRV
        set, or an orbBasic program is executing with a similar flag, BF_EXCLUSIVE_DRV.

        Note that you must enable this action by setting System Option Flag #4."""

        data = []
        data.append( ((msecTimeout & 65280) >> 8).to_bytes(1,"big") )
        data.append( (msecTimeout & 255).to_bytes(1,"big") )

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SET_MOTION_TO, data)
        msg = self.device.response(seq)

        #print("setMotionTimeout: ", msg.mrsp)
        return (msg.mrsp, None)

    def setPermanentOptionFlags(self, op):
        """Assigns the permanent option flags to the provided valueand writes them immediately to the config
        block for persistence across power cycles. See below for the bit definitions."""

        data = []
        data.append(b'\x00')
        data.append(b'\x00')

        aux = 1 & op['gyroMaxAsync']
        data.append(aux.to_bytes(1,"big"))

        aux1 = (op['sleepCharge'] + (op['vectorDrive'] << 1) + (op['selfLevelingCharger'] << 2) + (op['forceTailLED'] << 3)) & 255
        aux2 = ((op['motionTimeOuts'] + (op['retailDemoMode'] << 1) + (op['awakeLight'] << 2) + (op['awakeHeavy'] << 3)) << 4) & 255
        aux = aux1 + aux2
        data.append(aux.to_bytes(1,"big"))

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SET_OPTIONS_FLAG, data)
        msg = self.device.response(seq)

        #print("setPermanentOptionFlags: ", msg.mrsp)
        return (msg.mrsp, None)

    def getPermanentOptionFlags(self):
        """Returns the permanent option flags as a bitfieldas defined below:

            + 0 Set to prevent Sphero from immediately going to sleep when
                placed in the charger andconnected over Bluetooth.
            + 1 Set to enable Vector Drive, that is, when Sphero is stopped
                and a new roll command is issued it achieves the heading before
                moving along it.
            + 2 Set to disable self-leveling when Sphero is inserted into the charger.
            + 3 Set to force the tail LED always on.
            + 4 Set to enable motion timeouts (seeDID 02h, CID 34h)
            + 5 Set to enable retail Demo Mode (when placed in the charger, ball
                runs a slow rainbow macro for 60 minutes and then goes to sleep).
            + 6 Set double tap awake sensitivity to Light
            + 7 Set double tap awake sensitivity to Heavy
            + 8 Enable gyro max asyncmessage(NOT SUPPORTED IN VERSION 1.47)
            + 6-31 Unassigned
        """

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_GET_OPTIONS_FLAG)
        msg = self.device.response(seq)

        #print("getRGBLed: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))

        res = {}
        res["sleepCharge"] = int.from_bytes(msg.data[3], "big") & 1
        res["vectorDrive"] = (int.from_bytes(msg.data[3], "big") >> 1) & 1
        res["selfLevelingCharger"] = (int.from_bytes(msg.data[3], "big") >> 2) & 1
        res["forceTailLED"] = (int.from_bytes(msg.data[3], "big") >> 3) & 1
        res["motionTimeOuts"] = (int.from_bytes(msg.data[3], "big") >> 4) & 1
        res["retailDemoMode"] = (int.from_bytes(msg.data[3], "big") >> 5) & 1
        res["awakeLight"] = (int.from_bytes(msg.data[3], "big") >> 6) & 1
        res["awakeHeavy"] = (int.from_bytes(msg.data[3], "big") >> 7) & 1
        res["gyroMaxAsync"] = int.from_bytes(msg.data[2], "big") & 1

        return (ResponseCode_OK, res)

    def setTemporaryOptionFlags(self, flag):
        """Enable Stop On Disconnect behavior: when the Bluetooth link transitions from
        connected to disconnected, Sphero is commanded to stop rolling. This is ignored
        if a macro or orbBasicprogram is running though both have option flags to allow
        this during their execution. This flag is cleared after it is obeyed, thus it
        is a one-shot."""

        data = []
        data.append(b'\x00')
        data.append(b'\x00')
        data.append(b'\x00')
        data.append( (1 & flag).to_bytes(1,"big") )

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SET_TEMP_OPTIONS_FLAG, data)
        msg = self.device.response(seq)

        #print("setTemporaryOptionFlags: ", msg.mrsp)
        return (msg.mrsp, None)

    def getTemporaryOptionFlags(self):
        """Enable Stop On Disconnect behavior: when the Bluetooth link transitions from
        connected to disconnected, Sphero is commanded to stop rolling. This is ignored
        if a macro or orbBasicprogram is running though both have option flags to allow
        this during their execution. This flag is cleared after it is obeyed, thus it
        is a one-shot."""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_GET_TEMP_OPTIONS_FLAG)
        msg = self.device.response(seq)

        #print("getTemporaryOptionFlags: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))
        res = int.from_bytes(msg.data[3], "big") & 1

        return (ResponseCode_OK, res)

    def _getConfigurationBlock(self, id):
        """This command retrieves one of the configuration blocks. The response is a simple one; an error code of
        08h is returned when the resources are currently unavailable to send the requested block back. The
        actual configuration block data returns in an asynchronous message of type 04h due to its length (if
        there is no error).

            ID = 00h requests the factory configuration block
            ID = 01h requests the user configuration block, which is updated with current values first
        """

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SET_TEMP_OPTIONS_FLAG, [id.to_bytes(1,"big")])
        msg = self.device.response(seq)

        #print("getConfigurationBlock: ", msg.mrsp)
        return (msg.mrsp, None)

    def _setSSBModifierBlock(self, pwd, op):
        """This development-only command allows the SSB to be patched with a new modifier block, including the
        Boost macro. The changes take effectimmediately."""

        data = []
        data.append( ((pwd >> 24) & 255).to_bytes(1,"big") )
        data.append( ((pwd >> 16) & 255).to_bytes(1,"big") )
        data.append( ((pwd >> 8) & 255).to_bytes(1,"big") )
        data.append( (pwd & 255).to_bytes(1,"big") )

        data.append( bytearray(op) )

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SET_SSB_PARAMS, data)
        msg = self.device.response(seq)

        #print("setSSBModifierBlock: ", msg.mrsp)
        return (msg.mrsp, None)

    def _setDeviceMode(self, enableHackMode=False):
        """Assigns the operation mode of Sphero based on the supplied mode value:

            00h Normal mode
            01h User Hack mode(see below)

        User Hack mode enables ASCII shell commands; refer to the associated document for a detailed list
        of operations."""

        flag_enableHackMode = b'\x01' if enableHackMode else b'\x00'

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SET_DEVICE_MODE, [flag_enableHackMode])
        msg = self.device.response(seq)

        #print("setDeviceMode: ", msg.mrsp)
        return (msg.mrsp, None)

    def _setConfigurationBlock(self, block):
        """This command accepts an exact copy of the configuration block and loads it into the RAM copy of the
        configuration block.  Then the RAM copy is saved to flash.  The configuration block can be obtained by
        using the Get Configuration Block command."""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SET_CFG_BLOCK, block)
        msg = self.device.response(seq)

        #print("setConfigurationBlock: ", msg.mrsp)
        return (msg.mrsp, None)

    def _getDeviceMode(self):
        """This returns the current device mode, 00h for Normal mode or 01h for User Hack mode."""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_GET_DEVICE_MODE)
        msg = self.device.response(seq)

        #print("getDeviceMode: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))
        res = int.from_bytes(msg.data[0], "big")

        return (ResponseCode_OK, res)

    def _getSSB(self):
        """This command retrieves Sphero'sSoul Block. The response is simpleand then the actual block of
        soulular data returns in an asynchronous message of type 0Dh due to its 0x400 byte length (if there
        is no error)."""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_GET_SSB)
        msg = self.device.response(seq)

        #print("getSSB: ", msg.mrsp)
        return (msg.mrsp, None)

    def _setSSB(self, password, block):
        """This command sets Sphero's Soul Block. The actual payload length is 404h bytes but if you use the
        special DLEN encoding of ffh, Sphero will know what to expect. You need to supply the password in
        order for it to work."""

        data = []
        data.append( ((password >> 24) & 255).to_bytes(1,"big") )
        data.append( ((password >> 16) & 255).to_bytes(1,"big") )
        data.append( ((password >> 8) & 255).to_bytes(1,"big") )
        data.append( (password & 255).to_bytes(1,"big") )

        data.append( bytearray(block) )

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SET_SSB, data)
        msg = self.device.response(seq)

        #print("setSSB: ", msg.mrsp)
        return (msg.mrsp, None)

    def _refillBank(self, typeOp):
        """This command attempts to refill either the Boost bank (TYPE = 00h) or the Shield bank (TYPE = 01h) by
        attempting to deduct the respective refill cost from the current number of cores. If it succeeds the bank
        is set to the maximum attainable for that level, the cores are spent and an API success response is
        returned with the lower core balance. This also commits the SSB to flash to register this transaction.

        If there are not enough cores available to spend the API responds with an EEXEC error (code 08h)."""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SSB_REFILL, [typeOp.to_bytes(1,"big")])
        msg = self.device.response(seq)

        #print("refillBank: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))
        res = (int.from_bytes(msg.data[0], "big") << 24) | (int.from_bytes(msg.data[1], "big") << 16) | (int.from_bytes(msg.data[2], "big") << 8) | int.from_bytes(msg.data[3], "big")

        return (ResponseCode_OK, res)

    def _buyConsumable(self, idOp, quantity):
        """This command attempts to spend cores on consumables. The consumable ID (0..7) is given as well as the
        quantity requested to purchase. If the purchase succeeds the consumable count is increased, the cores
        are spent and an API success responseis returned with both the increased consumable quantity and
        lower core balance. This also commits the SSB to flash to register this transaction.

        If there are not enough cores available to spend or the purchase would exceed the max consumable
        quantity of 255 the API responds with an EEXEC error (code 08h)."""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SSB_BUY, [idOp.to_bytes(1,"big"), quantity.to_bytes(1,"big")])
        msg = self.device.response(seq)

        #print("buyConsumable: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))
        res['QTY'] = int.from_bytes(msg.data[0], "big")
        res['cores'] = (int.from_bytes(msg.data[1], "big") << 24) | (int.from_bytes(msg.data[2], "big") << 16) | (int.from_bytes(msg.data[3], "big") << 8) | int.from_bytes(msg.data[4], "big")

        return (ResponseCode_OK, res)

    def _useConsumable(self, idOp):
        """Attempt to use a consumable (run a macro) if the quantity remaining is non-zero. On success the return
        message echoes the ID of this consumable and how many of them remain. Note that this will NOT
        immediately commit the SSB to flash.

        If the associated macro is already runningor the quantity remaining is zero, this returns an EEXEC error
        (code 08h)."""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SSB_USE_CONSUMEABLE, [idOp.to_bytes(1,"big")])
        msg = self.device.response(seq)

        #print("useConsumable: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))
        res['id'] = int.from_bytes(msg.data[0], "big")
        res['QTY'] = int.from_bytes(msg.data[1], "big")

        return (ResponseCode_OK, res)

    def _grantCores(self, password, quantity, flags):
        """This command adds the supplied number of cores.If the first bit in the flags byte is set the command
        immediately commits the SSB to flash.  Otherwise it does not.All other bits are reserved.  If the
        password is not accepted, this command fails without consequence."""

        data = []
        data.append( ((password >> (8 * 0)) & 255).to_bytes(1,"big") )
        data.append( ((password >> (8 * 1)) & 255).to_bytes(1,"big") )
        data.append( ((password >> (8 * 2)) & 255).to_bytes(1,"big") )
        data.append( ((password >> (8 * 3)) & 255).to_bytes(1,"big") )

        data.append( ((quantity >> (8 * 0)) & 255).to_bytes(1,"big") )
        data.append( ((quantity >> (8 * 1)) & 255).to_bytes(1,"big") )
        data.append( ((quantity >> (8 * 2)) & 255).to_bytes(1,"big") )
        data.append( ((quantity >> (8 * 3)) & 255).to_bytes(1,"big") )
        data.append(flags.to_bytes(1,"big"))

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SSB_GRANT_CORES, data)
        msg = self.device.response(seq)

        #print("grantCores: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))
        res = (int.from_bytes(msg.data[0], "big") << 24) | (int.from_bytes(msg.data[1], "big") << 16) | (int.from_bytes(msg.data[2], "big") << 8) | int.from_bytes(msg.data[3], "big")

        return (ResponseCode_OK, res)

    def _addXP(self, password, quantity):
        """This command increases XP by adding the supplied number of minutes of drive timeand immediately
        commits the SSB to flash. If the password is not accepted, this command fails without consequence."""

        data = []
        data.append( ((password >> (8 * 0)) & 255).to_bytes(1,"big") )
        data.append( ((password >> (8 * 1)) & 255).to_bytes(1,"big") )
        data.append( ((password >> (8 * 2)) & 255).to_bytes(1,"big") )
        data.append( ((password >> (8 * 3)) & 255).to_bytes(1,"big") )

        data.append( ((quantity >> (8 * 0)) & 255).to_bytes(1,"big") )
        data.append( ((quantity >> (8 * 1)) & 255).to_bytes(1,"big") )
        data.append( ((quantity >> (8 * 2)) & 255).to_bytes(1,"big") )
        data.append( ((quantity >> (8 * 3)) & 255).to_bytes(1,"big") )

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SSB_ADD_XP, data)
        msg = self.device.response(seq)

        #print("addXP: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))
        res = int.from_bytes(msg.data[0], "big")

        return (ResponseCode_OK, res)

    def _levelUpAttribute(self, password, attrId):
        """This command attempts to increase the level of the specified attribute by spending attribute points. The
        IDs are 00h = Speed, 01h = Boost, 02h = Brightness and 03h = Shield. If successful the SSB is committed
        to flash. If there are not enough attribute points, this command returns an EEXEC error (code 08h).

        If the password is not accepted, this command fails without consequence.

        On success the response packet contains the attribute ID, the new level and the remaining attribute
        points."""

        data = []
        data.append( ((password >> (8 * 0)) & 255).to_bytes(1,"big") )
        data.append( ((password >> (8 * 1)) & 255).to_bytes(1,"big") )
        data.append( ((password >> (8 * 2)) & 255).to_bytes(1,"big") )
        data.append( ((password >> (8 * 3)) & 255).to_bytes(1,"big") )
        data.append(attrId.to_bytes(1,"big"))

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SSB_LEVEL_UP_ATTR, data)
        msg = self.device.response(seq)

        #print("levelUpAttribute: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))
        res['id'] = int.from_bytes(msg.data[0], "big")
        res['level'] = int.from_bytes(msg.data[1], "big")
        res['ptsRemaining'] = (int.from_bytes(msg.data[2], "big") << 8) | int.from_bytes(msg.data[3], "big")

        return (ResponseCode_OK, res)

    def _getPasswordSeed(self):
        """Protected Sphero commands require a password and this returns the seed to you.
        Refer to Appendix D for what to do next."""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_GET_PW_SEED)
        msg = self.device.response(seq)

        #print("getPasswordSeed: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))
        res = (int.from_bytes(msg.data[0], "big") << 24) | (int.from_bytes(msg.data[1], "big") << 16) | (int.from_bytes(msg.data[2], "big") << 8) | int.from_bytes(msg.data[3], "big")

        return (ResponseCode_OK, res)

    def _enableSSBAsyncMessages(self, enable):
        """Turn on/off soul block related asynchronous messages. This includes shield collision and regrowth
        messages, boost use and regrowth messages, XP growth and level-up messages. This feature defaults
        to off."""

        flag_enable = b'\x01' if enable else b'\x00'

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SSB_ENABLE_ASYNC, [flag_enable])
        msg = self.device.response(seq)

        #print("enableSSBAsyncMessages: ", msg.mrsp)
        return (msg.mrsp, None)

    # Macro commands
    def _runMacro(self, idOp):
        """This attempts to execute the specified macro. Macro IDs are organized into groups: 01 –31 are System
        Macros, that is, they are compiled into the Main Application. As such they are always available to be
        run and cannot be deleted. Macro IDs 32–253 are User Macros that are downloaded and persistently
        stored. They can be deletedin total. MacroID 255is a special user macro called the Temporary Macro
        as it is held in RAM for execution.Macro ID 254 is also a special user macro called the Stream Macro
        that doesn't require this call to begin execution.

        This command will fail if there is currentlyan executing macro or the specified ID Code isn't found.
        In the case of the former, send an abort command first."""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_RUN_MACRO, [idOp.to_bytes(1,"big")])
        msg = self.device.response(seq)

        #print("runMacro: ", msg.mrsp)
        return (msg.mrsp, None)

    def _saveTemporaryMacro(self, macroData):
        """This stores the attached macro definition intothe temporary RAM buffer for later execution. Any
        existing macro ID can be sent through this command and itisthen renamed toID FFh. If this command
        is sent while a Temporary or Stream Macro is executing it will be terminated so that its storage space
        can be overwritten.As with all macros, the longest definition that can be sent is 254 bytes (thus
        requiring DLEN to be FFh).

        You must follow this with a Run Macro command to begin execution."""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SAVE_TEMP_MACRO, [bytearray(macroData)])
        msg = self.device.response(seq)

        #print("saveTemporaryMacro: ", msg.mrsp)
        return (msg.mrsp, None)

    def _saveMacro(self, macroData):
        """This stores the attached macro definition into the persistent store forlater execution. This command
        can be sent even if other macrosare executing. You will receive a failure response if you attempt to
        send an ID number in the System Macro range, 255 for the Temp Macro and ID of an existing user macro
        in the storage block.As with all macros, the longest definition that can be sent is 254 bytes (thus
        requiring DLEN to be FFh).

        A special case of this command is to start and continue execution of the Stream Macro, ID 254. If a
        Temporary Macro is running it will be terminated and the Stream Macro will begin. If a Stream Macro is
        already running, this chunkwill be appended (if there is room). Stream Macros terminate via Abort or
        with a special END code.Refer to the Sphero Macro documentation for more detail."""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SAVE_MACRO, [bytearray(macroData)])
        msg = self.device.response(seq)

        #print("saveMacro: ", msg.mrsp)
        return (msg.mrsp, None)

    def _reinitMacroExecutive(self):
        """This terminates any running macro and reinitializes the macro system. The table of any persistent
        user macros is cleared."""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_REINIT_MACRO_EXECUTIVE)
        msg = self.device.response(seq)

        #print("reinitMacroExecutive: ", msg.mrsp)
        return (msg.mrsp, None)

    def _abortMacro(self):
        """This command aborts any executing macro and returns both its ID code and the command number
        currently in process. An exceptionis a System Macro that is executing with the UNKILLABLE flag set.
        A normal return code indicates the ID Code of the aborted macro as well as the command number at
        which execution was stopped. A return ID code of 00hindicates that no macro was running and an ID
        code with FFFFhas the CmdNum that the macro was unkillable."""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_ABORT_MACRO)
        msg = self.device.response(seq)

        #print("abortMacro: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))
        res = (int.from_bytes(msg.data[0], "big") << 8) | int.from_bytes(msg.data[1], "big")

        return (ResponseCode_OK, res)

    def _getMacroStatus(self):
        """This command returns the ID code and command number of the currently executing macro. If no macro
        is currently running,  00his returned for the ID code while the command number is left over from the
        last macro."""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_GET_MACRO_STATUS)
        msg = self.device.response(seq)

        #print("getMacroStatus: ", msg.mrsp)
        if (msg.mrsp != ResponseCode_OK):
            return (msg.mrsp, None)

        #print(len(msg.data))
        res['id'] = int.from_bytes(msg.data[0], "big")
        res['cmdNum'] = (int.from_bytes(msg.data[1], "big") << 8) | int.from_bytes(msg.data[2], "big")

        return (ResponseCode_OK, res)

    def _setMacroParameter(self, parameter, valueOne, valueTwo):
        """This command allows system globals that influence certain macro commands to be selectively altered
        from outside of the macro system itself. The values of Val1 and Val2 depend on the parameterindex.

            00h Assign System Delay 1: Val1 = MSB, Val2 = LSB
            01h Assign System Delay 2: Val1 = MSB, Val2 = LSB
            02h Assign System Speed 1: Val1 = speed, Val2 = 0 (ignored)
            03h Assign System Speed 2: Val1 = speed, Val2 = 0 (ignored)
            04h Assign System Loops: Val1 = loop count,Val2 = 0 (ignored)

        Details of what these system variables change are presented in the Sphero Macro document."""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SET_MACRO_PARAMETER, [parameter.to_bytes(1,"big"), valueOne.to_bytes(1,"big"), valueTwo.to_bytes(1,"big")])
        msg = self.device.response(seq)

        #print("setMacroParameter: ", msg.mrsp)
        return (msg.mrsp, None)

    def _appendMacroChunk(self, macroData):
        """This stores the attached macro definition into the temporary RAM buffer for later execution. It is similar
        to the Save Temporary Macro call but allows you to build up longer temporary macros.

        Any existing macro ID can be sent through this command and executed through the Run Macro call
        using ID FFh. If this command is sent while a Temporary or Stream Macro is executing it will be
        terminated so that its storage space can be overwritten. As with all macros, the longest chunkthat can
        be sent is 254 bytes (thus requiring DLEN to be FFh).

        You must follow this with a Run Macro command (ID FFh) to actually get it to go and it is best to prefix
        this command with an Abort call to make certain the larger buffer is completely initialized."""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_APPEND_MACRO_CHUNK, bytearray(macroData))
        msg = self.device.response(seq)

        #print("appendMacroChunk: ", msg.mrsp)
        return (msg.mrsp, None)

    # OrbBasic commands
    def _eraseOrbBasicStorage(self, area):
        """This erases any existing program in the specified storage area. Specify 00h for the temporary RAM buffer
        or 01h for the persistent storage area."""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_ERASE_ORBBASIC_STORAGE, [area.to_bytes(1,"big")])
        msg = self.device.response(seq)

        #print("eraseOrbBasicStorage: ", msg.mrsp)
        return (msg.mrsp, None)

    def _appendOrbBasicFragment(self, area, fragment):
        """Sending an orbBasic program to Sphero involves appending blocks of text toexisting ones in the
        specified storage area (00h for RAM, 01h for persistent). Complete lines are not required. A line
        begins with a decimal line number followed by a space and is terminated with a <LF>. See the orbBasic
        Interpreter document for complete information.

        Possible error responses would be ORBOTIX_RSP_CODE_EPARAM if an illegal storage area is specified or
        ORBOTIX_RSP_CODE_EEXEC  if the specified storage areais full"""

        data = bytearray()
        data.append(area.to_bytes(1,"big"))
        data += bytearray(fragment)

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_APPEND_ORBBASIC_FRAGMENT, data)
        msg = self.device.response(seq)

        #print("appendOrbBasicFragment: ", msg.mrsp)
        return (msg.mrsp, None)

    def _executeOrbBasicProgram(self, area, startLine):
        """This attempts to run a programin the specified storage area beginning at the specified line number. This
        command will fail if there is already an orbBasic program executing."""

        data = []
        data.append(area.to_bytes(1,"big"))
        data.append( ((startLine >> (8 * 0)) & 255).to_bytes(1,"big") )
        data.append( ((startLine >> (8 * 1)) & 255).to_bytes(1,"big") )

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_EXECUTE_ORBBASIC_PROGRAM, data)
        msg = self.device.response(seq)

        #print("executeOrbBasicProgram: ", msg.mrsp)
        return (msg.mrsp, None)

    def _abortOrbBasicProgram(self):
        """Aborts execution of any currently running orbBasic program."""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_ABORT_ORBBASIC_PROGRAM)
        msg = self.device.response(seq)

        #print("abortOrbBasicProgram: ", msg.mrsp)
        return (msg.mrsp, None)

    def _submitValueToInputStatement(self, value):
        """This takes the place of the typical user console in orbBasic and allows a user to answer an input request.
        If there is no pending input request when this API command is sent, the supplied value is ignored
        without error.Refer to the orbBasic language document for further information."""

        data = []
        data.append( ((value >> (8 * 0)) & 255).to_bytes(1,"big") )
        data.append( ((value >> (8 * 1)) & 255).to_bytes(1,"big") )
        data.append( ((value >> (8 * 2)) & 255).to_bytes(1,"big") )
        data.append( ((value >> (8 * 3)) & 255).to_bytes(1,"big") )

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_SUBMIT_VALUE_TO_INPUT_STATEMENT, data)
        msg = self.device.response(seq)

        #print("submitValueToInputStatement: ", msg.mrsp)
        return (msg.mrsp, None)

    def _commitRAMProgramToFlash(self):
        """This copies thecurrent orbBasic RAM program to persistent storage in Flash. It will fail if a program is
        currently executing out of Flash."""

        seq = self.device.sendCommand(DeviceId_SPHERO, SpheroCommandId_COMMIT_RAM_PROGRAM_TO_FLASH)
        msg = self.device.response(seq)

        #print("commitRAMProgramToFlash: ", msg.mrsp)
        return (msg.mrsp, None)

    #*******************************************************************************************************/
    #******************************        Async response commands         *********************************
    #*******************************************************************************************************/
    def asyncPowerNotification(self):
        """The power state byte mimics that of CID 20h above: 01h = Battery Charging, 02h = Battery OK,
        03h = Battery Low, 04h = Battery Critical"""

        msg = self.device.reciveAsync(AsyncResponseId_PowerNotification)

        print("asyncPowerNotification: ", msg)
        if (msg == None):
            return None

        print(len(msg.data))
        res = int.from_bytes(msg.data[0], "big")

        return res

    def _asyncLevel1DiagnosticResponse(self):
        """This is a developer-level command to help diagnose aberrant behavior. Most system counters, process
        flags, and system states are decoded into human readable ASCII.There are two responses to this
        command: a Simple Response followed by a large asyncmessage containing the results of the diagnostic
        tests. As of FW version 0.99, the answer was well over 1K in length and similar to:"""

        msg = self.device.reciveAsync(AsyncResponseId_Level1DiagnosticResponse)

        #print("asyncLevel1DiagnosticResponse: ", msg)
        if (msg == None):
            return None

        #print(len(msg.data))
        res = ""
        for i in range(0, len(msg.data)):
            res += int.from_bytes(msg.data[i], "big")

        return res

    def asyncSensorDataStreaming(self):
        """Each parameter is returned as a 16-bit signed integer. The table below defines the bits in MASK to those
         parameters with the indicated ranges and units. If the command is issued with a MASK of zero, then
         data streaming is disabled"""

        msg = self.device.reciveAsync(AsyncResponseId_SensorDataStreaming)

        print("asyncSensorDataStreaming: ", msg)
        if (msg == None):
            return None

        aux = self.stream
        res = {}
        print(len(msg.data))

        for i in range(0, 2, len(msg.data)):
            number = ((int.from_bytes(msg.data[i], "big") << 8) & 65535) + (int.from_bytes(msg.data[i+1], "big") & 65535)
            sig = int.from_bytes(msg.data[i], "big") >> 7

            if (aux.get('accelXRaw', None) != None):
                res['accelXRaw'] = -number if sig else number
                aux['accelXRaw'] = False

            elif (aux.get('accelYRaw', None) != None):
                res['accelYRaw'] = -number if sig else number
                aux['accelYRaw'] = False

            elif (aux.get('accelZRaw', None) != None):
                res['accelZRaw'] = -number if sig else number
                aux['accelZRaw'] = False

            elif (aux.get('gyroXRaw', None) != None):
                res['gyroXRaw'] = -number if sig else number
                aux['gyroXRaw'] = False

            elif (aux.get('gyroYRaw', None) != None):
                res['gyroYRaw'] = -number if sig else number
                aux['gyroYRaw'] = False

            elif (aux.get('gyroZRaw', None) != None):
                res['gyroZRaw'] = -number if sig else number
                aux['gyroZRaw'] = False

            elif (aux.get('rightEMFRaw', None) != None):
                res['rightEMFRaw'] = -number if sig else number
                aux['rightEMFRaw'] = False

            elif (aux.get('leftEMFRaw', None) != None):
                res['leftEMFRaw'] = -number if sig else number
                aux['leftEMFRaw'] = False

            elif (aux.get('leftPWMRaw', None) != None):
                res['leftPWMRaw'] = -number if sig else number
                aux['leftPWMRaw'] = False

            elif (aux.get('rightPWMRaw', None) != None):
                res['rightPWMRaw'] = -number if sig else number
                aux['rightPWMRaw'] = False

            elif (aux.get('pitchIMU', None) != None):
                res['pitchIMU'] = -number if sig else number
                aux['pitchIMU'] = False

            elif (aux.get('rollIMU', None) != None):
                res['rollIMU'] = -number if sig else number
                aux['rollIMU'] = False

            elif (aux.get('yawIMU', None) != None):
                res['yawIMU'] = -number if sig else number
                aux['yawIMU'] = False

            elif (aux.get('accelX', None) != None):
                res['accelX'] = -number if sig else number
                aux['accelX'] = False

            elif (aux.get('accelY', None) != None):
                res['accelY'] = -number if sig else number
                aux['accelY'] = False

            elif (aux.get('accelZ', None) != None):
                res['accelZ'] = -number if sig else number
                aux['accelZ'] = False

            elif (aux.get('gyroX', None) != None):
                res['gyroX'] = -number if sig else number
                aux['gyroX'] = False

            elif (aux.get('gyroY', None) != None):
                res['gyroY'] = -number if sig else number
                aux['gyroY'] = False

            elif (aux.get('gyroZ', None) != None):
                res['gyroZ'] = -number if sig else number
                aux['gyroZ'] = False

            elif (aux.get('rightEMF', None) != None):
                res['rightEMF'] = -number if sig else number
                aux['rightEMF'] = False

            elif (aux.get('leftEMF', None) != None):
                res['leftEMF'] = -number if sig else number
                aux['leftEMF'] = False

            elif (aux.get('q0', None) != None):
                res['q0'] = -number if sig else number
                aux['q0'] = False

            elif (aux.get('q1', None) != None):
                res['q1'] = -number if sig else number
                aux['q1'] = False

            elif (aux.get('q2', None) != None):
                res['q2'] = -number if sig else number
                aux['q2'] = False

            elif (aux.get('q3', None) != None):
                res['q3'] = -number if sig else number
                aux['q3'] = False

            elif (aux.get('odometerX', None) != None):
                res['odometerX'] = -number if sig else number
                aux['odometerX'] = False

            elif (aux.get('odometerY', None) != None):
                res['odometerY'] = -number if sig else number
                aux['odometerY'] = False

            elif (aux.get('accelOne', None) != None):
                res['accelOne'] = -number if sig else number
                aux['accelOne'] = False

            elif (aux.get('velocityX', None) != None):
                res['velocityX'] = -number if sig else number
                aux['velocityX'] = False

            elif (aux.get('velocityY', None) != None):
                res['velocityY'] = -number if sig else number
                aux['velocityY'] = False

        return res

    def _asyncConfigBlockContents(self):
        """This command retrieves one of the configuration blocks. The response is a simple one; an error code of
        08h is returned when the resources are currently unavailable to send the requested block back. The
        actual configuration block data returns in an asynchronous message of type 04h due to its length (if
        there is no error)."""

        msg = self.device.reciveAsync(AsyncResponseId_ConfigBlockContents)

        #print("asyncConfigBlockContents: ", msg)
        if (msg == None):
            return None

        #print(len(msg.data))
        res = msg.data

        return res

    def asyncPreSleepWarning10Sec(self):

        msg = self.device.reciveAsync(AsyncResponseId_PreSleepWarning10Sec)

        print("asyncPreSleepWarning10Sec: ", msg)

        if (msg == None):
            return None

        res = int.from_bytes(msg.data[0], "big")

        return res

    def _asyncMacroMarkers(self):

        msg = self.device.reciveAsync(AsyncResponseId_MacroMarkers)

        if (msg == None):
            return None

        #print("asyncMacroMarkers: ", msg)
        return msg.data

    def asyncCollisionDetected(self):
        """ """

        msg = self.device.reciveAsync(AsyncResponseId_CollisionDetected)

        print("asyncCollisionDetected: ", msg)
        if (msg == None):
            return None

        print(len(msg.data))
        res = {}
        res['x'] = (int.from_bytes(msg.data[0], "big") << 8) | int.from_bytes(msg.data[1], "big")
        res['y'] = (int.from_bytes(msg.data[2], "big") << 8) | int.from_bytes(msg.data[3], "big")
        res['z'] = (int.from_bytes(msg.data[4], "big") << 8) | int.from_bytes(msg.data[5], "big")

        res['axis'] = int.from_bytes(msg.data[6], "big")

        res['xMagnitude'] = (int.from_bytes(msg.data[7], "big") << 8) | int.from_bytes(msg.data[8], "big")
        res['yMagnitude'] = (int.from_bytes(msg.data[9], "big") << 8) | int.from_bytes(msg.data[10], "big")

        res['speed'] = int.from_bytes(msg.data[11], "big")

        res['timestamp'] = (int.from_bytes(msg.data[12], "big") << 24) | (int.from_bytes(msg.data[13], "big") << 16) | (int.from_bytes(msg.data[14], "big") << 8) | int.from_bytes(msg.data[15], "big")

        return res

    def _asyncOrbBasicPrintMessage(self):
        """The orbBasic PRINT ID 08h is akin to STDOUT"""

        msg = self.device.reciveAsync(AsyncResponseId_orbBasicPrintMessage)

        #print("asyncOrbBasicPrintMessage: ", msg)
        if (msg == None):
            return None

        #print(len(msg.data))
        res = "MESSAGE: "
        for i in range(0, len(msg.data)):
            res += str(msg.data[i], 'ascii')

        return res

    def _asyncOrbBasicErrorMessageASCII(self):
        """ 09h to STDER """

        msg = self.device.reciveAsync(AsyncResponseId_orbBasicErrorMessageASCII)

        #print("asyncOrbBasicErrorMessageASCII: ", msg)
        if (msg == None):
            return None

        #print(len(msg.data))
        res = "ERROR: "
        for i in range(0, len(msg.data)):
            res += str(msg.data[i], 'ascii')

        return res

    def _asyncOrbBasicErrorMessageBinary(self):
        """d 0Ah a machine readable version of STDERR"""

        msg = self.device.reciveAsync(AsyncResponseId_orbBasicErrorMessageBinary)

        #print("asyncOrbBasicErrorMessageBinary: ", msg)
        if (msg == None):
            return None

        #print(len(msg.data))
        res = "ERROR binary: "
        for i in range(0, len(msg.data)):
            res += msg.data[i]

        return res

    def _asyncSelfLevelResult(self):
        """The result byte can be: 00h = Unknown, 01h = Timed Out (level was not achieved), 02h = Sensors Error,
        03h = Self Level Disabled (see Option Flags), 04h = Aborted (by API call), 05h = Charger not found,
        06h = Success"""

        msg = self.device.reciveAsync(AsyncResponseId_SelfLevelResult)

        print("asyncSelfLevelResult: ", msg)
        if (msg == None):
            return None

        print(len(msg.data))
        res = int.from_bytes(msg.data[0], "big")

        return res

    def asyncGyroAxisLimitExceeded(self):
        """"The Gyro Axis Limit Exceeded message contains one byte of data where the bits
        signify the axes that exceeded the limit: bit 0 = X positive, bit 1 = X negative,
        bit 2 = Y+, bit 3 = Y-, bit 4 = Z+ and bit 5 = Z-. The message is emitted when one
        threshold is exceeded and all of the max measurements are cleared upon receipt of
        a Set Heading API command (DID 02h, CID 01h)"""

        msg = self.device.reciveAsync(AsyncResponseId_GyroAxisLimitExceeded)

        print("asyncGyroAxisLimitExceeded: ", msg)
        if (msg == None):
            return None

        print(len(msg.data))
        res = {}
        res['x'] = (int.from_bytes(msg.data[0], "big")) & 1
        res['xn'] = (int.from_bytes(msg.data[0], "big") >> 1) & 1

        res['y'] = (int.from_bytes(msg.data[0], "big") >> 2) & 1
        res['yn'] = (int.from_bytes(msg.data[0], "big") >> 3) & 1

        res['z'] = (int.from_bytes(msg.data[0], "big") >> 4) & 1
        res['zn'] = (int.from_bytes(msg.data[0], "big") >> 5) & 1

        return res

    def _asyncSpheroSoulData(self):
        """This command retrieves Sphero's Soul Block. The response is simple and then the actual block of
        soulular data returns in an asynchronous message of type 0Dh due to its 0x400 byte length (if there is no
        error)."""

        msg = self.device.reciveAsync(AsyncResponseId_SpheroSoulData)

        #print("asyncSpheroSoulData: ", msg)
        if (msg == None):
            return None

        #print(len(msg.data))
        res = msg.data

        return res

    def _asyncLevelUpNotification(self):
        """The level up notification contains two 16-bit unsigned integers. The first is the
        new robot level. The second is the total number of attribute points the user has
        to spend."""

        msg = self.device.reciveAsync(AsyncResponseId_LevelUpNotification)

        #print("asyncLevelUpNotification: ", msg)
        if (msg == None):
            return None

        #print(len(msg.data))
        res['level'] = (int.from_bytes(msg.data[0], "big") << 8) | int.from_bytes(msg.data[1], "big")
        res['attributes'] = (int.from_bytes(msg.data[2], "big") << 8) | int.from_bytes(msg.data[3], "big")

        return res

    def _asyncShieldDamageNotification(self):
        """The Shield damage notification contains one unsigned byte representing the portion of
        shield left (out of 255). The shields are damaged when Sphero collides with other objects.
        The shields are regenerate automatically over time. Both collisions and regeneration
        generate asynchronous updates."""

        msg = self.device.reciveAsync(AsyncResponseId_ShieldDamageNotification)

        #print("asyncShieldDamageNotification: ", msg)
        if (msg == None):
            return None

        #print(len(msg.data))
        res = int.from_bytes(msg.data[0], "big")

        return res

    def _asyncXPUpdateNotification(self):
        """The XP update notification contains one byte representing how much experience Sphero
        has gained toward the next robot level. The scale is from 0=0% to 255=100%."""

        msg = self.device.reciveAsync(AsyncResponseId_XPUpdateNotification)

        #print("asyncXPUpdateNotification: ", msg)
        if (msg == None):
            return None

        #print(len(msg.data))
        res = int.from_bytes(msg.data[0], "big")

        return res

    def _asyncBoostUpdateNotification(self):
        """The boost update notification contains one byte representing how much boost capability
        Sphero has. The value goes down when boost is used and automatically regenerates over time.
        Regeneration and use both generate asynchronous updates. The scale is from 0=0% to 255=100%"""

        msg = self.device.reciveAsync(AsyncResponseId_BoostUpdateNotification)

        #print("asyncBoostUpdateNotification: ", msg)
        if (msg == None):
            return None

        #print(len(msg.data))
        res = int.from_bytes(msg.data[0], "big")

        return res

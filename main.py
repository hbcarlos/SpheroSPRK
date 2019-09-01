#!/usr/bin/python3

from sphero import *
import keyboard
import time
import sys
import os
import re

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

def handlerAsync(resp):
    if resp.idcode == AsyncResponseId_PowerNotification:
        print(dev.asyncPowerNotification())
    if resp.idcode == AsyncResponseId_SensorDataStreaming:
        print(dev.asyncSensorDataStreaming())
    if resp.idcode == AsyncResponseId_PreSleepWarning10Sec:
        print(dev.asyncPreSleepWarning10Sec())
    if resp.idcode == AsyncResponseId_CollisionDetected:
        print(dev.asyncCollisionDetected())
    if resp.idcode == AsyncResponseId_GyroAxisLimitExceeded:
        print(dev.asyncGyroAxisLimitExceeded())
    input("Pulsa enter para continuar...")

def juego(dev):
    msg = """Controles:
    \t+ ESC: Salir.
    \t+ SPACE: Freno de mano.
    \t+ R/r: Girar 180�.
    \t+ W/w: Acelerar.
    \t+ S/s: Frenar.
    \t+ D/d: Girar a la derecha.
    \t+ A/a: Girar a la izquierda."""

    speed = 0
    heading = 0
    state = 0

    while keyboard.is_pressed('enter') != True:
        time.sleep(0.1)
        os.system("clear")
        print(msg)
        print("Speed: ", speed)
        print("Heading: ", heading)
        print("State: ", state)

        if keyboard.is_pressed('esc'):
            print("ESC")
            break
        elif keyboard.is_pressed('space'):
            print("SPACE")
            state = 0

        elif keyboard.is_pressed('r'):
            print("R")
            heading = 180
            state = 0

        elif keyboard.is_pressed('w'):
            print("W")
            speed = 255 if speed >= 255 else speed + 1
            state = 1

        elif keyboard.is_pressed('s'):
            print("S")
            speed = 0 if speed <= 0 else speed - 1
            state = 1

        elif keyboard.is_pressed('d'):
            print("D")
            heading = 0 if heading == 360 else heading + 10
            state = 1

        elif keyboard.is_pressed('a'):
            print("A")
            heading = 360 if heading == 0 else heading - 10
            state = 1

        dev.roll(speed, heading, state)

print("Bienvenido al controlador de Sphero!")
dev = SpheroSPRK("d3:57:0a:71:5f:d4", handlerAsync)
dev.connect()
if dev.ping()[0] != 0:
    exit(-1)

print("Conectado!")
print("Configurando Sphero...")

print(state[dev.setInactivityTimeout(600)[0]])
print(state[dev.setBackLEDOutput(0)[0]])
print(state[dev.setRGBLedOutput(0, 0, 0, True)[0]])
print(state[dev.configureLocator({'autoCalibrate':1,'x':0,'y':0,'yawTare':0})[0]])

op = {'sleepCharge':1,
    'vectorDrive':1,
    'selfLevelingCharger':1,
    'forceTailLED':0,
    'motionTimeOuts':1,
    'retailDemoMode':0,
    'awakeLight':1,
    'awakeHeavy':0,
    'gyroMaxAsync':0}
print(state[dev.setPermanentOptionFlags(op)[0]])
input("Pulsa enter para continuar...")

mss = """Usa SPACE para rodar el sphero hasta poner
la luz detras y pulsa esc para salir."""

dev.setBackLEDOutput(255)
grados = 0
while keyboard.is_pressed('esc') != True :
    time.sleep(0.1)
    os.system("clear")
    print(mss)
    if keyboard.is_pressed('space'):
        dev.roll(0, grados, 1)
        grados += 5
        grados = 0 if grados >= 360 else grados

dev.setBackLEDOutput(0)

mss = """Ahora a jugar
*************
Pulsa 'q' para salir.

Opciones:
\t+ T/t: Probar conexi�n (Ping).
\t+ L/l: Encender led.
\t+ H/h: Encender led trasero.
\t+ P/p: Leer posici�n.
\t+ N/n: Activar notificaciones de bateria.
\t+ C/c: Activar notificaciones de colisi�n.
\t+ D/d: Activar streaming de datos.
\t+ A/a: Comprobar notificaciones asincronas.
\t+ S/s: Sleep.
\t+ J/j: Modo juego.
"""

while keyboard.is_pressed('q') != True :
    time.sleep(0.1)
    os.system("clear")
    print(mss)

    if keyboard.is_pressed('t'):
        print(state[dev.ping()[0]])
        input("Pulsa enter para continuar...")

    elif keyboard.is_pressed('l'):
        print("Introduce el color del led principal (RGB 0-255)")
        red = int( re.sub("\D", "", input("RED: ")) )
        green = int( re.sub("\D", "", input("GREEN: ")) )
        blue = int( re.sub("\D", "", input("BLUE: ")) )
        dev.setRGBLedOutput(red, green, blue, True)
        input("Pulsa enter para continuar...")

    elif keyboard.is_pressed('h'):
        print("Introduce la intensidad del led trasero (0-255)")
        intensity = int( re.sub("\D", "", input("Intensidad: ")) )
        dev.setBackLEDOutput(intensity)
        input("Pulsa enter para continuar...")

    elif keyboard.is_pressed('p'):
        res = dev.readLocator()
        if res[0] != ResponseCode_OK:
            print("Error en la lectura")
            break;

        res = res[1]
        print("Posici�n")
        print("X: ", res['x'])
        print("Y: ", res['y'])
        print("Velocidad X: ", res['vx'])
        print("Velocidad Y: ", res['vy'])
        print("SOG: ", res['sog'])
        input("Pulsa enter para continuar...")

    elif keyboard.is_pressed('n'):
        print(state[dev.setPowerNotification(True)[0]])
        input("Pulsa enter para continuar...")

    elif keyboard.is_pressed('c'):
        op = {
        	# Detection method type to use. Supportedmethods are 01h, 02h, and 03h (see the collision
        	# detection document for details). Use 00h to completely disable this service.
        	'meth' : 1,
        	# An 8-bit settable threshold for the X (left/right) and Y (front/back) axes of Sphero.
        	# A value of 00h disables the contribution of that axis.
        	'xt' : 100,
        	'yt' : 100,
        	# An 8-bit settable speed value for the X and Y axes. This setting is ranged by the speed,
        	# then added to Xt, Yt to generate the final threshold value.
        	'xspd' : 100,
        	'yspd' : 100,
        	# An 8-bit post-collision dead time to prevent retriggering; specifiedin 10ms increments.
        	'dead' : 100 # 1segundo
        }

        print(state[dev.configureCollisionDetection(op)[0]])
        input("Pulsa enter para continuar...")

    elif keyboard.is_pressed('d'):
        op = {
        	'N' : 20,            # Divisor of the maximum sensor sampling rate
        	'M' : 1,             # Number of sample frames emitted per packet
        	'PCNT' : 4,          # Packet count 1-255 (or 0 for unlimited streaming)
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

        print(state[dev.setDataStreaming(op)[0]])
        input("Pulsa enter para continuar...")

    elif keyboard.is_pressed('a'):
        print(dev.asyncPowerNotification())
        print(dev.asyncSensorDataStreaming())
        print(dev.asyncPreSleepWarning10Sec())
        print(dev.asyncCollisionDetected())
        print(dev.asyncGyroAxisLimitExceeded())
        input("Pulsa enter para continuar...")

    elif keyboard.is_pressed('s'):
        dev.sleep(65535)
        input("Pulsa enter para continuar...")
        break

    elif keyboard.is_pressed('j'):
        juego(dev)
        input("Pulsa enter para continuar...")

dev.disconnect()
print("Disconected!!")

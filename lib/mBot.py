#!/usr/bin/env python3

import sys
import serial
import signal
import asyncio
import threading
import glob,struct
from time import sleep
from bleak import BleakClient, BleakScanner

class mSerial():
    # ser = None
    def __init__(self):
        sleep(0)

    def start(self, port):
        self.ser = serial.Serial(port,115200,timeout=0.5)
    
    def device(self):
        return self.ser

    def writePackage(self,package):
        self.ser.write(package)
        sleep(0.01)

    def read(self):
        return self.ser.read()

    def isOpen(self):
        return self.ser.isOpen()

    def inWaiting(self):
        return self.ser.inWaiting()

    def close(self):
        
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        sleep(0.2)
        self.ser.close()
        sleep(0.2)


found_advert = None
def find_mBot_ble_v1_c(bleDevice, advert):
    global found_advert
    # print("Filtering", bleDevice)
    if advert.local_name is None:
        return False

    if not advert.local_name.startswith("Makeblock_LE"):
        return False

    found_advert = advert
    return True

async def connectBle(devName):
    if devName is None:
        bleDev = await BleakScanner.find_device_by_filter(filterfunc=find_mBot_ble_v1_c)
    else:
        bleDev = await BleakScanner.find_device_by_name()
        if bleDev is None:
            print("mBot not found")
            return
    periperal = BleakClient(bleDev)
    await periperal.connect()
    if not periperal.is_connected:
        return None
    return periperal

class mBLE():
    useExistingService = False
    def __init__(self, bleName=None):
        self.bleName = bleName
        self.service = "0000ffe1-0000-1000-8000-00805f9b34fb"
        self.writeChar = "0000ffe3-0000-1000-8000-00805f9b34fb"
        self.readChar = "0000ffe2-0000-1000-8000-00805f9b34fb"
        self._bleak_thread = threading.Thread(target=self._run_bleak_loop)
        # Discard thread quietly on exit.
        self._bleak_thread.daemon = True
        self.buffer = []
        self._bleak_thread_ready = threading.Event()
        self._bleak_thread.start()
        # Wait for thread to start.
        self._bleak_thread_ready.wait()
    
    def _run_bleak_loop(self):
        self._bleak_loop = asyncio.new_event_loop()
        # Event loop is now available.
        self._bleak_thread_ready.set()
        self._bleak_loop.run_forever()

    def await_bleak(self, coro, timeout=None):
        """Call an async routine in the bleak thread from sync code, and await its result."""
        # This is a concurrent.Future.
        future = asyncio.run_coroutine_threadsafe(coro, self._bleak_loop)
        return future.result(timeout)

    def start(self):
        self.device = self.await_bleak(connectBle(self.bleName))
        # update bleName
        if self.device is None:
            print("Failed to connect")
            return None
        self.bleName = found_advert.local_name
        self.await_bleak(self.device.start_notify(self.readChar, self.handleRecv))

    def handleRecv(self, _, data):
        self.buffer = data

    def writePackage(self,package):
        self.await_bleak(self.device.write_gatt_char(self.writeChar, package, response=False))
        sleep(0.01)

    def read(self):
        c = self.buffer[0]
        self.buffer = self.buffer[1:]
        return chr(c)
        
    def isOpen(self):
        return self.device.is_connected
        
    def inWaiting(self):
        return len(self.buffer)
        
    def close(self):
        try:
            if self.device is None:
                print("Already disconnect")
                return None
            self.await_bleak(self.device.disconnect(), .5)
            self._bleak_loop.stop()
            self._bleak_thread.join(timeout=.5)
        except TimeoutError:
            exit()
        return
        # self._bleak_loop.close()


class mBot():
    def __init__(self):
        self.reponse_callback = {}
        self.buffer = []
        self.bufferIndex = 0
        self.isParseStart = False
        self.exiting = False
        self.isParseStartIndex = 0
        self.async_read = None
        
    def startWithSerial(self, port):
        self.device = mSerial()
        self.device.start(port)
        self.start()
    
    def startWithBle(self):
        self.device = mBLE()
        self.device.start()
        self.start()
    
    def excepthook(self, exctype, value, traceback):
        self.close()
        
    def start(self):
        sys.excepthook = self.excepthook
        self.async_read = threading.Thread(target=self.__onRead,args=(self.onParse,))
        self.async_read.start()
        
    def close(self):
        self.async_read.join(.5)
        self.device.close()
        
    def exit(self, signal, frame):
        self.exiting = True
        self.close()
        # sys.exit(0)
        
    def __onRead(self,callback):
        while 1:
            if self.exiting:
                break
            if self.device.isOpen():
                n = self.device.inWaiting()
                for i in range(n):
                    try:
                        r = ord(self.device.read())
                        callback(r)
                    except:
                        pass
                sleep(0.01)
            else:    
                sleep(0.5)
                
    def __writePackage(self,pack):
        self.device.writePackage(pack)

    def doRGBLed(self,port,slot,index,red,green,blue):
        self.__writePackage(bytearray([0xff,0x55,0x9,0x0,0x2,0x8,port,slot,index,red,green,blue]))

    def doRGBLedOnBoard(self,index,red,green,blue):
        self.doRGBLed(0x0,0x2,index,red,green,blue)

    def doMotor(self,port,speed):
        self.__writePackage(bytearray([0xff,0x55,0x6,0x0,0x2,0xa,port]+self.short2bytes(speed)))

    def doMove(self,leftSpeed,rightSpeed):
        self.__writePackage(bytearray([0xff,0x55,0x7,0x0,0x2,0x5]+self.short2bytes(-leftSpeed)+self.short2bytes(rightSpeed)))
        
    def doServo(self,port,slot,angle):
        self.__writePackage(bytearray([0xff,0x55,0x6,0x0,0x2,0xb,port,slot,angle]))
    
    def doBuzzer(self,buzzer,time=0):
        # ff 55 08 00 02 22 2d 06 01 fa 00
        self.__writePackage(bytearray([0xff,0x55,0x8,0x0,0x2,0x22,0x2d]+self.short2bytes(buzzer)+self.short2bytes(time)))

    def doSevSegDisplay(self,port,display):
        self.__writePackage(bytearray([0xff,0x55,0x8,0x0,0x2,0x9,port]+self.float2bytes(display)))
    
    # Send IR remote singal, not tested
    def doIROnBoard(self,message):
        self.__writePackage(bytearray([0xff,0x55,len(message)+3,0x0,0x2,0xd,message]))
        
    def requestLightOnBoard(self,extID,callback):
        self.requestLight(extID,8,callback)
    
    def requestLight(self,extID,port,callback):
        self.__doCallback(extID,callback)
        self.__writePackage(bytearray([0xff,0x55,0x4,extID,0x1,0x3,port]))

    def requestButtonOnBoard(self,extID,callback):
        self.__doCallback(extID,callback)
        self.__writePackage(bytearray([0xff,0x55,0x4,extID,0x1,0x1f,0x7]))
        
    def requestIROnBoard(self,extID,callback):
        self.__doCallback(extID,callback)
        self.__writePackage(bytearray([0xff,0x55,0x3,extID,0x1,0xd]))
    
    def requestTemperatureOnBoard(self, extID, callback):
        self.__doCallback(extID,callback)
        self.__writePackage(bytearray([0xff,0x55,0x4,extID,0x1,0x1b,0xd]))
        
    def requestSoundSenorOnBoard(self, extID, callback):
        self.__doCallback(extID,callback)
        self.__writePackage(bytearray([0xff,0x55,0x4,extID,0x1,0x7,0xe]))
    
    def requestGyroOnBoard(self, extID, axis, callback):
        self.__doCallback(extID,callback)
        self.__writePackage(bytearray([0xff,0x55,0x5,extID,0x1,0x6,0x1,axis]))
        
    def requestUltrasonicSensor(self,extID,port,callback):
        self.__doCallback(extID,callback)
        self.__writePackage(bytearray([0xff,0x55,0x4,extID,0x1,0x1,port]))
        
    def requestLineFollower(self,extID,port,callback):
        self.__doCallback(extID,callback)
        self.__writePackage(bytearray([0xff,0x55,0x4,extID,0x1,0x11,port]))
    
    def onParse(self, byte):
        position = 0
        value = 0    
        self.buffer+=[byte]
        bufferLength = len(self.buffer)
        if bufferLength >= 2:
            if (self.buffer[bufferLength-1]==0x55 and self.buffer[bufferLength-2]==0xff):
                self.isParseStart = True
                self.isParseStartIndex = bufferLength-2    
            if (self.buffer[bufferLength-1]==0xa and self.buffer[bufferLength-2]==0xd and self.isParseStart==True):            
                self.isParseStart = False
                position = self.isParseStartIndex+2
                extID = self.buffer[position]
                position+=1
                type = self.buffer[position]
                position+=1
                # 1 byte 2 float 3 short 4 len+string 5 double
                if type == 1:
                    value = self.buffer[position]
                if type == 2:
                    value = self.readFloat(position)
                    if(value<-255 or value>1023):
                        value = 0
                if type == 3:
                    value = self.readShort(position)
                if type == 4:
                    value = self.readString(position)
                if type == 5:
                    value = self.readDouble(position)
                if(type<=5):
                    self.responseValue(extID,value)
                self.buffer = []

    def readFloat(self, position):
        v = [self.buffer[position], self.buffer[position+1],self.buffer[position+2],self.buffer[position+3]]
        return struct.unpack('<f', struct.pack('4B', *v))[0]
    def readShort(self, position):
        v = [self.buffer[position], self.buffer[position+1]]
        return struct.unpack('<h', struct.pack('2B', *v))[0]
    def readString(self, position):
        l = self.buffer[position]
        position+=1
        s = ""
        for i in range(l):
            s += self.buffer[position+i].charAt(0)
        return s
    def readDouble(self, position):
        v = [self.buffer[position], self.buffer[position+1],self.buffer[position+2],self.buffer[position+3]]
        return struct.unpack('<f', struct.pack('4B', *v))[0]

    def responseValue(self, extID, value):
        self.reponse_callback["callback_"+str(extID)](value)
        
    def __doCallback(self, extID, callback):
        self.reponse_callback["callback_"+str(extID)] = callback

    def float2bytes(self,fval):
        val = struct.pack("f",fval)
        return [val[0],val[1],val[2],val[3]]

    def short2bytes(self,sval):
        val = struct.pack("h",sval)
        return [val[0], val[1]]

# Python Library for mBot
Table of contents
=================

  * [Description](#description)
  * [Software Dependencies](#software-dependencies)
  * [Installation](#installation)
  * [Usage](#usage)

Description
-----------
A Python interface to control and communicate with mBot robot kit from Makeblock

This has been tested with:

* the Raspberry PI.
* the Intel Edison.

Tested on Raspberry Pi with ubuntu 24 and Intel-Based macs.

Software Dependencies
---------------------

* Makeblock Library (https://github.com/Makeblock-official/Makeblock-Libraries)
* Python (http://python.org/download/)
* pyserial
* bleak

Prepare for Makeblock's mBot Ranger(Me Auriga)
----------------------------
1. Download the source from the git https://github.com/Makeblock-official/Makeblock-Libraries

2. copy the makeblock folder to your arduino default library. Your Arduino library folder should now look like this
(on Windows): [arduino installation directory]\libraries\makeblock\src
(on MACOS): [arduino Package Contents]\contents\Java\libraries\makeblock\src

3. Open the Arduino Application. (If it's already open, you will need to restart it to see changes.)

4. Click "File-> Examples". Here are firmwares for Makeblock's bots in "MakeBlockDrive->Firmware_for_Auriga".

5. Upload the Firmware to your bot.

6. To get the lastest firmware, install mBlock5, download mBot extension for mBlock5 and update the firmware. At the time of writing this the latest version is  : V09.01.017

Installation
-------

install python >= 3.8 ( http://python.org/downloads )

  ```
  [sudo] pip install "pyserial==3.5" "bleak==0.22.2"
  ```
Usage
-----------------
 ```
  git clone https://github.com/xeecos/python-for-mbot
 ```
 Enter the folder "python-for-mbot"
 
 Update the ble module name in the `mBLE` class 

 Edit lightsensor.py
 ```python
from lib.mBot import *

def onLight(value):
	 print("light = ",value)

if __name__ == '__main__':
	 bot = mBot()
	 bot.startWithSerial("COM15") or bot.startWithBle()
	 while(1):
	   bot.requestLightOnBoard(1,onLight)
	   sleep(0.5)
 ```
  
  ## using usb serial or bluetooth serial:
  
  change the serial port name "COMX or /dev/tty.XXX" for your mBot on system
  ```
  bot.startWithSerial("COM15")
  ```
  
  using wireless BLE:
  
  ```
  bot.startWithBle()
  ```
  
  running:
  
  ```
  [sudo] python lightsensor.py
  ```
  
### Learn more from Makeblock official website http://www.makeblock.com

Code References:
- Async to Sync: [Blinka](https://github.com/adafruit/Adafruit_Blinka_bleio/blob/a7d037244956a2d77e99250f76c11f9660d46386/_bleio/common.py#L136-L140)
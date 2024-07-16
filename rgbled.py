from lib.mBot import *

if __name__ == '__main__':
	bot = mBot()
	#bot.startWithSerial("/dev/tty.Repleo-CH341-000012FD")
	bot.startWithBle()
	ledIndex = 12 # will turn on the first led in the ring, use 0 to turn on all the leds
	red = 0
	blue = 0
	green = 0
	while(1):
		try:
			blue = 100
			bot.doRGBLedOnBoard(ledIndex,red,green,blue)
			sleep(0.5)
			blue = 0
			bot.doRGBLedOnBoard(ledIndex,red,green,blue)
			sleep(0.5)
		except KeyboardInterrupt:
			bot.doRGBLedOnBoard(ledIndex,0,0,0)
			bot.exit(0,0)
			break
		
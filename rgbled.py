from lib.mBot import *

if __name__ == '__main__':
	bot = mBot()
	#bot.startWithSerial("/dev/tty.Repleo-CH341-000012FD")
	bot.startWithBle()
	while(1):
		bot.doRGBLedOnBoard(1,100,0,0)
		sleep(0.5)
		bot.doRGBLedOnBoard(1,0,100,0)
		sleep(0.5)
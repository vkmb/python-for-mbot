from lib.mBot import *
bot = mBot()
#bot.startWithSerial("/dev/ttyUSB0")
bot.startWithBle()
while(1):
	try:
		bot.doMove(100,100)
		sleep(2)
		bot.doMove(-100,-100)
		sleep(2)
		bot.doMove(0,0)
		sleep(2)
	except KeyboardInterrupt:
		bot.doMove(0,0)
		bot.exit(0,0)
		break
	
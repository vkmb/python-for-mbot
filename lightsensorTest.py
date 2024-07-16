from lib.mBot import *

def onLight(value):
	print ("light = ",value)
	
if __name__ == '__main__':
	bot = mBot()
	#bot.startWithSerial("COM15")
	bot.startWithBle()
	while(1):
		try:
			bot.requestLightOnBoard(1,onLight)
			sleep(0.2)
		except KeyboardInterrupt:
			bot.exit(0,0)
			break
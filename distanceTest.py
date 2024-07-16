from lib.mBot import *
if __name__ == '__main__':
	callback_id = 1
	port_number = 10 # physical connection
	def onDistance(dist):
		print("distance:",dist)
		if dist<20 :
			bot.doMove(100,100)
			sleep(0.5)
			bot.doMove(-100,100)
			sleep(1)
		bot.doMove(-100,-100)
		
	bot = mBot()
	#bot.startWithSerial("/dev/ttyUSB0")
	bot.startWithBle()
	while(1):
		try:
			bot.requestUltrasonicSensor(callback_id,port_number,onDistance)
			sleep(0.2)
		except KeyboardInterrupt:
			bot.doMove(0,0)
			bot.exit(0,0)
			break
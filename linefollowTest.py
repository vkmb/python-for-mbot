from lib.mBot import *

def onLineFollower(value):
	print( "status = ",value)
	
if __name__ == '__main__':
	bot = mBot()
	#bot.startWithSerial("COM15")
	bot.startWithBle()
	while(1):
		try:
			port_number = 9
			callback_id = 1
			bot.requestLineFollower(callback_id,port_number,onLineFollower)
			sleep(0.2)
		except KeyboardInterrupt:
			bot.exit(0,0)
			break
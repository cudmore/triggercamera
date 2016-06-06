
import time
import serial

serialPort = '/dev/ttyACM0'

def run2():
	ser = serial.Serial(serialPort, baudrate=115200)
	ser.writeTimeout = 2
	ser.timeout = 1
	
	#ser.flush()
	ser.flushInput()
	ser.flushOutput()

	ser.write(b'trial')	
	
	time.sleep(0.5)

	serialIn = []
	while True:
		response = ser.readline()
		#print 'response=', response
		if response:
			serialIn.append(response)
		else:
			break
		
	ser.close()
	
	return serialIn
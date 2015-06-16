#!/usr/bin/env python

import serial
import time
import re
import sys

def doUsage():
	print ('apc.py: Read output current from AP7641 (maybe others?) via RS232.')
	print ('Will print current use on the commandline and return zero, or -1 on error.')
	print ('Uses 19200 baud - I could find no options to change this on the PDU, so it')
	print ('is hardcoded appropriately in apc.py.')
	print ('Supply -c to poll continuously, until killed.')
	print ('Caution: this code is pretty brittle, don\'t rely on it unless you don\'t mind fixing it!')
	print ('Usage: apc.py [serial port] <-c>')
	print ('eg. apc.py /dev/ttyS0')

# for python 3 must explicitly convert bytes to strings and vice-versa
# and must tell ser.write etc that we're sending bytes. Print is also a
# bit different

def getCurrentScreen(s):
	dataRead = ''
	# Read data until we hit a read timeout. Retry until we get
	# a non-empty string.
	while True:
		read = s.read().decode('UTF-8','ignore')
		dataRead += read
		if read == '' and dataRead != '':
			return dataRead

if len(sys.argv) < 2 or len(sys.argv) > 3:
	doUsage
	sys.exit(-1)
port = sys.argv[1]
contin = False
if (len(sys.argv) > 2):
	if (sys.argv[2] != '-c'):
		doUsage()
		sys.exit(-1)
	contin = True

print contin

ser = serial.Serial(port=port, baudrate=19200, timeout=0.1)

# We mash ESC a few times to get us back to the main menu. We need
# to do this since we don't know what state the PDU's menu will be
# in.
i = 0
while i < 5:
	i = i + 1
	ser.write(b'\033')
	time.sleep(0.1)

# Open the 'status' menu. It is number 1. 
ser.write(b'1\r\n')
time.sleep(0.1)

while True:
	# Grab the current display, split it into lines
	screen = getCurrentScreen(ser);
	lines = screen.split('\n\r')

	# The PDU will operate by first sending a dialog without any data in it, and then
	# populating it by periodically repositioning the cursor to the right places and
	# writing data. I don't fancy parsing all this by writing a terminal, so we just
	# look for the escape code that preceeds the current output value.
	for line in lines:
		m = re.match('.*\[K\\x1b\[6\;30H([0-9\.]+).*', line)
		if m != None:
			print ("%s\n", m.group(1) )

	if contin == False:
		break;

	time.sleep(5)


#!/usr/bin/python

import  smbus, cgi, cgitb, sys, os, serial, time

#Declare I2C chip addresses
POWER = 0x38
SELECTOR = 0X39

#Open serial port instance for LCD
ser=serial.Serial('/dev/ttyS1')
ser.timeout = 1
ser.baudrate = 115200

# Create instance of I2C bus
bus = smbus.SMBus(0)

# Create instance of FieldStorage
form = cgi.FieldStorage()

#Declare lcd buttons
lcd_button_set = {
	"Analog_1" : '\x01\x06\x0e\x00\x01\x08',
	"MuteOn"   : '\x01\x06\x08\x00\x01\x0e',
	"MuteOff"  : '\x01\x06\x08\x00\x00\x0f',
	"Standby"  : '\x01\x06\x03\x00\x01\x05',
	"PowerOn"  : '\x01\x06\x03\x00\x00\x04',
}

lcd_ack = '\x06'

#Set LCD button function		
def set_button(button):
	ser.write(lcd_button_set[button])
	time.sleep(0.1)
	if ser.read(1) == lcd_ack:
		print ("{0} button set".format(button))
	else:
		print ("{0} button set error".format(button))

#Get cgi-data
mute = form.getvalue('ampmute')

#Set mute
if mute == 'true'  :
	bus.write_byte_data(SELECTOR, 0x01, 0x01)
	set_button("MuteOn")
elif mute == 'ampmute' :
	bus.write_byte_data(SELECTOR, 0x01, 0x01)
	set_button("MuteOn")
elif mute == None :
	bus.write_byte_data(SELECTOR, 0x01, 0xC1)
	set_button("MuteOff")
elif mute == 'false' :
	bus.write_byte_data(SELECTOR, 0x01, 0xC1)
	set_button("MuteOff")





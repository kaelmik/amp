#!/usr/bin/python
################################################################################
# Author			: akael
# Creation date 	: 01.07.2013
# Project			: PB1007A Preamplifier Rev.1
# Langage			: Python
# Filename			: amp.py
# Target		 	: PB1001A AT91SAM9G20 Linux Kernel 2.6.38
# Description		: Preamplifier library and define
################################################################################

import ablib, serial, smbus, time, pca9554

#Define peripheral I2C address on PB1007A Board
POWER_IO = 0x38
SELECT_IO = 0x39
CS8416 = 0x10
WM8742 = 0x1A

#Define Selector map
UNMUTE_MASK = 0xC0
MUTE_MASK = 0x3F
SEL_MASK = 0x3F
SEL_ANALOG_1 = 0x01
SEL_ANALOG_2 = 0x09
SEL_SPDIF = 0x12
SEL_TOSLINK = 0x22
SEL_DLNA = 0x04

#Open serial port instance for LCD
ser=serial.Serial('/dev/ttyS1')
ser.timeout=1

#Open LCD Power pin instance
lcd_power=ablib.Pin('J7','35','low') #open an instance for lcd reset pin (Kernel ID 60)

#Open i2c_bus instance (/dev/i2c-0 on PB1007A) 
bus = smbus.SMBus(0)

#LCD Serial message
lcd_button_get = {
	"Analog_1" : '\x07\x06\x0e\x00\x01\x0e',
	"Analog_2" : '\x07\x06\x0f\x00\x01\x0f',
	"SPDIF"    : '\x07\x06\x11\x00\x01\x11',
	"TOSLINK"  : '\x07\x06\x10\x00\x01\x10',
	"DLNA"     : '\x07\x06\x0d\x00\x01\x0d',
	"Standby"  : '\x07\x06\x03\x00\x01\x03',
	"PowerOn"  : '\x07\x06\x03\x00\x00\x02',
}

#I2C write
def i2c_write(device, register, value):
	bus.write_byte_data(device, register, value)

#Select audio input  
def set_audio_input(input):
	if input == SEL_SPDIF:
		i2c_write(CS8416, 0x04, 0x80)
		i2c_write(CS8416, 0x05, 0x80)
	elif input == SEL_TOSLINK:
		i2c_write(CS8416, 0x04, 0x89)
		i2c_write(CS8416, 0x05, 0x80)
	else:
		i2c_write(CS8416, 0x04, 0x00)
		i2c_write(CS8416, 0x05, 0x00)
	bus.write_byte_data(SELECT_IO, pca9554.OUT_REG, (SEL_MASK & input))

#Mute HP Output
def mute_hp():
	old_val = bus.read_byte_data(SELECT_IO, pca9554.OUT_REG)
	bus.write_byte_data(SELECT_IO, pca9554.OUT_REG, (MUTE_MASK & old_val))
 
#Unmute HP Output
def unmute_hp():
	old_val = bus.read_byte_data(SELECT_IO, pca9554.OUT_REG)
	bus.write_byte_data(SELECT_IO, pca9554.OUT_REG, (UNMUTE_MASK | old_val))
  
#GPIO Init function
def gpio_init():
	"""Set GPIO with Analog 1 input selected"""
	mute_hp()
	i2c_write(SELECT_IO, pca9554.DIR_REG, 0x00)
	i2c_write(SELECT_IO, pca9554.POL_REG, 0x30)
	set_audio_input(SEL_ANALOG_1)
	i2c_write(POWER_IO, pca9554.DIR_REG, 0x00)
	i2c_write(POWER_IO, pca9554.OUT_REG, 0x10)
	i2c_write(POWER_IO, pca9554.OUT_REG, 0x13)
	unmute_hp()  

#LCD Startup init  
def lcd_init():
	"""Initialize LCD at system boot"""
	lcd_power.on() #Release lcd reset pin
	time.sleep(5) #Wait for screen to boot up
	ser.write('\x01\x06\x0e\x00\x01\x08')#set analog 1 input button
	time.sleep(2)
	s=ser.read(1) #read ACK from screen
	if s == '\x06' :
		print "ACK OK"
	else:
		print "ACK error"
	time.sleep(2)

#Read serial port for data from LCD
def serial_read():
	s = ser.read(6)
	if s ==  lcd_button_get['Analog_1']:
		print "Analog 1"
		set_audio_input(SEL_ANALOG_1)
	if s == lcd_button_get['Analog_2']:
		print "Analog 2"
		set_audio_input(SEL_ANALOG_2)
	if s == lcd_button_get['SPDIF']:
		print "SPDIF IN"
		set_audio_input(SEL_SPDIF)
	if s == lcd_button_get['TOSLINK']:
		print "Optical IN"
		set_audio_input(SEL_TOSLINK)
	if s == lcd_button_get['DLNA']:
		print "DLNA"
		set_audio_input(SEL_DLNA)
	if s ==  lcd_button_get['Standby']:
		print "Standby"
		mute_hp()
		i2c_write(POWER_IO, 0x01, 0x1C)
	if s ==  lcd_button_get['PowerOn']:
		print "Power ON"
		mute_hp()
		i2c_write(POWER_IO, 0x01, 0x10)
		time.sleep(0.5)
		i2c_write(POWER_IO, 0x01, 0x13)
		unmute_hp()

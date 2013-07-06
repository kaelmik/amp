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
MUTE_MASK = 0xC0
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

#PCA9554 Selector Instances
selector = pca9554.Pca9554(bus_id=0, address=SELECT_IO)
ana_en = pca9554.Pca9554(bus_id=0, address=SELECT_IO, line=0)
dig_en = pca9554.Pca9554(bus_id=0, address=SELECT_IO, line=1)
dlna_en = pca9554.Pca9554(bus_id=0, address=SELECT_IO, line=2)
rca_sel = pca9554.Pca9554(bus_id=0, address=SELECT_IO, line=3)
toslink_en = pca9554.Pca9554(bus_id=0, address=SELECT_IO, line=4)
spdif_en = pca9554.Pca9554(bus_id=0, address=SELECT_IO, line=5)
spk_l_en = pca9554.Pca9554(bus_id=0, address=SELECT_IO, line=6)
spk_r_en = pca9554.Pca9554(bus_id=0, address=SELECT_IO, line=7)

#PCA9554 Power Instances
power = pca9554.Pca9554(bus_id=0, address=POWER_IO)
amp_r = pca9554.Pca9554(bus_id=0, address=POWER_IO, line=0)
amp_l = pca9554.Pca9554(bus_id=0, address=POWER_IO, line=0)
p12va = pca9554.Pca9554(bus_id=0, address=POWER_IO, line=2)
m12va = pca9554.Pca9554(bus_id=0, address=POWER_IO, line=3)
dvdd = pca9554.Pca9554(bus_id=0, address=POWER_IO, line=4)

#LCD Serial message
lcd_button_get = {
	"Analog_1" : '\x07\x06\x0e\x00\x01\x0e',
	"Analog_2" : '\x07\x06\x0f\x00\x01\x0f',
	"SPDIF"    : '\x07\x06\x11\x00\x01\x11',
	"TOSLINK"  : '\x07\x06\x10\x00\x01\x10',
	"DLNA"     : '\x07\x06\x0d\x00\x01\x0d',
	"Standby"  : '\x07\x06\x03\x00\x01\x03',
	"PowerOn"  : '\x07\x06\x03\x00\x00\x02',
	"MuteOn"   : '\x07\x06\x08\x00\x01\x08',
	"MuteOff"  : '\x07\x06\x08\x00\x00\x09',
}

lcd_button_set = {
	"Analog_1" : '\x01\x06\x0e\x00\x01\x08',
	"MuteOn"   : '\x01\x06\x08\x00\x01\x0e',
	"MuteOff"  : '\x01\x06\x08\x00\x00\x0f',
}

lcd_form_set = {
	"Form0"    : '\x01\x0a\x00\x00\x00\x0b',
	"Form1"    : '\x01\x0a\x01\x00\x00\x0a',
	"Form2"    : '\x01\x0a\x02\x00\x00\x09',
	"Form3"    : '\x01\x0a\x03\x00\x00\x08',
	"Form4"    : '\x01\x0a\x04\x00\x00\x0f',
}

lcd_ack = '\x06'

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
	oldvalue = selector.readbyte()
	mute_state = oldvalue & MUTE_MASK
	selector.writebyte(input | mute_state)
	return

#Unmute HP Output
def mute_hp():
	spk_l_en.reset()
	spk_r_en.reset()
	return
	
#Mute HP Output
def unmute_hp():
	spk_l_en.set()
	spk_r_en.set()
	return
  
#GPIO Init function
def gpio_init():
	"""Set GPIO with Analog 1 input selected"""
	mute_hp()
	selector.set_dir_reg(0x00)
	set_audio_input(SEL_ANALOG_1)
	power.set_dir_reg(0x00)
	power.writebyte(0x10)
	power.writebyte(0x13)
	unmute_hp()

#LCD Startup init  
def lcd_init():
	"""Initialize LCD at system boot"""
	lcd_power.on() #Release lcd reset pin
	time.sleep(5) #Wait for screen to boot up
	ser.write(lcd_button_set["Analog_1"])#set analog 1 input button
	time.sleep(1)
	if ser.read(1) == lcd_ack: #read ACK from screen
		print "Analog 1 set"
	else:
		print "Analog 1 set error"
	time.sleep(1)
	
def set_form(form):
	ser.write(lcd_form_set[form])
	time.sleep(0.5)
	if ser.read(1) == lcd_ack:
		print ("{0} set".format(form))
	else:
		print ("{0} set error".format(form))

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
		power.writebyte(0x1C)
	if s ==  lcd_button_get['PowerOn']:
		print "Power ON"
		mute_hp()
		power.writebyte(0x10)
		time.sleep(0.5)
		power.writebyte(0x13)
		unmute_hp()
	if s ==  lcd_button_get['MuteOn']:
		print "Mute ON"
		mute_hp()
	if s ==  lcd_button_get['MuteOff']:
		print "Mute OFF"
		unmute_hp()
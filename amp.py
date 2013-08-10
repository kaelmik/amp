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

import ablib, serial, smbus, time, pca9554, datetime, config, spidev, urllib2
from operator import xor

#Define peripheral I2C address on PB1007A Board
POWER_IO  = 0x38
SELECT_IO = 0x39
CS8416    = 0x10
WM8742    = 0x1A

#Define Selector map
MUTE_MASK    = 0xC0
SEL_MASK     = 0x3F
SEL_ANALOG_1 = 0x01
SEL_ANALOG_2 = 0x09
SEL_SPDIF    = 0x12
SEL_TOSLINK  = 0x22
SEL_DLNA     = 0x04

#Open serial port instance for LCD
ser=serial.Serial('/dev/ttyS1')
ser.timeout = 1
ser.baudrate = 115200

#Open LCD Power pin instance
lcd_power=ablib.Pin('J7','35','low') #open an instance for lcd reset pin (Kernel ID 60)

#Open i2c_bus instance (/dev/i2c-0 on PB1007A) 
bus = smbus.SMBus(0)

#Open SPI bus instance for PGA2320
pga2320 = spidev.SpiDev()

#PCA9554 Selector Instances
selector   = pca9554.Pca9554(bus_id=0, address=SELECT_IO)
ana_en     = pca9554.Pca9554(bus_id=0, address=SELECT_IO, line=0)
dig_en     = pca9554.Pca9554(bus_id=0, address=SELECT_IO, line=1)
dlna_en    = pca9554.Pca9554(bus_id=0, address=SELECT_IO, line=2)
rca_sel    = pca9554.Pca9554(bus_id=0, address=SELECT_IO, line=3)
toslink_en = pca9554.Pca9554(bus_id=0, address=SELECT_IO, line=4)
spdif_en   = pca9554.Pca9554(bus_id=0, address=SELECT_IO, line=5)
spk_l_en   = pca9554.Pca9554(bus_id=0, address=SELECT_IO, line=6)
spk_r_en   = pca9554.Pca9554(bus_id=0, address=SELECT_IO, line=7)

#PCA9554 Power Instances
power = pca9554.Pca9554(bus_id=0, address=POWER_IO)
amp_r = pca9554.Pca9554(bus_id=0, address=POWER_IO, line=0)
amp_l = pca9554.Pca9554(bus_id=0, address=POWER_IO, line=1)
p12va = pca9554.Pca9554(bus_id=0, address=POWER_IO, line=2)
m12va = pca9554.Pca9554(bus_id=0, address=POWER_IO, line=3)
dvdd  = pca9554.Pca9554(bus_id=0, address=POWER_IO, line=4)

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
	"ScSaver"  : '\x07\x06\x06\x00\x00\x07',
	"VolSlider": '\x07\x04\x00',
}

lcd_button_set = {
	"Analog_1" : '\x01\x06\x0e\x00\x01\x08',
	"MuteOn"   : '\x01\x06\x08\x00\x01\x0e',
	"MuteOff"  : '\x01\x06\x08\x00\x00\x0f',
	"Standby"  : '\x01\x06\x03\x00\x01\x05',
	"PowerOn"  : '\x01\x06\x03\x00\x00\x04',
}

lcd_form_set = {
	"Form0"    : '\x01\x0a\x00\x00\x00\x0b',
	"Form1"    : '\x01\x0a\x01\x00\x00\x0a',
	"Form2"    : '\x01\x0a\x02\x00\x00\x09',
	"Form3"    : '\x01\x0a\x03\x00\x00\x08',
	"Form4"    : '\x01\x0a\x04\x00\x00\x0f',
	"Form5"    : '\x01\x0a\x05\x00\x00\x0e',
}

lcd_command = {
	"LedOn"		: '\x04\x01\x05',
	"LedOff"	: '\x04\x00\x04',
	"NetOn"     : '\x01\x0e\x00\x00\x01\x0e',
	"NetOff"    : '\x01\x0e\x00\x00\x00\x0f',
	"Vol_0"		: '\x01\x04\x00\x00\x00\x05',
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

#Mute HP Output
def mute_hp():
	spk_l_en.reset()
	spk_r_en.reset()
	return
	
#Unmute HP Output
def unmute_hp():
	spk_l_en.set()
	spk_r_en.set()
	return
	
#Check internet connexion function
def check_net():
    try:
        response=urllib2.urlopen('http://173.194.70.94',timeout=1)
        return True
    except urllib2.URLError as err: pass
    return False
	
def set_netled():
	if check_net() == True:
		set_command("NetOn")
	if check_net() == False:
		set_command("NetOff")
	
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
	time.sleep(0.5)
	if ser.read(1) == lcd_ack: #read ACK from screen
		print "Analog 1 set"
	else:
		print "Analog 1 set error"
	time.sleep(1)
	
#Update current time on LCD Screen
def set_time():
	now = datetime.datetime.now()
	time = now.strftime("%H:%M")
	if send_string(0x01,time) == 1:
		print ("set_time({0})".format(time))
	else:
		print "set_time() error"

#Set LCD form function	
def set_form(form):
	ser.write(lcd_form_set[form])
	time.sleep(0.1)
	if ser.read(1) == lcd_ack:
		print ("{0} set".format(form))
	else:
		print ("{0} set error".format(form))

#Set LCD command function	
def set_command(command):
	ser.write(lcd_command[command])
	time.sleep(0.1)
	if ser.read(1) == lcd_ack:
		print ("{0} set".format(command))
	else:
		print ("{0} set error".format(command))

#Set LCD button function		
def set_button(button):
	ser.write(lcd_button_set[button])
	time.sleep(0.1)
	if ser.read(1) == lcd_ack:
		print ("{0} button set".format(button))
	else:
		print ("{0} button set error".format(button))

#Send LCD string
def send_string(str_index, string_data):
	msg = [0x02]
	msg.append(str_index)
	size = len(string_data)
	msg.append(size)
	msg += map(ord, string_data)
	checksum = reduce(xor, msg)
	ser.write("\x02{0}{1}{2}{3}".format(chr(str_index),chr(size),string_data,chr(checksum)))
	if ser.read(1) == lcd_ack:
		return 1
	else:
		return 0

#Reset screen saver and auto-off counter		
def reset_counter():
	config.tick = 0
	config.auto_off = 0
	
#Set volume function
def set_volume(volume):
	gain = 31.5 - (0.5 * (255 - volume))
	dbgain = str(gain) + "dB"
	if send_string(0x02,dbgain) == 1:
		print ("Volume set to {0} dB".format(gain))
	else:
		print "set_volume() error"
	pga2320.open(1,0)
	old_vol = config.volume
	config.volume = volume
	if config.volume > old_vol :
		while old_vol < config.volume:
			old_vol += 1
			pga2320.writebytes([old_vol, old_vol])
			time.sleep(0.01)
	elif config.volume < old_vol :
		while old_vol > config.volume:
			old_vol -= 1
			pga2320.writebytes([old_vol, old_vol])
			time.sleep(0.01)
	elif config.volume == old_vol :
		pga2320.writebytes([old_vol, old_vol])
	pga2320.close()

#Read serial port for data from LCD
def serial_read():		
	s = ser.read(6)
	if s ==  lcd_button_get['Analog_1']:
		print "Analog 1"
		set_audio_input(SEL_ANALOG_1)
		reset_counter()
	if s == lcd_button_get['Analog_2']:
		print "Analog 2"
		set_audio_input(SEL_ANALOG_2)
		reset_counter()
	if s == lcd_button_get['SPDIF']:
		print "SPDIF IN"
		set_audio_input(SEL_SPDIF)
		reset_counter()
	if s == lcd_button_get['TOSLINK']:
		print "Optical IN"
		set_audio_input(SEL_TOSLINK)
		reset_counter()
	if s == lcd_button_get['DLNA']:
		print "DLNA"
		set_audio_input(SEL_DLNA)
		reset_counter()
	if s ==  lcd_button_get['Standby']:
		print "Standby"
		config.selector_cache = selector.readbyte()
		mute_hp()
		power.writebyte(0x1C)
		time.sleep(1)
		set_form("Form5")
		set_command("LedOff")
		config.power_state = 0
		reset_counter()
	if s ==  lcd_button_get['PowerOn']:
		print "Power ON"
		mute_hp()
		power.writebyte(0x10)
		time.sleep(0.1)
		power.writebyte(0x13)
		selector.writebyte(config.selector_cache)
		reset_counter()
	if s ==  lcd_button_get['MuteOn']:
		print "Mute ON"
		mute_hp()
		reset_counter()
	if s ==  lcd_button_get['MuteOff']:
		print "Mute OFF"
		unmute_hp()
		reset_counter()
	if s ==  lcd_button_get['ScSaver']:
		print "Screen saver OFF"
		reset_counter()
		set_command("LedOff")
		set_form("Form1")
		set_time()
		if config.power_state == 0:
			config.volume = 0
			config.power_state = 1
			set_command("Vol_0")
		set_netled()
		set_volume(config.volume)
		power.writebyte(0x13)
		unmute_hp()
		set_button("MuteOff")
		set_button("PowerOn")
		set_command("LedOn")
	if s[:3] == lcd_button_get['VolSlider']:
		reset_counter()
		value = s[4]
		volume = (ord(value))+40
		set_volume(volume)

		
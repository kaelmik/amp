#!/usr/bin/python
################################################################################
# Author			: akael
# Creation date 	: 01.07.2013
# Project			: PB1007A Preamplifier Rev.1
# Langage			: Python
# Filename			: main.py
# Target		 	: PB1001A AT91SAM9G20 Linux Kernel 2.6.38
# Description		: PB1007A firmware v1.0
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
################################################################################

import ablib, serial, smbus, time, config
from amp import *

#Init LCD
lcd_init()

#GPIO init
gpio_init()

#Set volume to mute
set_volume(0)
time.sleep(0.5)

#Set Form1
set_form("Form1")

#Set time
set_time()
t = 0 

#Power state
config.power_state = 1

#Set network status
set_netled()

#Process main loop
while(1):
	#Increment counter
	t = t + 1
	config.auto_off += 1
	config.tick += 1
	
	#Read serial port for input
	serial_read()
	time.sleep(0.05)
	
	#Set current time every ~15 seconds
	if t == 15 : 
		set_time()
	#	set_netled()
		t = 0
		
	#Check screen saver time
	if config.tick == config.SCREEN_SAVER_TIME:
		set_form("Form5")
		
	#Check auto power off time
	if config.auto_off == config.AUTO_OFF_TIME:
		print "Auto off time reached ... standby"
		config.power_state = 0
		set_command("LedOff")
		config.selector_cache = selector.readbyte()
		mute_hp()
		power.writebyte(0x1C)
		set_button("Standby")
		selector.writebyte(config.selector_cache)

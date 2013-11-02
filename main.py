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

import ablib, serial, smbus, time, config, os, sys
from amp import *
import tornado.ioloop
import tornado.web
import tornado.websocket
import threading
import ampserv

#sys_out = open(os.devnull, 'w')
#sys.stdout = sys_out

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
status("1")

#Set network status
set_netled()

#Define Tornado webserver API
application = tornado.web.Application([
	(r"/system",ampserv.system),
	(r"/home",ampserv.home),
	(r"/amp",ampserv.amp),
	(r"/mute",ampserv.mute),
	(r"/power",ampserv.power_set),
	(r"/input",ampserv.input),
	(r"/vol",ampserv.vol),
	(r"/refresh",ampserv.refresh),
	(r"/websocket",ampserv.WebSock),
	(r"/reboot",ampserv.reboot),
	(r"/api/network",ampserv.network),
	(r"/(.*)", tornado.web.StaticFileHandler, {"path": "./www/","default_filename": "index.html"}),
],debug=False)

#Function to start Tornado webserver
def start_tornado():
	application.listen(8080,"0.0.0.0")
	tornado.ioloop.IOLoop.instance().start()


#Launch Tornado in a new thread
thread = threading.Thread(target=start_tornado)
thread.start()

#Process main loop
while(1):
	#Increment counter
	t = t + 1
	config.auto_off += 1
	config.tick += 1
	
	#Read serial port for input
	serial_read()
	time.sleep(0.5)
	
	#Set current time every ~15 seconds
	if t == 15 : 
		set_time()
		t = 0
		
	#Check screen saver time
	if config.tick == config.SCREEN_SAVER_TIME:
		set_form("Form5")
		
	#Check auto power off time
	if config.auto_off == config.AUTO_OFF_TIME:
		print "Auto off time reached ... standby"
		config.power_state = 0
		status("0")
		set_command("LedOff")
		config.selector_cache = selector.readbyte()
		mute_hp()
		power.writebyte(0x1C)
		time.sleep(1)
		set_button("Standby")
		selector.writebyte(config.selector_cache)
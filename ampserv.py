#!/usr/bin/python
################################################################################
# Author			: akael
# Creation date 	: 01.07.2013
# Project			: PB1007A Preamplifier Rev.1
# Langage			: Python
# Filename			: ampserv.py
# Target		 	: PB1001A AT91SAM9G20 Linux Kernel 2.6.38
# Description		: Tornado Web Server implementation for PB1007A
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
################################################################################

import tornado.ioloop
import tornado.web
import tornado.websocket
import ablib, serial, smbus, time, datetime, spidev, urllib2, commands, os
from operator import xor

import sys
from amp import *

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
	save_input(input)
	return



#Send LCD string
def send_string(str_index, string_data):
	msg = [0x02]
	msg.append(str_index)
	size = len(string_data)
	msg.append(size)
	msg += map(ord, string_data)
	checksum = reduce(xor, msg)
	ser.write("\x02{0}{1}{2}{3}".format(chr(str_index),chr(size),string_data,chr(checksum)))
	ser.read(1)


#Set LCD form function	
def set_form(form):
	ser.write(lcd_form_set[form])
	time.sleep(0.1)
	ser.read(1)

#Set LCD command function	
def set_command(command):
	ser.write(lcd_command[command])
	time.sleep(0.1)
	ser.read(1)

#Write input to file
def save_input(input):
	f = open('/root/ampsoft/input', 'w')
	f.write(str(input))
	f.close()

#Write power status to file
def status(stat):
	f = open('/root/ampsoft/stat', 'w')
	f.write(stat)
	f.close()

#Set Volume Slider
def set_vol_slider(slider_data):
	msg = [0x01]
	msg.append(0x04)
	msg.append(slider_data)
	checksum = reduce(xor, msg)
	ser.write("\x01\x04\x00\x00{0}{1}".format(chr(slider_data),chr(checksum)))

class system(tornado.web.RequestHandler):
    def get(self):
	hostname = commands.getoutput("hostname -s")
	uname = commands.getoutput("uname -srm")
	audio_hw = commands.getoutput("cat /proc/asound/card0/pcm0p/info | grep id")
	hw_params = commands.getoutput("cat /proc/asound/card0/pcm0p/sub0/hw_params")
	uptime = commands.getoutput("uptime")
	lsusb = commands.getoutput("lsusb")
	df_h = commands.getoutput("df -h")
	free_m = commands.getoutput("free -m")
	ifconfig = commands.getoutput("ifconfig")
	iwconfig = commands.getoutput("iwconfig")
	w = commands.getoutput("w")
	date = commands.getoutput("date")
	self.render("www/system.html", title="System", 
			hostname=hostname,
			uname = uname,
			audio_hw = audio_hw,
			hw_params = hw_params,
			uptime = uptime,
			lsusb = lsusb,
			df_h = df_h,
			free_m = free_m,
			ifconfig = ifconfig,
			iwconfig = iwconfig,
			w = w,
			date = date,
		)

class amp(tornado.web.RequestHandler):
    def get(self):
	audio_hw = commands.getoutput("cat /proc/asound/card0/pcm0p/info | grep id")
	power,ana1,ana2,spdif,tos,dlna = "","","","","",""
	f = open('/root/ampsoft/input', 'r')
	input=int(f.read())
	f.close()
	if input == 0x01 :
		ana1 = "selected"
	elif input == 0x09 : 
		ana2 = "selected"
	elif input == 0x12 : 
		spdif = "selected"
	elif input == 0x22 : 
		tos = "selected"
	elif input == 0x04 : 
		dlna = "selected"
	f = open('/root/ampsoft/stat', 'r')
	a=f.read()
	f.close()
	if a == "0":
		power = "unchecked"
	if a == "1":
		power = "checked"
	f = open('/root/ampsoft/mute', 'r')
	mute=f.read()
	f.close()
	if mute == "0":
		mute = "unchecked"
	if mute == "1":
		mute = "checked"
	f = open('/root/ampsoft/vol', 'r')
	volume=(int(f.read()))
	f.close()
	self.render("www/amp.html", title="Amplifier Settings", 
			power = power,
			mute = mute,
			volume = volume,
			audio_hw = audio_hw,
			ana1=ana1,ana2=ana2,spdif=spdif,tos=tos,dlna=dlna,
		)



class refresh(tornado.web.RequestHandler):
    def get(self):
	audio_hw = commands.getoutput("cat /proc/asound/card0/pcm0p/info | grep id")
	power,ana1,ana2,spdif,tos,dlna = "","","","","",""
	f = open('/root/ampsoft/input', 'r')
	input=int(f.read())
	f.close()
	if input == 0x01 :
		ana1 = "selected"
	elif input == 0x09 : 
		ana2 = "selected"
	elif input == 0x12 : 
		spdif = "selected"
	elif input == 0x22 : 
		tos = "selected"
	elif input == 0x04 : 
		dlna = "selected"
	f = open('/root/ampsoft/stat', 'r')
	a=f.read()
	f.close()
	if a == "0":
		power = "unchecked"
	if a == "1":
		power = "checked"
	f = open('/root/ampsoft/mute', 'r')
	mute=f.read()
	f.close()
	if mute == "0":
		mute = "unchecked"
	if mute == "1":
		mute = "checked"
	f = open('/root/ampsoft/vol', 'r')
	volume=(int(f.read()))
	f.close()
	self.render("www/amp_part.html", title="Amplifier Settings", 
			power = power,
			mute = mute,
			volume = volume,
			audio_hw = audio_hw,
			ana1=ana1,ana2=ana2,spdif=spdif,tos=tos,dlna=dlna,
		)

class mute(tornado.web.RequestHandler):
	def post(self):
		if self.get_argument("ampmute")=="0":
			unmute_hp()
			set_button("MuteOff")
		if self.get_argument("ampmute")=="1":
			mute_hp()
			set_button("MuteOn")

class power_set(tornado.web.RequestHandler):
	def post(self):
		if self.get_argument("power")=="0":
			mute_hp()
			power.writebyte(0x1C)
			time.sleep(1)
			set_command("LedOff")
			time.sleep(0.1)
			set_form("Form5")
			status("0")
			pga2320.open(1,0)
			pga2320.writebytes([0, 0])
			pga2320.close()
			f = open('/root/ampsoft/vol', 'w')
			f.write("0")
			f.close()
		if self.get_argument("power")=="1":
			power.writebyte(0x13)
			set_form("Form1")
			pga2320.open(1,0)
			pga2320.writebytes([0, 0])
			pga2320.close()
			f = open('/root/ampsoft/vol', 'w')
			f.write("0")
			f.close()
			set_vol_slider(0)
			send_string(0x02,"-96.0dB")
			time.sleep(0.1)
			unmute_hp()
			set_button("MuteOff")
			time.sleep(0.1)
			set_button("PowerOn")
			time.sleep(0.1)
			set_command("LedOn")
			status("1")

class vol(tornado.web.RequestHandler):
	def post(self):
		volume = (self.get_argument("volum"))
		volum = (int(volume))+40
		gain = 31.5 - (0.5 * (255 - volum))
		dbgain = str(gain) + "dB"
		send_string(0x02,dbgain)
		f = open('/root/ampsoft/vol', 'w')
		f.write(self.get_argument("volum"))
		f.close()
		set_vol_slider(volum-40)
		pga2320.open(1,0)
		pga2320.writebytes([volum, volum])
		pga2320.close()

class input(tornado.web.RequestHandler):
	def post(self):
		print(self.get_argument("inputs"))
		if self.get_argument("inputs")== "SEL_ANALOG_1" :
			set_audio_input(SEL_ANALOG_1)
			set_button("Analog_1")
		elif self.get_argument("inputs")== "SEL_ANALOG_2" :
			set_audio_input(SEL_ANALOG_2)
			set_button("Analog_2")
		elif self.get_argument("inputs")== "SEL_SPDIF" :
			set_audio_input(SEL_SPDIF)
			set_button("SPDIF")
		elif self.get_argument("inputs")== "SEL_TOSLINK" :
			set_audio_input(SEL_TOSLINK)
			set_button("TOSLINK")
		elif self.get_argument("inputs")== "SEL_DLNA" :
			set_audio_input(SEL_DLNA)
			set_button("DLNA")

class WebSock(tornado.websocket.WebSocketHandler):
	def open(self):
		print "WebSocket opened"
		if self not in wss:
			wss.append(self)
	def on_message(self, message):
		print("You said message:".format(message))

	def on_close(self):
		print "WebSocket closed"
		if self in wss:
			wss.remove(self)
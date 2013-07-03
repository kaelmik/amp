#!/usr/bin/python
"""-----------------------------------------------------------------------------
Author			: akael
Creation date 	: 01.07.2013
Project			: PB1007A Preamplifier Rev.1
Langage			: Python
Filename		: main.py
Target		 	: PB1001A AT91SAM9G20 Linux Kernel 2.6.38
Description		: PB1007A firmware v1.0

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
-----------------------------------------------------------------------------"""

import ablib, serial, smbus, time
from amp import *

#GPIO init
gpio_init()

#Init LCD
lcd_init()

#Fonctions Serial
while(1):
 s=ser.read(6)
 if s ==  '\x07\x06\x0e\x00\x01\x0e':
   print "Analog 1"
   i2c_write(SELECT_IO, 0x01, 0x01)
 if s == '\x07\x06\x0f\x00\x01\x0f':
   print "Analog 2"
   i2c_write(SELECT_IO, 0x01, 0x39)
 if s == '\x07\x06\x11\x00\x01\x11':
   print "SPDIF IN"
   i2c_write(CS8416, 0x04, 0x80)
   i2c_write(CS8416, 0x05, 0x80)
   i2c_write(SELECT_IO, 0x01, 0x02)
 if s == '\x07\x06\x10\x00\x01\x10':
   print "Optical IN"
   i2c_write(CS8416, 0x04, 0x89)
   i2c_write(CS8416, 0x05, 0x80)
   i2c_write(SELECT_IO, 0x01, 0x02)
 if s == '\x07\x06\x0d\x00\x01\x0d':
   print "DLNA"
   i2c_write(SELECT_IO, 0x01, 0x04)
 if s ==  '\x07\x06\x03\x00\x01\x03':
   print "Standby"
   i2c_write(POWER_IO, 0x01, 0x1C)
 if s ==  '\x07\x06\x03\x00\x00\x02':
   print "Power ON"
   i2c_write(POWER_IO, 0x01, 0x10)
   time.sleep(0.5)
   i2c_write(POWER_IO, 0x01, 0x13)
 time.sleep(0.5)

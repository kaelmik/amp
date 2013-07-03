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

#Define which i2c_bus device driver to use
#(normally /dev/i2c-0) 
bus = smbus.SMBus(0)

#Define serial port
ser=serial.Serial('/dev/ttyS1')
ser.timeout=1


#Define I2C address 
POWER_IO = 0x38
SELECT_IO = 0x39
CS8416 = 0x10
WM8742 = 0x1A

#Init LCD
lcd_reset=ablib.Pin('J7','35','low')
lcd_reset.on()

#Fonctions I2C
def i2c_write(device, register, value):
  bus.write_byte_data(device,register,value)



#Inputs init
i2c_write(SELECT_IO, 0x03, 0x00)
i2c_write(SELECT_IO, 0x01, 0x01)
i2c_write(POWER_IO, 0x03, 0x00)
i2c_write(POWER_IO, 0x01, 0x10)
i2c_write(POWER_IO, 0x01, 0x13)

#wait for screen to boot up
time.sleep(5)
#set analog 1 input button
ser.write('\x01\x06\x0e\x00\x01\x08')
time.sleep(2)
s=ser.read(1) #read ACK
if s == '\x06' :
  print "ACK OK"
time.sleep(2)


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
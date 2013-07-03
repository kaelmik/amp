#!/usr/bin/python
"""-----------------------------------------------------------------------------
Author			: akael
Creation date 	: 01.07.2013
Project			: PB1007A Preamplifier Rev.1
Langage			: Python
Filename		: amp.py
Target		 	: PB1001A AT91SAM9G20 Linux Kernel 2.6.38
Description		: Preamplifier library and define
-----------------------------------------------------------------------------"""
import ablib, serial, smbus, time, pca9554

#Define peripheral I2C address on PB1007A Board
POWER_IO = 0x38
SELECT_IO = 0x39
CS8416 = 0x10
WM8742 = 0x1A

#Define serial port for LCD
ser=serial.Serial('/dev/ttyS1')
ser.timeout=1

#Define which i2c_bus to use (/dev/i2c-0 on PB1007A) 
bus = smbus.SMBus(0)

#Fonctions I2C
def i2c_write(device, register, value):
  bus.write_byte_data(device,register,value)
  
#GPIO Init function
def gpio_init():
  """Set GPIO with Analog 1 input selected"""
  i2c_write(SELECT_IO, pca9554.DIR_REG, 0x00)
  i2c_write(SELECT_IO, pca9554.OUT_REG, 0x01)
  i2c_write(POWER_IO, pca9554.DIR_REG, 0x00)
  i2c_write(POWER_IO, pca9554.OUT_REG, 0x10)
  i2c_write(POWER_IO, pca9554.OUT_REG, 0x13) 

#LCD Startup init  
def lcd_init():
  """Initialize LCD at system boot"""
  lcd_power=ablib.Pin('J7','35','low') #open an instance for lcd reset pin (Kernel ID 60)
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
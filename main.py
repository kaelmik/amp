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

import ablib, serial, smbus, time
from amp import *

#Init LCD
lcd_init()

#GPIO init
gpio_init()

#Set Form1
set_form("Form1")

#Fonctions Serial
while(1):
  serial_read()
  time.sleep(0.2)

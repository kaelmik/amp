#!/usr/bin/python
################################################################################
# Author			: akael
# Creation date 	: 01.07.2013
# Project			: PB1007A Preamplifier Rev.1
# Langage			: Python
# Filename			: config.py
# Target		 	: PB1001A AT91SAM9G20 Linux Kernel 2.6.38
# Description		: Global inter module variables + config variable
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
################################################################################


#Sreen saver and auto power off time
SCREEN_SAVER_TIME = 600
AUTO_OFF_TIME = 5400

#File to save variable
mute  = '/root/ampsoft/var/mute'
vol   = '/root/ampsoft/var/vol'
input = '/root/ampsoft/var/input'
power = '/root/ampsoft/var/stat'

#Screen saver counter
tick = 0

#Auto off counter
auto_off = 0

#Selector cache
selector_cache = 0

#Volume
volume = 0

#Power state
power_state = 0
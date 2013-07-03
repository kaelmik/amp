#!/usr/bin/python
"""-----------------------------------------------------------------------------
Author			: akael
Creation date 	: 01.07.2013
Project			: PB1007A Preamplifier Rev.1
Langage			: Python
Filename		: pca9554.py
Target		 	: PB1001A AT91SAM9G20 Linux Kernel 2.6.38
Description		: PCA9554A GPIO Expander
-----------------------------------------------------------------------------"""

#Define register
IN_REG = 0x00 #Input register
OUT_REG = 0x01 #Output register
POL_REG = 0x02 #Polarity inversion register (1=data inverted)
DIR_REG = 0x03 #Config register (0=output, 1=input)

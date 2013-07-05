#!/usr/bin/python
################################################################################
# Author			: akael
# Creation date 	: 01.07.2013
# Project			: PB1007A Preamplifier Rev.1
# Langage			: Python
# Filename			: pca9554.py
# Target		 	: PB1001A AT91SAM9G20 Linux Kernel 2.6.38
# Description		: PCA9554A GPIO Expander
################################################################################

import smbus

class Pca9554():

	"""
	Pca9554 (8 bit I2C expander)
	"""

	#Define register
	__IN_REG = 0x00 #Input register
	__OUT_REG = 0x01 #Output register
	__POL_REG = 0x02 #Polarity inversion register (1=data inverted)
	__DIR_REG = 0x03 #Config register (0=output, 1=input)
	
	IN = 1
	OUT = 0

	i2c_bus=-1
	i2c_address=-1
	line=-1

	def __init__(self, bus_id=0,address=0x39,line=0, direction="Null"):
		self.i2c_bus = smbus.SMBus(bus_id)
		self.i2c_address=address
		self.line=line
		if direction == IN:
			self.setinput()
		if direction == OUT:
			self.setoutput()
		return

	def set_dir_reg(self, value):
		"""set direction register : 0=output, 1=input"""
		self.i2c_bus.write_byte_data(self.i2c_address, __DIR_REG, value)
		return
	
	def setinput(self):
		"""set bit as input"""
		currentvalue = self.i2c_bus.read_byte_data(self.i2c_address, __DIR_REG, value)
		self.i2c_bus.write_byte_data(self.i2c_address, __DIR_REG, currentvalue | 1<<self.line)
		
	def setoutput(self):
		"""set bit as output"""
		currentvalue = self.i2c_bus.read_byte_data(self.i2c_address, __DIR_REG, value)
		self.i2c_bus.write_byte_data(self.i2c_address, __DIR_REG, currentvalue & (255-(1<<self.line)))	
		
	def writebyte(self,value):
		"""write output byte value"""
		self.i2c_bus.write_byte_data(self.i2c_address, __OUT_REG, value)	
		return

	def readbyte(self):
		"""read input byte value"""
		return self.i2c_bus.read_byte_data(self.i2c_address, __IN_REG)

	def set(self):
		"""set output bit at 1"""
		currentvalue = self.i2c_bus.read_byte_data(self.i2c_address, __OUT_REG)
		self.i2c_bus.write_byte_data(self.i2c_address, __OUT_REG, currentvalue | 1<<self.line)	
		return

	def reset(self):
		"""reset output bit at 0"""
		currentvalue = self.i2c_bus.read_byte_data(self.i2c_address, __OUT_REG)
		self.i2c_bus.write_byte_data(self.i2c_address, __OUT_REG, currentvalue & (255-(1<<self.line)))	
		return

	def get(self):
		"""read input bit value"""
		linevalue = self.i2c_bus.read_byte_data(self.i2c_address, __IN_REG)
		ret=linevalue >> self.line
		return ret &= 1
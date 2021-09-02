#! /usr/bin/python
from __future__ import print_function
import evora


class Parser(object):
	def __init__(self):
		self.e = evora.evora()

	def parse(self, input = None):
			print(input)
			input = input.split()
			if input[0] == 'connect':
				return self.e.startup()
			if input[0] == 'temp':
				return self.e.getTemp()
			if input[0] == 'setTEC':
				return self.e.setTEC(input[1])
			if input[0] == 'getTEC':
				return self.e.getTEC()
			if input[0] == 'warmup':
				return self.e.warmup()
			if input[0] == 'shutdown':
				return self.e.shutdown()
			if input[0] == 'expose':
				# expose flat 1 10 2
				type = input[1]
				expnum = int(input[2])
				itime = int(input[3])
				bin = int(input[4])
				return self.e.expose(expnum, itime, bin)

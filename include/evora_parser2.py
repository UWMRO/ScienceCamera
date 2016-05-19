#!/usr/bin/python

#import evora

class Parser(object):
	def __init__(self):
		pass
		#self.e = evora.evora()

	def parse(self, input = None):
			print input
			input = input.split()
			
			if input[0] == 'connect':
				return "Connecting to Evora"
				#return self.e.connect()
			if input[0] == 'temp':
				return "Getting temperature"
				#return self.e.getTemp()
			if input[0] == 'setTEC':
				return "Setting TEC"
				#return self.e.setTEC(input[1])
			if input[0] == 'getTEC':
				return "Getting TEC"
				#return self.e.getTEC()
			if input[0] == 'warmup':
				return "Warming Up"
				#return self.e.warmup()
			if input[0] == 'shutdown':
				return "Shutting Down"
				#return self.e.shutdown()
			if input[0] == 'expose':
				# expose flat 1 10 2
				type = input[1]
				expnum = int(input[2])
				itime = int(input[3])
				bin = int(input[4])
				return "type: %s, expnum: %s sec, itime: %s, binning: %s"%(input[1], input[2], input[3], input[4])
				#return self.e.expose(expnum, itime, bin)
			




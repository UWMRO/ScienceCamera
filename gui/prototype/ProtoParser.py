

class ProtoParser():
	def __init__(self):
		print "Entered the parser"

	def parse(self, command = None):
		#print command
		command = command.split() # split the evora command by white space.
		if command[0] == "expose":
			return "Exposing for " + command[1] + "seconds"

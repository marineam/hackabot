#!/usr/bin/python
#
# The Python rewrite of the ever famous Hackabot 
#
# This code is under the GPL 2.0 and all that good jazz.

"""Hackabot baby!

This is the Python rewrite of Hackabot, aka manatee. This is the result of
several rewrites of the original Perl version trying to either use multiple
processes or threads. In short, Perl frickin sucks at sharing data between
threads. Hopefully python will prove itself to be much better.
"""

import string
import time
from ircbot import SingleServerIRCBot
from irclib import nm_to_n 
from amara import binderytools

class Hackabot(SingleServerIRCBot):
	def __init__(self, file):
		# TODO: Semivalidate 'file' before actually using it.
		self.config = binderytools.bind_file(file).hackabot
		self.msg("Setting up irc object for "+str(self.config.server)+"...")
		SingleServerIRCBot.__init__(self, [(self.config.server.xml_text_content(), int(self.config.port.xml_text_content()))], self.config.nick.xml_text_content(), self.config.name.xml_text_content())

	def on_nicknameinuse(self, irc, event):
		irc.nick(irc.get_nickname() + "_")

	def on_welcome(self, irc, event):
		time.sleep(1)
		for i in range(0, len(self.config.automsg)):
			irc.privmsg(str(self.config.automsg[i].to),
					str(self.config.automsg[i].msg))
		time.sleep(1)
		for i in range(0, len(self.config.autojoin)):
			irc.join(str(self.config.autojoin[i].chan))
			irc.privmsg(str(self.config.autojoin[i].chan),
					str(self.config.automsg[i].msg))

		#c.join(self.channel)

	def on_privmsg(self, irc, event):
        	nick = nm_to_n(event.source())
		irc.privmsg(nick,"What?")

	#def on_pubmsg(self, irc, event):

	def msg(self, txt):
		print "hackabot: ",txt

def main():
	import sys
	if len(sys.argv) != 2:
		print "Usage: ",argv[0]," path/to/config.xml"
		sys.exit(1)

	#s = string.split(sys.argv[1], ":", 1)
	#server = s[0]
	#if len(s) == 2:
	#	try:
	#		port = int(s[1])
	#	except ValueError:
	#		print "Error: Erroneous port."
	#		sys.exit(1)
	#else:
	#	port = 6667
	#channel = sys.argv[2]
	#nickname = sys.argv[3]

	bot = Hackabot(sys.argv[1])
	bot.start()

if __name__ == "__main__":
	main()

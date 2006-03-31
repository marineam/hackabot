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
import thread
import socket
import time
import sys
import os
import re
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_u, nm_to_h, Event 
from amara import binderytools

class Hackabot(SingleServerIRCBot):
	def __init__(self, file):
		# TODO: Semivalidate 'file' before actually using it.
		self.config = binderytools.bind_file(file).hackabot
		self.msg("Setting up irc object for "+str(self.config.server)+"...")
		os.putenv("HACKABOT_DIR", str(self.config.directory))
		os.putenv("HACKABOT_ETC", \
			str(self.config.directory)+"/"+str(self.config.etc))
		os.putenv("HACKABOT_CMD", \
			str(self.config.directory)+"/"+str(self.config.commands))
		os.putenv("HACKABOT_SOCK", \
			str(self.config.directory)+"/"+str(self.config.socket))

		SingleServerIRCBot.__init__(self, [(self.config.server.xml_text_content(), int(self.config.port.xml_text_content()))], self.config.nick.xml_text_content(), self.config.name.xml_text_content())

	def on_nicknameinuse(self, c, event):
		self.connection.nick(self.connection.get_nickname() + "_")

	def on_welcome(self, c, event):
		time.sleep(1)
		self.msg("Connected!")
		thread.start_new_thread(self.server,tuple())
		for automsg in self.config.automsg:
			self.msg("sending msg to "+str(automsg.to))
			self.privmsg(str(automsg.to), str(automsg.msg))
		time.sleep(1)
		for autojoin in self.config.autojoin:
			self.msg("joining "+str(autojoin.chan))
			self.connection.join(str(autojoin.chan))
			if hasattr(autojoin, 'msg'):
				self.privmsg(str(autojoin.chan), str(autojoin.msg))

	def on_privmsg(self, c, event):
        	to = nm_to_n(event.source())
		thread.start_new_thread(self.do_msg,(event,to))

	def on_pubmsg(self, c, event):
		to = event.target()
		thread.start_new_thread(self.do_msg,(event,to))

	def on_action(self, c, event):
		to = event.target()
		thread.start_new_thread(self.do_hook,(event,to))

	def on_notice(self, c, event):
		to = event.target()
		thread.start_new_thread(self.do_hook,(event,to))

	def on_join(self, c, event):
		to = event.target()
		thread.start_new_thread(self.do_hook,(event,to))

	def on_part(self, c, event):
		to = event.target()
		thread.start_new_thread(self.do_hook,(event,to))

	def on_quit(self, c, event):
		to = event.target()
		thread.start_new_thread(self.do_hook,(event,to))

	def privmsg(self, to, txt):
		self.connection.privmsg(to, txt)
	
		nickmask = self.connection.nickname \
			+ "!" + self.connection.username \
			+ "@" + self.connection.localhost

		if re.match(r'#',to):
			self.do_hook(Event("pubsnd", nickmask, to, [txt]),to)
		else:
			self.do_hook(Event("privsnd", nickmask, to, [txt]),to)

	def action(self, to, txt):
		self.connection.action(to, txt)
	
		nickmask = self.connection.nickname \
			+ "!" + self.connection.username \
			+ "@" + self.connection.localhost

		self.do_hook(Event("action", nickmask, to, [txt]),to)

	def notice(self, to, txt):
		self.connection.notice(to, txt)
	
		nickmask = self.connection.nickname \
			+ "!" + self.connection.username \
			+ "@" + self.connection.localhost

		self.do_hook(Event("notice", nickmask, to, [txt]),to)

	def do_msg(self, event, to):
		nick = nm_to_n(event.source())
		r = self.do_hook(event, to)
		if r != "noall" and r != "nocmd":
			self.do_cmd(event, to)

	def do_hook(self, event, to):
		ret = "ok"
		dir = "/"+str(self.config.directory)+\
			"/"+str(self.config.hooks)+\
			"/"+event.eventtype()

		hooks = os.listdir(dir)
		for hook in hooks:
			if re.match(r'\.', hook):
				continue

			if len(event.arguments()) > 0:
				arg = event.arguments()[0]
			else:
				arg = None

			r = self.do_prog(event, to, dir+"/"+hook, arg)
			if r == "noall" or r == "nohook":
				ret = r
				break
			elif r == "nocmd":
				ret = r
		return ret

	def do_cmd(self, event, to):
		c = re.match(r'!([^\s/]+)\s*(.*)', event.arguments()[0])
		if (not c):
			return

		cmd = "/"+str(self.config.directory)+\
			"/"+str(self.config.commands)+\
			"/"+c.group(1)
		msg = c.group(2)
		
		return self.do_prog(event, to, cmd, msg)
	
	def do_prog(self, event, to, cmd, msg):
		if not os.access(cmd,os.X_OK):
			return
		
		write,read = os.popen2(cmd)
		write.write("type "+event.eventtype()+"\n")
		write.write("nick "+nm_to_n(event.source())+"\n")
		write.write("user "+nm_to_u(event.source())+"\n")
		write.write("host "+nm_to_h(event.source())+"\n")
		if isinstance(to, str):
			write.write("to "+to+"\n")
		if isinstance(msg, str):
			write.write("msg "+msg+"\n")
		write.close()

		ret = self.process(read, to)
		read.close()
		return ret
	
	def process(self, sockfile, to = None):
		ret = "ok"
		sendnext = False
		rw = (sockfile.mode != 'r')

		while True:
			line = sockfile.readline().rstrip("\n")
			if not line:
				break

			if to and sendnext:
				self.privmsg(to, line)
			elif to and re.match(r'sendnext', line):
				sendnext = True
			elif to and re.match(r'send\s+(.+)',line):
				c = re.match(r'send\s+(.+)',line)
				self.privmsg(to, c.group(1))
			elif to and re.match(r'notice\s+(.+)',line):
				c = re.match(r'notice\s+(.+)',line)
				self.notice(to, c.group(1))
			elif to and re.match(r'me\s+(.+)',line):
				c = re.match(r'me\s+(.+)',line)
				self.action(to, c.group(1))
			elif to and re.match(r'action\s+(.+)',line):
				c = re.match(r'action\s+(.+)',line)
				self.action(to, c.group(1))
			elif re.match(r'to\s+(\S+)',line):
				c = re.match(r'to\s+(\S+)',line)
				to = c.group(1)
			elif re.match(r'nick\s+(\S+)',line):
				c = re.match(r'nick\s+(\S+)',line)
				self.connection.nick(c.group(1))
			elif re.match(r'topic\s+(.+)',line):
				c = re.match(r'topic\s+(.+)',line)
				self.connection.topic(to, c.group(1))
			elif re.match(r'join\s+(\S+)',line):
				c = re.match(r'join\s+(\S+)',line)
				self.connection.join(c.group(1))
			elif re.match(r'part\s+(\S+)',line):
				c = re.match(r'part\s+(\S+)',line)
				self.connection.part(c.group(1))
			elif re.match(r'quit\s*(.*)',line):
				c = re.match(r'quit\s*(.*)',line)
				self.msg("Exiting!")
				self.disconnect(c.group(1))
				self.connection.execute_delayed(1,sys.exit)
			elif re.match(r'chservop\s+(\S+)\s*(\S*)',line):
				c = re.match(r'chservop\s+(\S+)\s*(\S*)',line)
				self.connection.privmsg("ChanServ", 
					"op "+c.group(1)+" "+c.group(2))
			elif rw and re.match(r'names\s+(#\S*)',line):
				c = re.match(r'names\s+(#\S*)',line)
				chan = c.group(1)
				if self.channels.has_key(chan):
					list = self.channels[chan].users()
					names = " "+string.join(list," ")
				else:
					names = ""
				sockfile.write("names "+chan+names+"\n")
				sockfile.flush()
			elif re.match(r'nocmd',line):
				ret = "nocmd"
			elif re.match(r'nohook',line):
				ret = "nohook"
			elif re.match(r'noall',line):
				ret = "noall"
			else:
				self.msg("Unknown request: "+line)
		return ret
	
	def server(self):
		file = "/"+str(self.config.directory)+ \
			"/"+str(self.config.socket)

		self.msg("Creating control socket...")
		listen = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		os.unlink(file)
		listen.bind(file)
		listen.listen(5)

		while True:
			client,c = listen.accept()
			thread.start_new_thread(self.servclient,(client,))
		#what should I do with this:
		listen.close()
	
	def servclient(self, client):
		#self.msg("New control socket connection.")
		self.process(client.makefile('r+'))
		#self.msg("Closing control socket connection.")
		client.close()

	def msg(self, txt):
		print "hackabot:",txt

def main():
	if len(sys.argv) != 2:
		print "Usage:",sys.argv[0],"path/to/config.xml"
		sys.exit(1)

	bot = Hackabot(sys.argv[1])
	bot.start()

if __name__ == "__main__":
	main()

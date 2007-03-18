#!/usr/bin/env python
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

		# reconnect is not required, but needs to exist
		if not hasattr(self.config, "reconnect"):
			self.config.xml_append_fragment(
				"<reconnect>60</reconnect>")
		
		self.msg("Setting up irc object for "+str(self.config.server)+"...")
		os.putenv("HACKABOT_CFG", file)
		os.putenv("HACKABOT_DIR", str(self.config.directory))
		os.putenv("HACKABOT_ETC", \
			str(self.config.directory)+"/"+str(self.config.etc))
		os.putenv("HACKABOT_CMD", \
			str(self.config.directory)+"/"+str(self.config.commands))
		os.putenv("HACKABOT_SOCK", \
			str(self.config.directory)+"/"+str(self.config.socket))

		SingleServerIRCBot.__init__(self, [(str(self.config.server), int(str(self.config.port)))], str(self.config.nick), str(self.config.name), int(str(self.config.reconnect)))

	def on_nicknameinuse(self, c, event):
		self.connection.nick(self.connection.get_nickname() + "_")

	def on_welcome(self, c, event):
		time.sleep(1)
		self.msg("Connected!")
		thread.start_new_thread(self.server,tuple())
		if hasattr(self.config, 'automsg'):
			for automsg in self.config.automsg:
				self.msg("sending msg to "+str(automsg.to))
				self.privmsg(str(automsg.to), str(automsg.msg))
		time.sleep(1)
		if hasattr(self.config, 'autojoin'):
			for autojoin in self.config.autojoin:
				self.msg("joining "+str(autojoin.chan))
				if hasattr(autojoin, 'password'):
					self.connection.join( \
						str(autojoin.chan), \
						str(autojoin.password))
				else:
					self.connection.join(str(autojoin.chan))
				if hasattr(autojoin, 'msg'):
					self.privmsg(str(autojoin.chan), \
						str(autojoin.msg))

	def on_privmsg(self, c, event):
        	to = nm_to_n(event.source())
		thread.start_new_thread(self.do_msg,(event,to))

	def on_pubmsg(self, c, event):
		to = event.target()
		thread.start_new_thread(self.do_msg,(event,to))

	def on_action(self, c, event):
		to = event.target()
		thread.start_new_thread(self.do_hook,(event,to))

	def on_pubnotice(self, c, event):
		to = event.target()
		thread.start_new_thread(self.do_hook,(event,to))

	def on_privnotice(self, c, event):
		to = event.target()
		thread.start_new_thread(self.do_hook,(event,to))

	def on_join(self, c, event):
		to = event.target()
		thread.start_new_thread(self.do_hook,(event,to))

	def on_part(self, c, event):
		to = event.target()
		thread.start_new_thread(self.do_hook,(event,to))

	def on_topic(self, c, event):
		# quick hack so topic changes are handeled by currenttopic/topicinfo all the time
		self.connection.topic(event.target())

	def on_currenttopic(self, c, event):
		to = event.arguments()[0]
		if (self.channels.has_key(to)):
			self.channels[to].topic = event.arguments()[1]
		else:
			self.msg("currenttopic: chan '"+to+"' not known")
		thread.start_new_thread(self.do_hook,(event,to))

	def on_topicinfo(self, c, event):
		to = event.arguments()[0]
		if (self.channels.has_key(to)):
			self.channels[to].topic_nick = event.arguments()[1]
			self.channels[to].topic_time = event.arguments()[2]
		else:
			self.msg("topicinfo: chan '"+to+"' not known")
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

		if re.match(r'#',to):
			self.do_hook(Event("pubnotice", nickmask, to, [txt]),to)
		else:
			self.do_hook(Event("privnotice", nickmask, to, [txt]),to)

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

		if not os.access(dir,os.R_OK):
			return ret

		hooks = os.listdir(dir)
		hooks.sort()
		for hook in hooks:
			if re.match(r'\.', hook):
				continue

			if event.eventtype() == "currenttopic":
				to = event.arguments()[0]
				arg = event.arguments()[1]
				event._source = None
			elif event.eventtype() == "topicinfo":
				to = event.arguments()[0]
				arg = event.arguments()[1]+" "+event.arguments()[2]
				event._source = None
			elif len(event.arguments()) > 0:
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
		if isinstance(event.source(), str):
			write.write("nick "+nm_to_n(event.source())+"\n")
			if event.source().find('!') > 0: 
				write.write("user "+ \
					nm_to_u(event.source())+"\n")
			if event.source().find('@') > 0: 
				write.write("host "+ \
					nm_to_h(event.source())+"\n")
		if isinstance(to, str):
			write.write("to "+to+"\n")
		if isinstance(msg, str):
			write.write("msg "+msg+"\n")
		write.write("currentnick %s\n" % self.connection.get_nickname())
		write.close()

		ret = self.process(read, to, event)
		read.close()
		return ret
	
	def process(self, sockfile, to = None, event = None):
		ret = "ok"
		sendnext = False
		rw = (sockfile.mode != 'r')

		for line in sockfile:
			line = line.rstrip("\n")

			if to and sendnext:
				self.privmsg(to, line)
				continue

			c = re.match(r'sendnext', line)
			if to and c:
				sendnext = True
				continue

			c = re.match(r'send\s+(.+)',line)
			if to and c:
				self.privmsg(to, c.group(1))
				continue

			c = re.match(r'notice\s+(.+)',line)
			if to and c:
				self.notice(to, c.group(1))
				continue

			c = re.match(r'(me|action)\s+(.+)',line)
			if to and c:
				self.action(to, c.group(2))
				continue

			c = re.match(r'to\s+(\S+)',line)
			if c:
				to = c.group(1)
				continue

			c = re.match(r'nick\s+(\S+)',line)
			if c:
				self.connection.nick(c.group(1))
				continue

			c = re.match(r'topic\s+(.+)',line)
			if c:
				self.connection.topic(to, c.group(1))
				continue

			c = re.match(r'join\s+(\S+)',line)
			if c:
				self.connection.join(c.group(1))
				continue

			c = re.match(r'part\s+(\S+)',line)
			if c:
				self.connection.part(c.group(1))
				continue

			c = re.match(r'quit\s*(.*)',line)
			if c:
				self.msg("Exiting!")
				self.disconnect(c.group(1))
				self.connection.execute_delayed(1,sys.exit)
				continue

			c = re.match(r'currenttopic\s+(#\S+)',line)
			if rw and c:
				chan = c.group(1)
				if self.channels.has_key(chan):
					if hasattr(self.channels[chan], 'topic'):
						topic = " "+self.channels[chan].topic
					else:
						topic = ""
				else:
					topic = ""
				sockfile.write("currenttopic "+chan+topic+"\n")
				sockfile.flush()
				continue

			c = re.match(r'topicinfo\s+(#\S+)',line)
			if rw and c:
				chan = c.group(1)
				if self.channels.has_key(chan):
					if hasattr(self.channels[chan], 'topic_nick') and \
						hasattr(self.channels[chan], 'topic_time'):
						topic = " "+self.channels[chan].topic_nick \
							+" "+self.channels[chan].topic_time
					else:
						topic = ""
				else:
					topic = ""
				sockfile.write("topicinfo "+chan+topic+"\n")
				sockfile.flush()
				continue

			c = re.match(r'names\s+(#\S+)',line)
			if rw and c:
				chan = c.group(1)
				if self.channels.has_key(chan):
					list = self.channels[chan].users()
					names = " "+string.join(list," ")
				else:
					names = ""
				sockfile.write("names "+chan+names+"\n")
				sockfile.flush()
				continue

			if rw and re.match(r'channels',line):
				list = self.channels.keys()
				names = " "+string.join(list," ")
				sockfile.write("channels"+names+"\n")
				sockfile.flush()
				continue

			if rw and re.match(r'currentnick',line):
				sockfile.write("currentnick %s\n" %
					self.connection.get_nickname())
				sockfile.flush()
				continue

			if event and re.match(r'msg\s*(.*)',line) and ( \
					event.eventtype() == "pubmsg" or \
					event.eventtype() == "privmsg" or \
					event.eventtype() == "pubsnd" or \
					event.eventtype() == "privsnd" or \
					event.eventtype() == "pubnotice" or \
					event.eventtype() == "privnotice" or \
					event.eventtype() == "action"):
				c = re.match(r'msg\s*(.*)',line)
				event._arguments[0] = c.group(1)
				continue

			if re.match(r'nocmd',line):
				ret = "nocmd"
				continue

			if re.match(r'nohook',line):
				ret = "nohook"
				continue

			if re.match(r'noall',line):
				ret = "noall"
				continue
			
			self.msg("Unknown request: "+line)

		return ret
	
	def server(self):
		file = "/"+str(self.config.directory)+ \
			"/"+str(self.config.socket)

		self.msg("Creating control socket...")
		listen = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	
		# Ignore an unlink error since it might not exist
		try:
			os.unlink(file)
		except OSError:
			pass

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

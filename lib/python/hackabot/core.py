"""Hackabot Core"""

import re
import time

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor
from twisted.python import context

from hackabot import log, db, plugin

def nick(sent_by):
    return sent_by.split('!',1)[0]

class HBotConnection(irc.IRCClient):
    """Protocol handler for a single IRC Connection

    This class cannot hold any state needed between reconnects, etc.
    """

    sourceURL = None

    def connectionMade(self):
        # Hack to auto magically set the log prefix based on network
        # name rather than class name
        self.transport.logstr = self.factory.logstr

        log.info("Connected!", prefix=self.factory.logstr)

        # Used by IRCClient
        self.nickname = self.factory.nickname
        self.username = self.factory.username
        self.realname = self.factory.realname

        # Used to track channel information
        self.channels = {}

        irc.IRCClient.connectionMade(self)

    def signedOn(self):
        log.info("Signed On!")
        self.factory.clientConnected(self)

        for chan in self.factory.channels:
            self.join(chan['channel'], chan['password'])

    def nickChanged(self, nick):
        log.info("Nick changed to: %s" % nick)
        old = self.nickname
        self.nickname = nick

        event = {
                'type': 'rename',
                'old': old,
                'new': new,
                'time': time.time()
                }

        plugin.manager.hook(self, event)

    def privmsg(self, sent_by, sent_to, msg):
        sent_by = nick(sent_by)
        sent_to = nick(sent_to)
        log.debug("<%s> %s" % (sent_by, msg))

        event = {
                'type': 'msg',
                'sent_by': sent_by,
                'sent_to': sent_to,
                'text': msg,
                'time': time.time()
                }

        if sent_to == self.nickname:
            event['reply_to'] = sent_by
        else:
            event['reply_to'] = sent_to

        plugin.manager.hook(self, event)

        if len(msg) > 1 and msg[0] == '!':
            match = re.match("(\w+)(\W.*|$)", msg[1:])
            command = match.group(1)
            text = match.group(2)
            text = text.strip()

            cmdevent = event.copy()
            cmdevent['type'] = "command"
            cmdevent['command'] = command
            cmdevent['text'] = text

            plugin.manager.command(self, cmdevent)

    def action(self, sent_by, sent_to, msg):
        sent_by = nick(sent_by)
        sent_to = nick(sent_to)
        log.debug("<%s> %s" % (sent_by, msg))

        event = {
                'type': 'me',
                'sent_by': sent_by,
                'sent_to': sent_to,
                'text': msg,
                'time': time.time()
                }

        if sent_to == self.nickname:
            event['reply_to'] = sent_by
        else:
            event['reply_to'] = sent_to

        plugin.manager.hook(self, event)

    def noticed(self, sent_by, sent_to, msg):
        sent_by = nick(sent_by)
        sent_to = nick(sent_to)
        log.debug("<%s> %s" % (sent_by, msg))

        event = {
                'type': 'notice',
                'sent_by': sent_by,
                'sent_to': sent_to,
                'text': msg,
                'time': time.time()
                }

        if sent_to == self.nickname:
            event['reply_to'] = sent_by
        else:
            event['reply_to'] = sent_to

        plugin.manager.hook(self, event)

    def joined(self, channel):
        log.info("Joined %s" % channel)
        self.channels[channel] = {'users': set(), 'topic': ""}

        event = {
                'type': 'join',
                'user': self.nickname,
                'channel': channel,
                'time': time.time()
                }

        plugin.manager.hook(self, event)

    def left(self, channel):
        log.info("Left %s" % channel)
        del self.channels[channel]

        event = {
                'type': 'part',
                'user': self.nickname,
                'channel': channel,
                'text': "",
                'time': time.time()
                }

        plugin.manager.hook(self, event)

    def kickedFrom(self, channel, kicker, msg):
        log.info("Kicked from %s by %s: %s" % (channel, nick(kicker), msg))
        del self.channels[channel]

        event = {
                'type': 'kick',
                'kicker': kicker,
                'kickee': self.nickname,
                'channel': channel,
                'text': msg,
                'time': time.time()
                }

        plugin.manager.hook(self, event)

    def topicUpdated(self, user, channel, topic):
        log.debug("%s topic: %s" % (channel, topic))
        self.channels[channel]['topic'] = topic

        event = {
                'type': 'topic',
                'user': user,
                'channel': channel,
                'text': topic,
                'time': time.time()
                }

        plugin.manager.hook(self, event)

    def userJoined(self, user, channel):
        log.debug("%s joined channel %s" % (user, channel))
        self.channels[channel]['users'].add(user)

        event = {
                'type': 'join',
                'user': user,
                'channel': channel,
                'time': time.time()
                }

        plugin.manager.hook(self, event)

    def userLeft(self, user, channel):
        log.debug("%s left channel %s" % (user, channel))
        self.channels[channel]['users'].discard(user)

        # TODO: re-implement this so we can get the text
        event = {
                'type': 'part',
                'user': user,
                'channel': channel,
                'text': "",
                'time': time.time()
                }

        plugin.manager.hook(self, event)

    def userKicked(self, user, channel, kicker, msg):
        log.debug("%s kicked from %s by %s: %s" % (user, channel, kicker, msg))
        self.channels[channel]['users'].discard(user)

        event = {
                'type': 'kick',
                'kicker': kicker,
                'kickee': user,
                'channel': channel,
                'text': msg,
                'time': time.time()
                }

        plugin.manager.hook(self, event)

    def userQuit(self, user, msg):
        log.debug("%s quit: %s" % (user, msg))
        for chan in self.channels:
            chan['users'].discard(user)

        event = {
                'type': 'quit',
                'user': user,
                'text': msg,
                'time': time.time()
                }

        plugin.manager.hook(self, event)

    def userRenamed(self, oldname, newname):
        log.debug("%s changed to %s" % oldname, newname)
        for chan in self.channels:
            if oldname in chan['users']:
                chan['users'].discard(oldname)
                chan['users'].add(newname)

        event = {
                'type': 'rename',
                'old': oldname,
                'new': newname,
                'time': time.time()
                }

        plugin.manager.hook(self, event)

    def irc_RPL_NAMREPLY(self, prefix, params):
        # Odd that twisted doesn't handle this one
        channel = params[2]
        users = params[3]

        log.debug("%s users: %s" % (channel, users))

        users = [u.lstrip("+@") for u in users.split()]
        users.sort()

        # Is it safe to assume that a single NAMREPLY covers all users?
        self.channels[channel]['users'] = set(users)

        event = {
            'type': 'names',
            'channel': channel,
            'users': users,
            'time': time.time()
        }
        plugin.manager.hook(self, event)

    def irc_unknown(self, prefix, command, params):
        log.trace("unknown: %s %s %s" % (prefix, command, params))

    # Hook into commands for logging, etc.
    def msg(self, to, msg, length=None):
        irc.IRCClient.msg(self, to, msg, length)

        if msg and msg[0] == irc.X_DELIM:
            # Ignore any CTCP stuff
            ctcp = irc.ctcpExtract(msg)
            if not ctcp['normal']:
                return
            msg = " ".join(ctcp['normal'])

        event = {
                'type': 'msg',
                'sent_by': self.nickname,
                'sent_to': to,
                'reply_to': None,
                'text': msg,
                'time': time.time()
                }

        plugin.manager.hook(self, event)

    def notice(self, to, msg):
        irc.IRCClient.notice(self, to, msg)

        if msg and msg[0] == irc.X_DELIM:
            # Ignore any CTCP stuff
            ctcp = irc.ctcpExtract(msg)
            if not ctcp['normal']:
                return
            msg = " ".join(ctcp['normal'])

        event = {
                'type': 'notice',
                'sent_by': self.nickname,
                'sent_to': to,
                'reply_to': None,
                'text': msg,
                'time': time.time()
                }

        plugin.manager.hook(self, event)

    def me(self, to, msg):
        # Override the twisted behavior of only allowing channels for this
        self.ctcpMakeQuery(to, [('ACTION', msg)])

        event = {
                'type': 'me',
                'sent_by': self.nickname,
                'sent_to': to,
                'reply_to': None,
                'text': msg,
                'time': time.time()
                }

        plugin.manager.hook(self, event)

# So other bits can get access to the current connections
connections = {}

class HBotNetwork(protocol.ClientFactory):
    """Maintain a connection to an IRC network"""

    protocol = HBotConnection
    noisy = False

    def __init__(self, network, servers, channels):
        assert servers
        assert 'nick' in network
        self.network = network['network']
        self.nickname = network['nick']
        self.username = network['user']
        self.realname = network['name']
        self.servers = servers
        self.current = None
        self.channels = channels
        self._sviter = iter(self.servers)
        self._delay = 1

        if network['network'] is None:
            self.logstr = "client"
        else:
            self.logstr = "client:%s" % network['network']

    def connect(self):
        """Connect to a server in this IRC network"""

        try:
            self.current = self._sviter.next()
        except StopIteration:
            self._sviter = iter(self.servers)
            self.current = self._sviter.next()

        if self.current['ssl']:
            raise Exception("SSL Connections are unimplemented!")
        else:
            reactor.connectTCP(self.current['host'],
                    self.current['port'], self)

    def _reconnect(self):
        # Failure! Try again...
        reactor.callLater(self._delay, self.connect)

        if self._delay < 128:
            self._delay *= 2

    def startedConnecting(self, connector):
        log.info("Connecting to %s:%s..." % (self.current['host'],
            self.current['port']), prefix=self.logstr)

    def clientConnected(self, connection):
        # Called from HBotConnection once connection is OK
        self._delay = 1
        connections[self.network] = connection

    def clientConnectionLost(self, connector, reason):
        log.warn("Lost connection to %s:%s: %s" % (self.current['host'],
            self.current['port'], reason.value), prefix=self.logstr)
        del connections[self.network]
        self._reconnect()

    def clientConnectionFailed(self, connector, reason):
        log.warn("Failed to connect to %s:%s: %s" % (self.current['host'],
            self.current['port'], reason.value), prefix=self.logstr)
        del connections[self.network]
        self._reconnect()

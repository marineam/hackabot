"""Hackabot Core"""

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
        self.factory.clientConnected()

        for chan in self.factory.channels:
            self.join(chan['channel'], chan['password'])

    def nickChanged(self, nick):
        self.nickname = nick
        log.info("Nick changed to: %s" % nick)
        plugin.manager.hook('rename', self, self.nickname, nick)

    def privmsg(self, sent_by, sent_to, msg):
        sent_by = nick(sent_by)
        sent_to = nick(sent_to)
        log.debug("<%s> %s" % (sent_by, msg))

        if sent_to == self.nickname:
            reply_to = sent_by
        else:
            reply_to = sent_to

        plugin.manager.hook('msg', self, sent_by, sent_to, reply_to, msg)

        if len(msg) > 1 and msg[0] == '!':
            command, space, text = msg[1:].partition(" ")
            plugin.manager.command(command,self,sent_by,sent_to,reply_to,text)

    def action(self, sent_by, sent_to, msg):
        sent_by = nick(sent_by)
        sent_to = nick(sent_to)
        log.debug("<%s> %s" % (sent_by, msg))

        if sent_to == self.nickname:
            reply_to = sent_by
        else:
            reply_to = sent_to

        plugin.manager.hook('action', self, sent_by, sent_to, reply_to, msg)

    def noticed(self, sent_by, sent_to, msg):
        sent_by = nick(sent_by)
        sent_to = nick(sent_to)
        log.debug("<%s> %s" % (sent_by, msg))

        if sent_to == self.nickname:
            reply_to = sent_by
        else:
            reply_to = sent_to

        plugin.manager.hook('notice', self, sent_by, sent_to, reply_to, msg)

    def joined(self, channel):
        log.info("Joined %s" % channel)
        self.channels[channel] = {'users': set(), 'topic': ""}

        plugin.manager.hook('join', self, self.nickname, channel)

    def left(self, channel):
        log.info("Left %s" % channel)
        del self.channels[channel]

        plugin.manager.hook('part', self, self.nickname, channel)

    def kickedFrom(self, channel, kicker, msg):
        log.info("Kicked from %s by %s: %s" % (channel, nick(kicker), msg))
        del self.channels[channel]

        plugin.manager.hook('kick', self, kicker, self.nickname, channel, msg)

    def topicUpdated(self, user, channel, topic):
        log.debug("%s topic: %s" % (channel, topic))
        self.channels[channel]['topic'] = topic

        plugin.manager.hook('topic', self, user, channel, topic)

    def userJoined(self, user, channel):
        log.debug("%s joined channel %s" % (user, channel))
        self.channels[channel]['users'].add(user)

        plugin.manager.hook('join', self, user, channel)

    def userLeft(self, user, channel):
        log.debug("%s left channel %s" % (user, channel))
        self.channels[channel]['users'].discard(user)

        # TODO: re-implement this so we can get the text
        plugin.manager.hook('part', self, user, channel, "")

    def userKicked(self, user, channel, kicker, msg):
        log.debug("%s kicked from %s by %s: %s" % (user, channel, kicker, msg))
        self.channels[channel]['users'].discard(user)

        plugin.manager.hook('kick', self, kicker, user, channel, msg)

    def userQuit(self, user, msg):
        log.debug("%s quit: %s" % (user, msg))
        for chan in self.channels:
            chan['users'].discard(user)

        plugin.manager.hook('quit', self, user, msg)

    def userRenamed(self, oldname, newname):
        log.debug("%s changed to %s" % oldname, newname)
        for chan in self.channels:
            if oldname in chan['users']:
                chan['users'].discard(oldname)
                chan['users'].add(newname)

        plugin.manager.hook('rename', self, oldname, newname)

    def irc_RPL_NAMREPLY(self, prefix, params):
        # Odd that twisted doesn't handle this one
        channel = params[2]
        users = params[3]

        log.debug("%s users: %s" % (channel, users))

        users = [u.lstrip("+@") for u in users.split()]
        users.sort()

        # Is it safe to assume that a single NAMREPLY covers all users?
        self.channels[channel]['users'] = set(users)

        plugin.manager.hook('names', self, channel, users)

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

        plugin.manager.hook('msg', self, self.nickname, to, None, msg)

    def notice(self, to, msg):
        irc.IRCClient.notice(self, to, msg)

        if msg and msg[0] == irc.X_DELIM:
            # Ignore any CTCP stuff
            ctcp = irc.ctcpExtract(msg)
            if not ctcp['normal']:
                return
            msg = " ".join(ctcp['normal'])

        plugin.manager.hook('notice', self, self.nickname, to, None, msg)

    def me(self, to, msg):
        # Override the twisted behavior of only allowing channels for this
        self.ctcpMakeQuery(to, [('ACTION', msg)])
        plugin.manager.hook('me', self, self.nickname, to, None, msg)


class HBotNetwork(protocol.ClientFactory):
    """Maintain a connection to an IRC network"""

    protocol = HBotConnection
    noisy = False

    def __init__(self, network, servers, channels):
        assert servers
        assert 'nick' in network
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

    def clientConnected(self):
        # Called from HBotConnection once connection is OK
        self._delay = 1

    def clientConnectionLost(self, connector, reason):
        log.warn("Lost connection to %s:%s: %s" % (self.current['host'],
            self.current['port'], reason.value), prefix=self.logstr)
        self._reconnect()

    def clientConnectionFailed(self, connector, reason):
        log.warn("Failed to connect to %s:%s: %s" % (self.current['host'],
            self.current['port'], reason.value), prefix=self.logstr)
        self._reconnect()

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
        log.info("Nick changed to: %s" % nick)

        db.dblog('rename', sent_by=self.nickname, sent_to=nick)
        self.nickname = nick

    def privmsg(self, sent_by, sent_to, msg):
        sent_by = nick(sent_by)
        sent_to = nick(sent_to)
        log.debug("<%s> %s" % (sent_by, msg))

        if sent_to == self.nickname:
            db.dblog('msg', sent_by=sent_by, sent_to=sent_to, text=msg)
        else:
            db.dblog('msg', sent_by=sent_by, channel=sent_to, text=msg)

        if len(msg) > 1 and msg[0] == '!':
            command, space, text = msg[1:].partition(" ")
            plugin.manager.command(command, self, sent_by, sent_to, text)


    def action(self, sent_by, sent_to, msg):
        sent_by = nick(sent_by)
        sent_to = nick(sent_to)
        log.debug("<%s> %s" % (sent_by, msg))

        if sent_to == self.nickname:
            db.dblog('action', sent_by=sent_by, sent_to=sent_to, text=msg)
        else:
            db.dblog('action', sent_by=sent_by, channel=sent_to, text=msg)

    def noticed(self, sent_by, sent_to, msg):
        sent_by = nick(sent_by)
        sent_to = nick(sent_to)
        log.debug("<%s> %s" % (sent_by, msg))

        if sent_to == self.nickname:
            db.dblog('notice', sent_by=sent_by, sent_to=sent_to, text=msg)
        else:
            db.dblog('notice', sent_by=sent_by, channel=sent_to, text=msg)

    def joined(self, channel):
        log.info("Joined %s" % channel)
        self.channels[channel] = {'users': set(), 'topic': ""}

        db.dblog('join', sent_by=self.nickname, channel=channel)

    def left(self, channel):
        log.info("Left %s" % channel)
        del self.channels[channel]

        db.dblog('part', sent_by=self.nickname, channel=channel)

    def kickedFrom(self, channel, kicker, msg):
        log.info("Kicked from %s by %s: %s" % (channel, nick(kicker), msg))
        del self.channels[channel]

        db.dblog('kick', sent_by=kicker, sent_to=self.nickname,
                    channel=channel, text=msg)

    def topicUpdated(self, user, channel, topic):
        log.debug("%s topic: %s" % (channel, topic))
        self.channels[channel]['topic'] = topic

        db.dblog('topic', sent_by=user, channel=channel, text=topic)

    def userJoined(self, user, channel):
        log.debug("%s joined channel %s" % (user, channel))
        self.channels[channel]['users'].add(user)

        db.dblog('join', sent_by=user, channel=channel)

    def userLeft(self, user, channel):
        log.debug("%s left channel %s" % (user, channel))
        self.channels[channel]['users'].discard(user)

        db.dblog('part', sent_by=user, channel=channel)

    def userKicked(self, user, channel, kicker, msg):
        log.debug("%s kicked from %s by %s: %s" % (user, channel, kicker, msg))
        self.channels[channel]['users'].discard(user)

        db.dblog('kick', sent_by=kicker, sent_to=user,
                    channel=channel, text=msg)

    def userQuit(self, user, msg):
        log.debug("%s quit: %s" % (user, msg))
        for chan in self.channels:
            chan['users'].discard(user)

        db.dblog('quit', sent_by=user, text=msg)

    def userRenamed(self, oldname, newname):
        log.debug("%s changed to %s" % oldname, newname)
        for chan in self.channels:
            if oldname in chan['users']:
                chan['users'].discard(oldname)
                chan['users'].add(newname)

        db.dblog('rename', sent_by=oldname, sent_to=newname)

    def irc_RPL_NAMREPLY(self, prefix, params):
        # Odd that twisted doesn't handle this one
        channel = params[2]
        users = params[3]

        log.debug("%s users: %s" % (channel, users))

        users = [u.lstrip("+@") for u in users.split()]
        users.sort()

        # Is it safe to assume that a single NAMREPLY covers all users?
        self.channels[channel]['users'] = set(users)

        db.dblog('stats', channel=channel, text=users)

    def irc_unknown(self, prefix, command, params):
        log.trace("unknown: %s %s %s" % (prefix, command, params))


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

"""Hackabot Core"""

import os
import re
import time

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor, error, defer

# SSL support is screwy
try:
   from twisted.internet import ssl
except ImportError:
   # happens the first time the interpreter tries to import it
   ssl = None
if ssl and not ssl.supported:
   # happens second and later times
   ssl = None

from hackabot import db, log, plugin, remote, parse_config
from hackabot import ConfigError, NotConnected
from hackabot.etree import ElementTree
from hackabot.acl import ACL

def nick(sent_by):
    return sent_by.split('!',1)[0]

class HBotManager(object):
    """Manage various network connections"""

    def __init__(self, path=None, xml=None, exit_cb=None, exit_args=()):
        self.config = parse_config(path, xml)
        self.dbpool = db.ConnectionPool(self.config)
        self.plugins = plugin.PluginManager()
        self._exit_cb = exit_cb
        self._exit_args = exit_args
        self._exit_deferred = None
        self._remote = remote.HBRemoteControl(self)
        self._networks = {}
        self._default = None

        for network in self.config.findall("network"):
            id = network.get("id", None)

            if id not in self._networks:
                net = HBotNetwork(self, network)
            else:
                raise ConfigError("Duplicate network id '%s'" % id)

            if not self._default:
                self._default = net

            self._networks[id] = net

        if len(self._networks) == 0:
            ConfigError("No networks defined!")
        elif len(self._networks) != 1 and None in self._networks:
            ConfigError("Missing network id!")

        self.connect()

    def reload(self):
        """Reload plugins and configs"""
        # TODO: reload the config!
        self.plugins.reload()

    def connect(self):
        """Connect to all configured networks"""
        for net in self._networks.itervalues():
            net.connect()
        self._remote.connect()

    def disconnect(self, message=''):
        """Disconnect all configured networks"""

        self._exit_deferred = d = defer.Deferred()

        log.info("Quitting with message '%s'" % message)
        remote_d = self._remote.disconnect()
        for net in self._networks.itervalues():
            net.disconnect(message)

        d.addCallback(lambda _: remote_d)
        d.addCallback(lambda _: self.plugins.wait())
        return d

    def default(self):
        """The default network"""
        return self._default

    def networkLost(self, id):
        """Callback for when a network stops reconnecting"""

        # If there are no active networks left then quit
        active = False
        for net in self._networks.itervalues():
            if net.reconnect:
                active = True

        if not active:
            if self._exit_cb:
                cb = self._exit_cb
                args = self._exit_args
                self._exit_cb = None
                self._exit_args = None
                cb(*args)

            if self._exit_deferred:
                d = self._exit_deferred
                self._exit_deferred = None
                d.callback(None)

    def __getitem__(self, key):
        return self._networks[key]

    def __len__(self):
        return len(self._networks)

    def __contains__(self, key):
        return key in self._networks


class HBotConnection(irc.IRCClient):
    """Protocol handler for a single IRC Connection

    This class cannot hold any state needed between reconnects, etc.
    """

    # Regex for !cmd commands
    COMMAND = re.compile("^!(\w+)(\W.*|$)")

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
        self.password = self.factory.password

        # Used to track channel information
        self.channels = {}

        # Used by plugins to access global info
        self.manager = self.factory.manager
        self.network = self.factory

        irc.IRCClient.connectionMade(self)

    def signedOn(self):
        log.info("Signed On!")
        self.factory.clientConnected(self)

        for automsg in self.factory.config.findall('automsg'):
            to = automsg.get('to', None)
            msg = automsg.get('msg', None)

            if to and msg:
                self.msg(to, msg)
            else:
                log.error("Invalid automsg: %s" % ElementTree.tostring(automsg))

        for autojoin in self.factory.config.findall('autojoin'):
            chan = autojoin.get('chan', None)
            password = autojoin.get('password', None)

            if chan:
                self.join(chan, password)
            else:
                log.error("Invalid autojoin: %s" % ElementTree.tostring(autojoin))

    def nickChanged(self, nick):
        log.info("Nick changed to: %s" % nick)
        old = self.nickname
        self.nickname = nick

        event = {
                'type': 'rename',
                'old': old,
                'new': nick,
                'time': time.time()
                }

        self.manager.plugins.hook(self, event)

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
            event['private'] = True
        else:
            event['reply_to'] = sent_to
            event['private'] = False

        self.manager.plugins.hook(self, event)

        match = self.COMMAND.match(msg)
        if match:
            command = match.group(1)
            text = match.group(2)
            text = text.strip()

            cmdevent = event.copy()
            cmdevent['type'] = "command"
            cmdevent['command'] = command
            cmdevent['text'] = text

            ok, reply = self.factory.acl.check(cmdevent)
            if reply:
                self.msg(event['reply_to'], reply)
            if ok:
                self.manager.plugins.command(self, cmdevent)

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
            event['private'] = True
        else:
            event['reply_to'] = sent_to
            event['private'] = False

        self.manager.plugins.hook(self, event)

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
            event['private'] = True
        else:
            event['reply_to'] = sent_to
            event['private'] = False

        self.manager.plugins.hook(self, event)

    def joined(self, channel):
        log.info("Joined %s" % channel)
        self.channels[channel] = {'users': set(), 'topic': ""}

        event = {
                'type': 'join',
                'user': self.nickname,
                'reply_to': channel,
                'channel': channel,
                'time': time.time()
                }

        self.manager.plugins.hook(self, event)

    def left(self, channel):
        log.info("Left %s" % channel)
        del self.channels[channel]

        event = {
                'type': 'part',
                'user': self.nickname,
                'reply_to': channel,
                'channel': channel,
                'text': "",
                'time': time.time()
                }

        self.manager.plugins.hook(self, event)

    def kickedFrom(self, channel, kicker, msg):
        log.info("Kicked from %s by %s: %s" % (channel, nick(kicker), msg))
        del self.channels[channel]

        event = {
                'type': 'kick',
                'kicker': kicker,
                'kickee': self.nickname,
                'reply_to': channel,
                'channel': channel,
                'text': msg,
                'time': time.time()
                }

        self.manager.plugins.hook(self, event)

    def topicUpdated(self, user, channel, topic):
        log.debug("%s topic: %s" % (channel, topic))
        self.channels[channel]['topic'] = topic

        event = {
                'type': 'topic',
                'user': user,
                'reply_to': channel,
                'channel': channel,
                'text': topic,
                'time': time.time()
                }

        self.manager.plugins.hook(self, event)

    def userJoined(self, user, channel):
        log.debug("%s joined channel %s" % (user, channel))
        self.channels[channel]['users'].add(user)

        event = {
                'type': 'join',
                'user': user,
                'reply_to': channel,
                'channel': channel,
                'time': time.time()
                }

        self.manager.plugins.hook(self, event)

    def userLeft(self, user, channel):
        log.debug("%s left channel %s" % (user, channel))
        self.channels[channel]['users'].discard(user)

        # TODO: re-implement this so we can get the text
        event = {
                'type': 'part',
                'user': user,
                'reply_to': channel,
                'channel': channel,
                'text': "",
                'time': time.time()
                }

        self.manager.plugins.hook(self, event)

    def userKicked(self, user, channel, kicker, msg):
        log.debug("%s kicked from %s by %s: %s" % (user, channel, kicker, msg))
        self.channels[channel]['users'].discard(user)

        event = {
                'type': 'kick',
                'kicker': kicker,
                'kickee': user,
                'reply_to': channel,
                'channel': channel,
                'text': msg,
                'time': time.time()
                }

        self.manager.plugins.hook(self, event)

    def userQuit(self, user, msg):
        log.debug("%s quit: %s" % (user, msg))
        for chan in self.channels.itervalues():
            chan['users'].discard(user)

        event = {
                'type': 'quit',
                'user': user,
                'text': msg,
                'time': time.time()
                }

        self.manager.plugins.hook(self, event)

    def userRenamed(self, oldname, newname):
        log.debug("%s changed to %s" % (oldname, newname))
        for chan in self.channels.itervalues():
            if oldname in chan['users']:
                chan['users'].discard(oldname)
                chan['users'].add(newname)

        event = {
                'type': 'rename',
                'old': oldname,
                'new': newname,
                'time': time.time()
                }

        self.manager.plugins.hook(self, event)

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
        self.manager.plugins.hook(self, event)

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
                'internal': True,
                'type': 'msg',
                'sent_by': self.nickname,
                'sent_to': to,
                'reply_to': None,
                'text': msg,
                'time': time.time()
                }

        self.manager.plugins.hook(self, event)

    def notice(self, to, msg):
        irc.IRCClient.notice(self, to, msg)

        if msg and msg[0] == irc.X_DELIM:
            # Ignore any CTCP stuff
            ctcp = irc.ctcpExtract(msg)
            if not ctcp['normal']:
                return
            msg = " ".join(ctcp['normal'])

        event = {
                'internal': True,
                'type': 'notice',
                'sent_by': self.nickname,
                'sent_to': to,
                'reply_to': None,
                'text': msg,
                'time': time.time()
                }

        self.manager.plugins.hook(self, event)

    def me(self, to, msg):
        # Override the twisted behavior of only allowing channels for this
        self.ctcpMakeQuery(to, [('ACTION', msg)])

        event = {
                'internal': True,
                'type': 'me',
                'sent_by': self.nickname,
                'sent_to': to,
                'reply_to': None,
                'text': msg,
                'time': time.time()
                }

        self.manager.plugins.hook(self, event)

    def sendLine(self, line):
       log.rainman("SEND: %s" % (line,))
       irc.IRCClient.sendLine(self, line)

    def lineReceived(self, line):
       log.rainman("RECV: %s" % (line,))
       irc.IRCClient.lineReceived(self, line)


# So other bits can get access to the current connections
connections = {}

class HBotNetwork(protocol.ClientFactory):
    """Maintain a connection to an IRC network"""

    protocol = HBotConnection
    noisy = False

    def __init__(self, manager, config):
        self.config = config
        self.manager = manager
        self.reconnect = False
        self.id = config.get('id', None)
        self.nickname = config.get('nick', None)
        self.realname = config.get('name', self.nickname)
        self.username = self.nickname
        self.password = None
        self.acl = ACL(manager.config, config)

        servers = config.findall('server')
        if not servers:
            raise ConfigError("No servers defined for network '%s'" % self.id)
        else:
            for server in servers:
                if not server.get('hostname', None):
                    raise ConfigError("Server with no hostname in '%s'"
                            % self.id)
                if not server.get('port', "1").isdigit():
                    raise ConfigError("Server with invalid port '%s' in '%s'"
                            % (server.get('port', None), self.id))

        self._force_disconnect_timer = None
        self._connection = None
        self._server_curr = None
        self._server_iter = None
        self._delay = 1

        if self.id is None:
            self.logstr = "client"
        else:
            self.logstr = "client:%s" % self.id

    def connection(self):
        if self._connection:
            return self._connection
        else:
            raise NotConnected()

    def _server(self, next=False):
        # Rotate though the list of servers endlessly

        if not next and self._server_curr:
            return self._server_curr

        if not self._server_iter:
            self._server_iter = iter(self.config.findall('server'))

        try:
            self._server_curr = self._server_iter.next()
        except StopIteration:
            self._server_iter = iter(self.config.findall('server'))
            self._server_curr = self._server_iter.next()

        return self._server_curr

    def connect(self):
        """Connect to a server in this IRC network"""

        self.reconnect = True
        server = self._server(next=True)

        # Reset password as it is configured per-server
        self.password = server.get('password', None)

        use_ssl = server.get('ssl', 'false').lower()
        if use_ssl not in ('true', 'false'):
            raise ConfigError("<server ssl=? /> must be 'true' or 'false'")

        timeout = 30 # should this be configurable?

        if use_ssl == 'true':
            if not ssl:
                raise ConfigError("SSL support requires pyOpenSSL")
            context = ssl.ClientContextFactory()
            reactor.connectSSL(server.get('hostname'),
                    int(server.get('port', 6667)), self, context, timeout)
        else:
            reactor.connectTCP(server.get('hostname'),
                    int(server.get('port', 6667)), self, timeout)

    def disconnect(self, message):
        """Disconnect from an IRC network"""

        self.reconnect = False
        if self._connection:
            self._connection.quit(message)
            # Close the connection if the server doesn't within 15 seconds
            self._force_disconnect_timer = \
                    reactor.callLater(15, self._force_disconnect)

    def _force_disconnect(self):
        if self._connection:
            log.warn("Killing connection...")
            self._force_disconnect_timer = None
            self._connection.transport.loseConnection()

    def _reconnect(self):
        if self._force_disconnect_timer:
            self._force_disconnect_timer.cancel()
            self._force_disconnect_timer = None
        if not self.reconnect:
            self.manager.networkLost(self.id)
            return

        # Failure! Try again...
        reactor.callLater(self._delay, self.connect)

        if self._delay < 128:
            self._delay *= 2

    def startedConnecting(self, connector):
        addr = connector.getDestination()
        log.info("Connecting to %s:%s..." % (addr.host, addr.port),
                prefix=self.logstr)

    def clientConnected(self, connection):
        # Called from HBotConnection once connection is OK
        self._delay = 1
        self._connection = connection

    def clientConnectionLost(self, connector, reason):
        addr = connector.getDestination()
        if isinstance(reason.value, error.ConnectionDone):
            log.info("Connection to %s:%s closed" % (addr.host, addr.port))
        else:
            log.warn("Connection to %s:%s lost: %s" %
                    (addr.host, addr.port, reason.value), prefix=self.logstr)
        self._connection = None
        self._reconnect()

    def clientConnectionFailed(self, connector, reason):
        addr = connector.getDestination()
        log.warn("Connecting to %s:%s failed: %s" %
                (addr.host, addr.port, reason.value), prefix=self.logstr)
        self._connection = None
        self._reconnect()

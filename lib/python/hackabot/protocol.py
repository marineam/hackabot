"""The basic line protocol"""

from zope.interface import implements
from twisted.internet import reactor, error
from twisted.internet.interfaces import IHalfCloseableProtocol
from twisted.internet.protocol import ProcessProtocol
from twisted.protocols.basic import LineOnlyReceiver

from hackabot import core, log

class CommandError(Exception):
    pass

class HBLineProtocol(LineOnlyReceiver):
    """Simple line based protocol for interacting with subprocesses
    and external commands/scripts/whatever.
    """

    implements(IHalfCloseableProtocol)

    delimiter = '\n'

    def __init__(self):
        self._to = None
        self._net = core.manager.default()

    def connectionMade(self):
        log.debug("New connection.")

    def connectionLost(self, reason):
        log.debug("Lost connection.")

    def readConnectionLost(self):
        log.debug("Lost read connection.")
        reactor.callLater(0,self.transport.loseConnection)

    def lineReceived(self, line):
        line = line.strip()
        command, space, args = line.partition(" ")

        if hasattr(self, "handle_%s" % command):
            try:
                getattr(self, "handle_%s" % command)(args.strip())
            except CommandError, ex:
                self.sendLine("error %s" % ex)
        else:
            self.sendLine("error unknown command '%s'" % command)

    def to(self):
        if self._to:
            return self._to
        else:
            raise CommandError("to has not been set")

    def conn(self):
        if self._net:
            try:
                return self._net.connection()
            except core.NotConnected:
                raise CommandError("net %s is not connected", self._net.id)
        else:
            raise CommandError("net has not been set")

    def handle_to(self, args):
        """Set a nick or channel to send messages to. For events the
        default to the current channel for public messages or the
        sending user for private messages. If this is not an event
        there is no default and must be set explicitly.
        If the argument is omitted the current target is returned.
        
        to [<nick or channel>]
        """

        if not args:
            self.sendLine("ok %s" % self.to())
        elif " " in args or "\t" in args:
            raise CommandError("to may not contain whitespace")
        else:
            self._to = args
            self.sendLine("ok")

    def handle_net(self, args):
        """Set the network to send messages to. For events the default
        is the current network, otherwise the first network listed in
        the config will be the default.
        If the argument is omitted the current network is returned.
        
        net [<network id>]
        """

        if not args:
            id = self.conn().factory.id
            if id is None:
                self.sendLine("ok only one network")
            else:
                self.sendLine("ok %s" % id)
        elif args not in core.manager:
            raise CommandError("invalid network id '%s'" % args)
        else:
            self._net = core.manager[args]
            self.sendLine("ok")

    def handle_msg(self, args):
        """Send a message using the current 'to' and 'net'.
        Note that all beginning and ending whitespace is ignored.
        If you need to send ascii art use the 'dump' command.

        msg <some message>
        """

        self.conn().msg(self.to(), args)
        self.sendLine("ok")

    def handle_send(self, args):
        """Alias for 'msg'"""

        self.handle_msg(args)

    def handle_notice(self, args):
        """Send a notice using the current 'to' and 'net'.
        Note that all beginning and ending whitespace is ignored.

        notice <some message>
        """

        self.conn().notice(self.to(), args)
        self.sendLine("ok")

    def handle_me(self, args):
        """Send a /me message using the current 'to' and 'net'.
        Note that all beginning and ending whitespace is ignored.

        me <some message>
        """

        self.conn().me(self.to(), args)
        self.sendLine("ok")

    def handle_action(self, args):
        """Alias for 'me'"""

        self.handle_me(args)

    def handle_nick(self, args):
        """Change or get the bots nick. If no argument is given the
        current one is returned.

        nick [<new nick>]
        """

        if not args:
            self.sendLine("ok %s" % self.conn().nickname)
        elif " " in args or "\t" in args:
            raise CommandError("invalid nick '%s'" % args)
        else:
            self.conn().setNick(args)
            self.sendLine("ok")

    def handle_join(self, args):
        """Join a given channel.

        join <channel>
        """

        if not args:
            raise CommandError("no channel given")
        elif " " in args or "\t" in args:
            raise CommandError("invalid channel '%s'" % args)
        else:
            self.conn().join(args)
            self.sendLine("ok")

    def handle_part(self, args):
        """Leave a given channel.

        part <channel> [<some reason>]
        """

        channel, nill, reason = args.partition(" ")

        if channel not in self.conn().channels:
            raise CommandError("not in channel '%s'" % args)
        else:
            reason = reason.strip()
            self.conn().part(channel, reason)
            self.sendLine("ok")

    def handle_quit(self, args):
        """Quit!
        
        quit [<some reason>]"""

        # FIXME: handle this gracefully
        reactor.stop()

class HBProcessProtocol(ProcessProtocol, HBLineProtocol):
    """ProcessProtocol adapter for HBLineProtocol"""

    def __init__(self, conn, event):
        self._net = conn.factory
        self._pid = ""

        if 'reply_to' in event:
            self._to = event['reply_to']
        else:
            self._to = None

        if 'text' in event and event['text']:
            self._text = event['text']
            if self._text[-1] != '\n':
                self._text += '\n'
        else:
            self._text = ""

    def connectionMade(self):
        log.debug("Process started", prefix=self._pid)
        self._pid = str(self.transport.pid)

        # workaround to make the LineProtocol happy
        self.transport.disconnecting = 0

        self.transport.write(self._text)
        self.transport.closeStdin()

    def outReceived(self, data):
        log.trace(data.strip(), prefix=self._pid)
        self.dataReceived(data)

    def errReceived(self, data):
        log.warn(data.strip(), prefix=self._pid)

    def sendLine(self, line):
        if line.startswith("error"):
            log.warn(line, prefix=self._pid)
        else:
            log.trace(line, prefix=self._pid)

    def outConnectionLost(self):
        if self._buffer:
            self.lineReceived("%s\n" % self._buffer)

    def processEnded(self, reason):
        if not isinstance(reason.value, error.ProcessDone):
            log.warn(reason, prefix=self._pid)
        else:
            log.debug("Process ended", prefix=self._pid)

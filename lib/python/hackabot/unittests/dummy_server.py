"""Various dummy servers for use in unit tests."""

from email.parser import FeedParser
from zope.interface import implements
from twisted.internet import defer, error, protocol, reactor, defer
from twisted.python import failure, log
from twisted.words.protocols import irc
from twisted.words import service
from twisted.cred import checkers, credentials, portal
from twisted.mail import smtp

class TesterClient(irc.IRCClient):
    """A simple IRC client for interacting with the bot"""

    nickname = "tester"
    channel = "#hackabot"

    def __init__(self, log=None, channel=None):
        if channel:
            self.channel = channel
        self._log = log
        self._notify = None
        self._ready = defer.Deferred()
        self._done = defer.Deferred()

    def signedOn(self):
        self.join(self.channel)

    def joined(self, channel):
        assert self._ready and channel == self.channel
        log.msg("[%s] joined %s" % (self.nickname, channel))
        d = self._ready
        self._ready = None
        d.callback(None)

    def connectionLost(self, reason=protocol.connectionDone):
        if isinstance(reason.value, error.ConnectionDone):
            reason = None
        d = self._done
        self._done = None
        d.callback(reason)

    def _logit(self, name, user, message):
        if user:
            user = user.split('!',1)[0]
        log.msg("[%s] %s from %s: %s" % (self.nickname, name, user, message))
        if self._log is not None:
            self._log.append((name, user, message))
        if self._notify and (
                self._notify[1] in (None, name) and
                self._notify[2] in (None, user) and
                self._notify[3] in (None, message)):
            notify = self._notify[0]
            self._notify = None
            notify.callback(None)

    def privmsg(self, user, channel, message):
        self._logit('privmsg', user, message)

    def action(self, user, channel, message):
        self._logit('action', user, message)

    def userJoined(self, user, channel):
        self._logit('join', user, None)

    def userLeft(self, user, channel):
        self._logit('part', user, None)

    def userQuit(self, user, message):
        self._logit('quit', user, message)

    def userRenamed(self, old, new):
        self._logit('nick', old, new)

    def notice(self, to, msg):
        # This blows, but I don't want to deal with implementing it.
        raise Exception("Twisted's IRC server doesn't support NOTICE")

    def ready(self):
        return self._ready

    def notify(self, name=None, user=None, message=None):
        assert self._notify is None
        self._notify = (defer.Deferred(), name, user, message)
        return self._notify[0]

    def done(self):
        return self._done

class PassThroughFactory(protocol.ClientFactory):

    def __init__(self, proto):
        self.protocol = proto

    def buildProtocol(self, addr):
        return self.protocol

class SimpleChecker(object):

    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (credentials.IUsernamePassword,)

    def requestAvatarId(self, credentials):
        return credentials.username

class SimpleIRCUser(service.IRCUser):

    password = ""
    name = None

    def handleCommand(self, command, prefix, params):
        line = ' '.join([command] + list(params))
        if prefix:
            line = ":%s %s" % (prefix, line)
        log.msg("[%s] RECV %s" % (self.name, line))
        service.IRCUser.handleCommand(self, command, prefix, params)

    def sendLine(self, line):
        log.msg("[%s] SEND %s" % (self.name, line))
        service.IRCUser.sendLine(self, line)

class SimpleIRCFactory(service.IRCFactory):

    protocol = SimpleIRCUser

    def __init__(self):
        realm = service.InMemoryWordsRealm("TEST")
        realm.createGroupOnRequest = True
        realm.createUserOnRequest = True
        port = portal.Portal(realm, [SimpleChecker()])
        service.IRCFactory.__init__(self, realm, port)

class Tester(object):

    def __init__(self, channel='#hackabot'):
        # Setup server
        self._server = reactor.listenTCP(0, SimpleIRCFactory())
        self.port = self._server.getHost().port

        # Setup client
        self.log = []
        self.client = TesterClient(self.log, channel)
        reactor.connectTCP("127.0.0.1", self.port,
                PassThroughFactory(self.client))

    def loseConnection(self):
        self.client.quit()
        return defer.DeferredList([
            self.client.done(),
            self._server.loseConnection()])

    def ready(self):
        return self.client.ready()

    def notify(self, *args, **kwargs):
        return self.client.notify(*args, **kwargs)

class SMTPMessageParser(FeedParser):
    """Parse the email message and store the resulting MIME
    document in the original SMTP factory object."""

    implements(smtp.IMessage)

    def __init__(self, factory):
        self.factory = factory
        FeedParser.__init__(self)

    def lineReceived(self, line):
        self.feed("%s\n" % line)

    def eomReceived(self):
        self.factory.callback(self.close())
        return defer.succeed(None)

    def connectionLost(self):
        self.factory.callback(failure.Failure(error.ConnectionLost()))

class SMTPMessageDelivery(object):
    """Accept all messages"""

    implements(smtp.IMessageDelivery)

    def __init__(self, factory):
        self.factory = factory

    def receivedHeader(self, helo, origin, recipients):
        return "Received: Dummy SMTP Server"

    def validateFrom(self, helo, origin):
        return origin

    def validateTo(self, user):
        return lambda: SMTPMessageParser(self.factory)

class SMTP(smtp.SMTPFactory):

    def __init__(self):
        self.message = defer.Deferred()
        self.delivery = SMTPMessageDelivery(self)

    def buildProtocol(self, addr):
        p = smtp.SMTPFactory.buildProtocol(self, addr)
        p.delivery = self.delivery
        return p

    def callback(self, result):
        self.message.callback(result)

from twisted.internet import protocol, reactor
from hackabot.unittests import dummy_server, IRCTestCase

class DummyClient(dummy_server.TesterClient):
    nickname = "dummy"

class DummyTestCase(IRCTestCase):
    """Sanity check the tester infrastructure"""

    def testLog(self):
        dummy = DummyClient()
        c = reactor.connectTCP("127.0.0.1", self.tester.port,
                dummy_server.PassThroughFactory(dummy))

        expect = [('join', 'dummy', None),
                  ('privmsg', 'dummy', 'test'),
                  ('part', 'dummy', None)]

        def ready(_):
            dummy.msg(dummy.channel, "test")
            dummy.quit()
            d = dummy.done()
            d.addCallback(check)
            return d

        def check(_):
            if len(self.tester.log) >= len(expect):
                self.assertEquals(self.tester.log, expect)
            else:
                d = self.tester.notify()
                d.addCallback(check)
                return d

        d = dummy.ready()
        d.addCallback(ready)
        return d

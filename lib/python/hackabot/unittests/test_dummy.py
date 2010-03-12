from twisted.internet import protocol, reactor
from hackabot.unittests import dummy_server, IRCTestCase, HBTestCase

class DummyClient(dummy_server.TesterClient):
    nickname = "dummy"

class DummyTestCase(IRCTestCase):
    """Sanity check the tester infrastructure"""

    def test_log(self):
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

    def test_commands(self):
        log = []
        dummy = DummyClient(log)
        c = reactor.connectTCP("127.0.0.1", self.tester.port,
                dummy_server.PassThroughFactory(dummy))

        expect = [('privmsg', 'tester', 'aaaa'),
                  ('action', 'tester', 'bbbb')]

        def ready(_):
            d = dummy.notify('action')
            d.addCallback(check)
            self.send("aaaa")
            self.action("bbbb")
            return d

        def check(_):
            self.assertEquals(log, expect)
            dummy.quit()
            return dummy.done()

        d = dummy.ready()
        d.addCallback(ready)
        return d

class TrivialTestCase(HBTestCase):

    def test_expect(self):
        return self.expect([])

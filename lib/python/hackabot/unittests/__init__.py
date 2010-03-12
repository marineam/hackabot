"""Base Hackabot TestCase"""

from twisted.internet import defer
from twisted.trial import unittest

from hackabot import core, parse_config
from hackabot.etree import ElementTree
from hackabot.unittests import dummy_server

class IRCTestCase(unittest.TestCase):

    channel = "#hackabot"

    def setUp(self):
        self.tester = dummy_server.Tester(self.channel)
        return self.tester.ready()

    def send(self, msg, to=channel):
        self.tester.client.msg(to, msg)

    def action(self, msg, to=channel):
        self.tester.client.me(to, msg)

    def tearDown(self):
        return self.tester.loseConnection()

class HBTestCase(IRCTestCase):

    nickname = "hackabot"
    username = "Hackabot Test"
    channel = "#hackabot"

    def buildConfig(self):
        cfg = ElementTree.Element("hackabot")
        net = ElementTree.SubElement(cfg, "network")
        net.attrib['nick'] = self.nickname
        net.attrib['name'] = self.username
        svr = ElementTree.SubElement(net, "server")
        svr.attrib['hostname'] = "127.0.0.1"
        svr.attrib['port'] = str(self.tester.port)
        join = ElementTree.SubElement(net, "autojoin")
        join.attrib['chan'] = self.channel
        return cfg

    def setUp(self):
        self._hb_exit = defer.Deferred()

        def stop():
            assert self._hb_exit
            self._hb_exit.callback(None)

        def start(_):
            config = ElementTree.tostring(self.buildConfig())
            self.manager = core.HBotManager(xml=config, exit_cb=stop)
            return self.tester.notify('join', self.nickname)

        d = super(HBTestCase, self).setUp()
        d.addCallback(start)
        return d

    def expect(self, log):
        log = [('join', self.nickname, None)] + list(log)
        if len(self.tester.log) >= len(log):
            self.assertEquals(self.tester.log, log)
        else:
            d = self.tester.notify()
            d.addCallback(lambda _: self.expect(log))
            return d

    def tearDown(self):
        self.manager.disconnect()
        self._hb_exit.addCallback(lambda _: super(HBTestCase, self).tearDown())
        return self._hb_exit
